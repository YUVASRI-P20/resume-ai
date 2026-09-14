"""
Role-based access control helpers.

Usage in a route:

    @router.get("/recruiter-only")
    async def handler(user: User = Depends(require_roles(RoleName.RECRUITER, RoleName.ADMIN))):
        ...
"""
from typing import Callable

from fastapi import Depends

from app.api.deps import get_current_active_user
from app.core.exceptions import AuthorizationError
from app.models.role import RoleName
from app.models.user import User


def require_roles(*allowed_roles: RoleName) -> Callable:
    async def dependency(user: User = Depends(get_current_active_user)) -> User:
        if RoleName(user.role.name) not in allowed_roles:
            raise AuthorizationError(
                f"This action requires one of the following roles: "
                f"{', '.join(r.value for r in allowed_roles)}"
            )
        return user

    return dependency
