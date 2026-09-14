"""Schemas for companies, job roles, evidence-based matching, streaks and dashboard."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------- Companies & Job Roles ---------------- #
class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    industry: str | None = None


class JobRoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    description: str | None = None
    domain: str | None = None
    seniority: str | None = None
    job_description: str | None = None


class RoleRequirementsOut(BaseModel):
    """The role plus its actual requirements from the database."""

    role: JobRoleOut
    company: CompanyOut
    requirements: List[dict]  # [{requirement, category, importance}]


# ---------------- Role Match ---------------- #
class EvidenceItemOut(BaseModel):
    requirement: str
    category: str | None = None
    importance: int | None = None
    evidence: Optional[str] = None
    status: str  # strong | moderate | weak | missing
    confidence: float
    reason: str | None = None


class RoleMatchRequest(BaseModel):
    company_id: uuid.UUID
    job_role_id: uuid.UUID


class RoleMatchResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    company_id: uuid.UUID
    job_role_id: uuid.UUID
    match_percentage: float
    strong_areas: List[str] = []
    weak_areas: List[str] = []
    requirements_matched: List[str] = []
    requirements_missing: List[str] = []
    evidence: List[EvidenceItemOut] = []
    created_at: datetime


# ---------------- Streak ---------------- #
class StreakOut(BaseModel):
    streak_days: int
    longest_streak_days: int
    last_activity_date: Optional[str] = None


# ---------------- Dashboard aggregate ---------------- #
class ResumeSummaryOut(BaseModel):
    id: uuid.UUID
    original_filename: str
    status: str
    uploaded_at: datetime


class InterviewProgressOut(BaseModel):
    total: int
    completed: int
    in_progress: int
    last_score: Optional[float] = None


class KnowledgeGapOut(BaseModel):
    topic: str
    description: str


class DashboardOut(BaseModel):
    user_name: str
    email: str
    streak: StreakOut
    resume: Optional[ResumeSummaryOut] = None
    selected_company: Optional[str] = None
    selected_role: Optional[str] = None
    match_percentage: Optional[float] = None
    strong_areas: List[str] = []
    weak_areas: List[str] = []
    interview_progress: InterviewProgressOut
    knowledge_gaps: List[KnowledgeGapOut] = []
    roadmap_progress: Optional[float] = None
