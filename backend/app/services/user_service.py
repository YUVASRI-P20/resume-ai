"""User profile business logic (self-service, not admin/recruiter tooling)."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.users.get_by_id_with_role(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def update_profile(self, user: User, payload: UserUpdate) -> User:
        if payload.full_name is not None:
            user.full_name = payload.full_name
        await self.session.commit()
        await self.users.refresh(user)
        return user
