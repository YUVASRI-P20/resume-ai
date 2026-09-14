"""User-facing Pydantic schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.role import RoleName


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: RoleName
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("role", mode="before")
    @classmethod
    def _extract_role_name(cls, v):
        # `User.role` is a related Role ORM object (has `.name`); accept
        # that, a plain string, or an already-built RoleName.
        if hasattr(v, "name"):
            return v.name
        return v


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
