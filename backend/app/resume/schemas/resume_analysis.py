import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.resume.models.resume_analysis import AnalysisStatus, KeywordStatus, SuggestionSeverity, SuggestionType


class ResumeScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    section: str
    score: float
    feedback: str | None = None


class ResumeSuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    suggestion_type: SuggestionType
    section: str | None = None
    severity: SuggestionSeverity
    message: str
    suggested_fix: str | None = None


class ResumeKeywordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    keyword: str
    status: KeywordStatus
    relevance: float | None = None


class ResumeAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    status: AnalysisStatus
    error_message: str | None = None

    overall_score: float | None = None
    ats_compatibility_score: float | None = None
    professional_summary_analysis: str | None = None
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
    missing_skills: list[str] | None = None
    missing_keywords: list[str] | None = None
    grammar_suggestions: list[str] | None = None
    formatting_suggestions: list[str] | None = None

    section_scores: list[ResumeScoreOut] = []
    suggestions: list[ResumeSuggestionOut] = []
    keywords: list[ResumeKeywordOut] = []

    created_at: datetime


class AnalyzeResumeRequest(BaseModel):
    force_refresh: bool = Field(default=False, description="Re-run analysis even if a recent one exists")


SUPPORTED_COMPANIES: list[str] = [
    "Google", "Microsoft", "Amazon", "Zoho", "TCS",
    "Infosys", "Accenture", "Flipkart", "Adobe", "Oracle",
]


class CompanyMatchRequest(BaseModel):
    company_name: str = Field(description=f"One of: {', '.join(SUPPORTED_COMPANIES)}")
    target_role: str | None = Field(default=None, description="Optional specific role, e.g. 'Backend Engineer'")


class CompanyMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    company_name: str
    target_role: str | None = None
    role_match_score: float
    resume_compatibility_score: float
    required_skills: list[str] | None = None
    matched_skills: list[str] | None = None
    missing_skills: list[str] | None = None
    relevant_keywords: list[str] | None = None
    improvement_suggestions: list[str] | None = None
    created_at: datetime
    disclaimer: str = (
        "These scores estimate resume-to-role compatibility based on keyword and skill "
        "overlap. They are not a prediction of actual hiring outcomes or interview invites."
    )
