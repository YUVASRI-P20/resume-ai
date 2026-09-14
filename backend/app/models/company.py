"""
Companies, job roles, and evidence-based resume<->role matching.

- Company / JobRole / RoleRequirement: the job data source the UI selects
  from (seeded from migration 0005; extendable without code changes).
- RoleMatchResult: one evidence-based match run of a resume against a role.
  Each requirement stores the resume evidence, match status and confidence
  so the UI can explain WHY a skill is strong/weak instead of just a %.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    roles: Mapped[list["JobRole"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class JobRole(Base):
    __tablename__ = "job_roles"
    __table_args__ = (UniqueConstraint("company_id", "title", name="uq_company_role_title"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(String(150), nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Free-form JD text used for AI prompts (stored verbatim from the source).
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company: Mapped["Company"] = relationship(back_populates="roles")
    requirements: Mapped[list["RoleRequirement"]] = relationship(
        back_populates="job_role", cascade="all, delete-orphan"
    )


class RequirementCategory(str, enum.Enum):
    SKILL = "skill"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"
    TOOL = "tool"
    EXPERIENCE = "experience"


class MatchStatus(str, enum.Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    MISSING = "missing"


class RoleRequirement(Base):
    """A single requirement of a job role (e.g. 'Python', 'Docker', 'System Design')."""

    __tablename__ = "role_requirements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    requirement: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[RequirementCategory] = mapped_column(
        Enum(RequirementCategory), default=RequirementCategory.SKILL, nullable=False
    )
    # Relative importance weight used by the match score (1 = nice to have, 5 = must have).
    importance: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    job_role: Mapped["JobRole"] = relationship(back_populates="requirements")


class RoleMatchResult(Base):
    """One evidence-based match run: a resume vs a company job role."""

    __tablename__ = "role_match_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    job_role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False
    )

    match_percentage: Mapped[float] = mapped_column(Float, nullable=False)

    strong_areas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    weak_areas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    requirements_matched: Mapped[list | None] = mapped_column(JSON, nullable=True)
    requirements_missing: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Evidence per requirement: [{requirement, evidence, status, confidence, reason}, ...]
    evidence: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
