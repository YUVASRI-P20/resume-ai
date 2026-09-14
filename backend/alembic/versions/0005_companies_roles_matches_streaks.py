"""companies, job roles, evidence-based role matching, login streaks + seed data

Revision ID: 0005
Revises: 0004
"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def uuid_col():
    return postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("industry", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_companies_name", "companies", ["name"], unique=True)

    op.create_table(
        "job_roles",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("company_id", uuid_col(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("domain", sa.String(150)),
        sa.Column("seniority", sa.String(50)),
        sa.Column("job_description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("company_id", "title", name="uq_company_role_title"),
    )
    op.create_index("ix_job_roles_company_id", "job_roles", ["company_id"])

    op.create_table(
        "role_requirements",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("job_role_id", uuid_col(), sa.ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requirement", sa.String(150), nullable=False),
        sa.Column(
            "category",
            sa.Enum("skill", "technology", "concept", "experience", name="requirementcategory"),
            nullable=False,
        ),
        sa.Column("importance", sa.Integer(), nullable=False),
    )
    op.create_index("ix_role_requirements_job_role_id", "role_requirements", ["job_role_id"])

    op.create_table(
        "role_match_results",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", uuid_col(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_role_id", uuid_col(), sa.ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("match_percentage", sa.Float(), nullable=False),
        sa.Column("strong_areas", sa.JSON()),
        sa.Column("weak_areas", sa.JSON()),
        sa.Column("requirements_matched", sa.JSON()),
        sa.Column("requirements_missing", sa.JSON()),
        sa.Column("evidence", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_role_match_results_resume_id", "role_match_results", ["resume_id"])
    op.create_index("ix_role_match_results_user_id", "role_match_results", ["user_id"])

    op.create_table(
        "login_events",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("login_date", sa.Date(), nullable=False),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_login_events_user_id", "login_events", ["user_id"])

    op.create_table(
        "user_streaks",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("streak_days", sa.Integer(), nullable=False),
        sa.Column("longest_streak_days", sa.Integer(), nullable=False),
        sa.Column("last_activity_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", name="uq_user_streaks_user_id"),
    )

    # ---- Seed companies / roles / requirements (shared seed module) ----
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.services.seed_data import build_seed_rows

    bind = op.get_bind()

    for c in build_seed_rows():
        cid = uuid.uuid4()
        bind.execute(
            sa.text(
                "INSERT INTO companies (id, name, description, industry, is_active) "
                "VALUES (:id, :name, :description, :industry, 1)"
            ),
            {
                "id": str(cid), "name": c["company"],
                "description": c["description"], "industry": c["industry"],
            },
        )
        for r in c["roles"]:
            rid = uuid.uuid4()
            jd = (
                f"{r['title']} at {c['company']} — {r['description']} "
                f"Key requirements: {', '.join(req for req, _cat, _imp in r['requirements'])}."
            )
            bind.execute(
                sa.text(
                    "INSERT INTO job_roles (id, company_id, title, description, domain, seniority, job_description, is_active) "
                    "VALUES (:id, :company_id, :title, :description, :domain, :seniority, :jd, 1)"
                ),
                {
                    "id": str(rid), "company_id": str(cid), "title": r["title"],
                    "description": r["description"], "domain": r["domain"],
                    "seniority": r["seniority"], "jd": jd,
                },
            )
            for req, cat, imp in r["requirements"]:
                bind.execute(
                    sa.text(
                        "INSERT INTO role_requirements (id, job_role_id, requirement, category, importance) "
                        "VALUES (:id, :job_role_id, :requirement, :category, :importance)"
                    ),
                    {"id": str(uuid.uuid4()), "job_role_id": str(rid), "requirement": req, "category": cat, "importance": imp},
                )


def downgrade() -> None:
    op.drop_table("user_streaks")
    op.drop_table("login_events")
    op.drop_table("role_match_results")
    op.drop_table("role_requirements")
    op.drop_table("job_roles")
    op.drop_table("companies")
    for name in ["requirementcategory"]:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
