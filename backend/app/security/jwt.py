"""
JWT creation and verification.

Three distinct token *types* are issued, distinguished by a "type"
claim so a token minted for one purpose can never be replayed as
another (e.g. an email-verification token can't be used as an access
token):

  - access              short-lived, sent as Authorization: Bearer <token>
  - refresh             longer-lived, persisted (hashed) and rotated on use
  - email_verification  single purpose, short-lived
  - password_reset      single purpose, short-lived
"""
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import TokenError, TokenExpiredError


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: uuid.UUID | str, role: str) -> str:
    return _create_token(
        subject=str(user_id),
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"role": role},
    )


def create_refresh_token(user_id: uuid.UUID | str) -> str:
    return _create_token(
        subject=str(user_id),
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_email_verification_token(user_id: uuid.UUID | str) -> str:
    return _create_token(
        subject=str(user_id),
        token_type=TokenType.EMAIL_VERIFICATION,
        expires_delta=timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS),
    )


def create_password_reset_token(user_id: uuid.UUID | str) -> str:
    return _create_token(
        subject=str(user_id),
        token_type=TokenType.PASSWORD_RESET,
        expires_delta=timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    """Decode + validate a JWT, enforcing the expected `type` claim.

    Raises TokenExpiredError / TokenError (both AuthenticationError
    subclasses) on any failure — callers don't need to know about jose's
    exception types.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except JWTError as exc:
        raise TokenError("Could not validate token") from exc

    if payload.get("type") != expected_type.value:
        raise TokenError(f"Expected a {expected_type.value} token")

    return payload
