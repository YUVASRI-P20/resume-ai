"""
Authentication service — owns every business rule for registration,
login, token refresh/rotation, logout, email verification, and password
reset. Routers stay thin and only translate HTTP <-> service calls.
"""
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    NotFoundError,
    TokenError,
)
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse, RegisterRequest, TokenPair
from app.schemas.user import UserRead
from app.security.jwt import (
    TokenType,
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
)
from app.security.password import hash_password, verify_password
from app.services.email_service import email_service


def _hash_token(raw_token: str) -> str:
    """SHA-256 the raw JWT before persisting — the DB never holds a usable token."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.roles = RoleRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    # ---------------------------------------------------------------- #
    # Registration
    # ---------------------------------------------------------------- #
    async def register(
        self, payload: RegisterRequest, user_agent: str | None, ip_address: str | None
    ) -> AuthResponse:
        if await self.users.email_exists(payload.email):
            raise AlreadyExistsError("An account with this email already exists")

        role = await self.roles.get_by_name(payload.role)
        if role is None:
            # Roles are seeded at migration time; missing here means the
            # seed hasn't run rather than bad user input.
            raise NotFoundError(f"Role '{payload.role}' is not configured")

        user = await self.users.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            role_id=role.id,
            is_active=True,
            is_email_verified=False,
        )
        await self.session.commit()
        await self.users.refresh(user)
        user = await self.users.get_by_id_with_role(user.id)

        verification_token = create_email_verification_token(user.id)
        email_service.send_verification_email(user.email, verification_token)

        tokens = await self._issue_token_pair(user, user_agent, ip_address)
        await self.session.commit()
        return AuthResponse(user=UserRead.model_validate(user), tokens=tokens)

    # ---------------------------------------------------------------- #
    # Login
    # ---------------------------------------------------------------- #
    async def login(
        self, email: str, password: str, user_agent: str | None, ip_address: str | None
    ) -> AuthResponse:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        # Real login streak: records the event and advances the streak
        # (first-ever login => Day 1). Runs in a savepoint so a failure can
        # never block or corrupt the login transaction.
        try:
            from app.services.streak_service import record_login

            async with self.session.begin_nested():
                await record_login(self.session, user.id, ip_address=ip_address, user_agent=user_agent)
        except Exception:  # noqa: BLE001
            from app.core.logging import get_logger

            get_logger(__name__).warning("Streak recording failed for user %s", user.id)

        tokens = await self._issue_token_pair(user, user_agent, ip_address)
        await self.session.commit()
        return AuthResponse(user=UserRead.model_validate(user), tokens=tokens)

    # ---------------------------------------------------------------- #
    # Token refresh (with rotation)
    # ---------------------------------------------------------------- #
    async def refresh(
        self, raw_refresh_token: str, user_agent: str | None, ip_address: str | None
    ) -> TokenPair:
        payload = decode_token(raw_refresh_token, TokenType.REFRESH)
        token_hash = _hash_token(raw_refresh_token)

        stored = await self.refresh_tokens.get_by_hash(token_hash)
        if stored is None:
            raise TokenError("Refresh token not recognized")

        now = datetime.now(timezone.utc)
        if stored.revoked:
            # Reuse of a rotated-out token is a strong signal of theft —
            # burn every token for this user as a precaution.
            await self.refresh_tokens.revoke_all_for_user(stored.user_id)
            await self.session.commit()
            raise TokenError("Refresh token has already been used and was revoked")

        if stored.expires_at.replace(tzinfo=timezone.utc) < now:
            raise TokenError("Refresh token has expired")

        user = await self.users.get_by_id_with_role(uuid.UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise InactiveUserError()

        # Rotate: issue a new pair, mark the old one as replaced.
        new_access = create_access_token(user.id, user.role.name)
        new_refresh = create_refresh_token(user.id)
        new_hash = _hash_token(new_refresh)

        await self.refresh_tokens.revoke(stored, replaced_by_hash=new_hash)
        await self.refresh_tokens.create(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self.session.commit()

        return TokenPair(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    # ---------------------------------------------------------------- #
    # Logout
    # ---------------------------------------------------------------- #
    async def logout(self, raw_refresh_token: str) -> None:
        token_hash = _hash_token(raw_refresh_token)
        stored = await self.refresh_tokens.get_by_hash(token_hash)
        if stored is not None and not stored.revoked:
            await self.refresh_tokens.revoke(stored)
            await self.session.commit()
        # Logging out with an already-invalid/unknown token is a no-op,
        # not an error — the end state the caller wants is already true.

    # ---------------------------------------------------------------- #
    # Email verification
    # ---------------------------------------------------------------- #
    async def verify_email(self, raw_token: str) -> None:
        payload = decode_token(raw_token, TokenType.EMAIL_VERIFICATION)
        user = await self.users.get_by_id(uuid.UUID(payload["sub"]))
        if user is None:
            raise NotFoundError("User not found")
        user.is_email_verified = True
        await self.session.commit()

    async def resend_verification_email(self, email: str) -> None:
        user = await self.users.get_by_email(email)
        if user is None:
            # Don't leak whether an email is registered.
            return
        if user.is_email_verified:
            return
        token = create_email_verification_token(user.id)
        email_service.send_verification_email(user.email, token)

    # ---------------------------------------------------------------- #
    # Password reset
    # ---------------------------------------------------------------- #
    async def forgot_password(self, email: str) -> None:
        user = await self.users.get_by_email(email)
        if user is None:
            # Same response either way — prevents user enumeration.
            return
        token = create_password_reset_token(user.id)
        email_service.send_password_reset_email(user.email, token)

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        payload = decode_token(raw_token, TokenType.PASSWORD_RESET)
        user = await self.users.get_by_id(uuid.UUID(payload["sub"]))
        if user is None:
            raise NotFoundError("User not found")

        user.hashed_password = hash_password(new_password)
        await self.session.flush()
        # Any password reset invalidates every existing session.
        await self.refresh_tokens.revoke_all_for_user(user.id)
        await self.session.commit()

    # ---------------------------------------------------------------- #
    # Internal helpers
    # ---------------------------------------------------------------- #
    async def _issue_token_pair(
        self, user: User, user_agent: str | None, ip_address: str | None
    ) -> TokenPair:
        access = create_access_token(user.id, user.role.name)
        refresh = create_refresh_token(user.id)

        await self.refresh_tokens.create(
            user_id=user.id,
            token_hash=_hash_token(refresh),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=user_agent,
            ip_address=ip_address,
        )

        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
