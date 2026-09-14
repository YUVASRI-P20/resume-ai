"""
Shared FastAPI dependencies: DB session re-export, bearer-token
extraction, and "current user" resolution used by every protected route.
"""
import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, InactiveUserError, NotFoundError
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.jwt import TokenType, decode_token

# tokenUrl is documentation-only here (we don't use OAuth2 password flow
# form login) — it just tells Swagger UI where the login endpoint lives.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token, TokenType.ACCESS)
    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    users = UserRepository(db)
    user = await users.get_by_id_with_role(uuid.UUID(user_id))
    if user is None:
        raise NotFoundError("User not found")

    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise InactiveUserError()
    return user
