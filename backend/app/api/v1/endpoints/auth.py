"""Authentication endpoints: register, login, logout, refresh, password
reset, and email verification."""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPair,
    VerifyEmailRequest,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.utils.rate_limiter import limiter
from app.core.config import settings

router = APIRouter()


def _client_meta(request: Request) -> tuple[str | None, str | None]:
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    return user_agent, ip_address


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new STUDENT or RECRUITER account",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
    request: Request,
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    user_agent, ip_address = _client_meta(request)
    service = AuthService(db)
    return await service.register(payload, user_agent, ip_address)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in with email and password",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user_agent, ip_address = _client_meta(request)
    service = AuthService(db)
    return await service.login(payload.email, payload.password, user_agent, ip_address)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Revoke a refresh token (log out the current session)",
)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Exchange a refresh token for a new access/refresh pair (rotates the refresh token)",
)
async def refresh(
    request: Request,
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    user_agent, ip_address = _client_meta(request)
    service = AuthService(db)
    return await service.refresh(payload.refresh_token, user_agent, ip_address)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset email",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.forgot_password(payload.email)
    # Always the same response, whether or not the email exists.
    return MessageResponse(message="If that email is registered, a reset link has been sent")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password using a token from the forgot-password email",
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.reset_password(payload.token, payload.new_password)
    return MessageResponse(message="Password has been reset successfully")


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email using a token from the verification email",
)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.verify_email(payload.token)
    return MessageResponse(message="Email verified successfully")


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the currently authenticated user",
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user
