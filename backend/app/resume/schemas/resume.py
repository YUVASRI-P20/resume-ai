import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.resume.models.resume import ResumeSectionType, ResumeStatus, SkillCategory


class ExtractedSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: SkillCategory
    proficiency_hint: str | None = None


class ResumeSectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    section_type: ResumeSectionType
    order_index: int
    content_text: str | None = None
    content_json: Any | None = None


class ResumeListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    status: ResumeStatus
    full_name: str | None = None
    email: str | None = None
    file_size_bytes: int
    created_at: datetime
    updated_at: datetime


class ResumeDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    status: ResumeStatus
    parse_error: str | None = None

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None

    file_size_bytes: int
    content_type: str
    created_at: datetime
    updated_at: datetime

    sections: list[ResumeSectionOut] = []
    skills: list[ExtractedSkillOut] = []


class ResumeUploadResponse(BaseModel):
    id: uuid.UUID
    status: ResumeStatus
    message: str
