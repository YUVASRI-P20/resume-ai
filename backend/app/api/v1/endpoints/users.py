"""User profile endpoints + a role-gated example route for future modules
to copy the pattern from."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database.session import get_db
from app.models.role import RoleName
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.security.permissions import require_roles
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead, summary="Get my profile")
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=UserRead, summary="Update my profile")
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update_profile(current_user, payload)


@router.get(
    "/admin/ping",
    response_model=dict,
    summary="Example ADMIN-only route (reference implementation for future modules)",
)
async def admin_ping(user: User = Depends(require_roles(RoleName.ADMIN))):
    return {"message": f"Hello, admin {user.email}"}
