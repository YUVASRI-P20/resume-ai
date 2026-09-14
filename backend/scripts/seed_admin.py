"""
One-off script to create the first ADMIN user (ADMIN accounts are never
created through the public /register endpoint).

Usage:
    python -m scripts.seed_admin admin@interviewiq.ai "S3curePass1" "Platform Admin"
"""
import asyncio
import sys

from app.database.session import AsyncSessionLocal
from app.models.role import RoleName
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password


async def main(email: str, password: str, full_name: str) -> None:
    async with AsyncSessionLocal() as session:
        users = UserRepository(session)
        roles = RoleRepository(session)

        if await users.email_exists(email):
            print(f"A user with email {email} already exists — aborting.")
            return

        admin_role = await roles.get_by_name(RoleName.ADMIN.value)
        if admin_role is None:
            print("ADMIN role not found — run `alembic upgrade head` first.")
            return

        await users.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role_id=admin_role.id,
            is_active=True,
            is_email_verified=True,
        )
        await session.commit()
        print(f"Admin user created: {email}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))
