"""
Local-development bootstrap.

For zero-setup runs (sqlite, no alembic, no Postgres) this creates all
tables from the ORM metadata and seeds:
  - the three auth roles (normally seeded by migration 0001), and
  - the companies / job roles / requirements (normally seeded by 0005).

On Postgres deployments the alembic migrations own schema + seeds; this
module detects an existing database and does nothing.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select, text

from app.core.logging import get_logger
from app.database.session import engine
from app.models.role import Role, RoleName

logger = get_logger(__name__)

ROLE_DESCRIPTIONS = {
    RoleName.STUDENT: "Candidate preparing for technical interviews",
    RoleName.RECRUITER: "Recruiter account",
    RoleName.ADMIN: "Platform administrator",
}


async def bootstrap_dev_database() -> None:
    """Create tables + seed base rows if the DB is empty (idempotent)."""
    from app.database.base import Base
    import app.models  # noqa: F401 — registers every model on Base.metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Seed roles if missing
        for role_name in RoleName:
            await conn.execute(
                text(
                    "INSERT INTO roles (id, name, description, created_at, updated_at) "
                    "SELECT :id, :name, :description, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP "
                    "WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = :name)"
                ),
                {"id": str(uuid.uuid4()), "name": role_name.value, "description": ROLE_DESCRIPTIONS[role_name]},
            )

    # Seed companies/roles/requirements if missing (uses the sync engine).
    await _seed_companies_if_empty()


async def _seed_companies_if_empty() -> None:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    from app.models.company import Company, JobRole, RequirementCategory, RoleRequirement
    from app.services.seed_data import build_seed_rows

    factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        exists = (await session.execute(select(Company).limit(1))).scalar_one_or_none()
        if exists is not None:
            return

        for c in build_seed_rows():
            company = Company(name=c["company"], description=c.get("description"), industry=c.get("industry"))
            session.add(company)
            await session.flush()
            for r in c["roles"]:
                role = JobRole(
                    company_id=company.id,
                    title=r["title"],
                    description=r.get("description"),
                    domain=r.get("domain"),
                    seniority=r.get("seniority"),
                    job_description=(
                        f"{r['title']} at {c['company']} — {r['description']} "
                        f"Key requirements: {', '.join(req for req, _cat, _imp in r['requirements'])}."
                    ),
                )
                session.add(role)
                await session.flush()
                for req, cat, imp in r["requirements"]:
                    session.add(
                        RoleRequirement(
                            job_role_id=role.id,
                            requirement=req,
                            category=RequirementCategory(cat),
                            importance=imp,
                        )
                    )
        await session.commit()
        logger.info("Seeded companies/job roles for local development.")
