"""
Pydantic schemas that define the STRICT structured JSON contract the Gemini
AI service must return. Used with `response.model_validate_json()` (or
`model_validate` on parsed JSON) to catch malformed AI output before it
touches the database.
"""
from pydantic import BaseModel, Field, field_validator


def _clamp_0_100(v: float) -> float:
    return max(0.0, min(100.0, float(v)))


class SectionScoreAI(BaseModel):
    section: str
    score: float = Field(ge=0, le=100)
    feedback: str = ""

    @field_validator("score", mode="before")
    @classmethod
    def clamp_score(cls, v):
        return _clamp_0_100(v)


class SuggestionAI(BaseModel):
    type: str = Field(description="grammar | formatting | content | keyword | achievement")
    section: str | None = None
    severity: str = Field(default="medium", description="low | medium | high")
    message: str
    suggested_fix: str | None = None


class KeywordAI(BaseModel):
    keyword: str
    status: str = Field(description="present | missing")
    relevance: float = Field(default=0.5, ge=0, le=1)


class ResumeAnalysisAI(BaseModel):
    """Top-level structured response expected from the resume-analysis prompt."""

    overall_score: float = Field(ge=0, le=100)
    ats_compatibility_score: float = Field(ge=0, le=100)
    professional_summary_analysis: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    missing_skills: list[str] = []
    missing_keywords: list[str] = []
    grammar_suggestions: list[str] = []
    formatting_suggestions: list[str] = []
    section_scores: list[SectionScoreAI] = []
    suggestions: list[SuggestionAI] = []
    keywords: list[KeywordAI] = []

    @field_validator("overall_score", "ats_compatibility_score", mode="before")
    @classmethod
    def clamp(cls, v):
        return _clamp_0_100(v)


class CompanyMatchAI(BaseModel):
    """Top-level structured response expected from the company-match prompt."""

    role_match_score: float = Field(ge=0, le=100)
    resume_compatibility_score: float = Field(ge=0, le=100)
    required_skills: list[str] = []
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    relevant_keywords: list[str] = []
    improvement_suggestions: list[str] = []

    @field_validator("role_match_score", "resume_compatibility_score", mode="before")
    @classmethod
    def clamp(cls, v):
        return _clamp_0_100(v)


class ResumeExtractionAI(BaseModel):
    """Structured extraction schema used when parsing raw resume text into sections."""

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    professional_summary: str | None = None
    skills: list[str] = []
    education: list[dict] = []
    experience: list[dict] = []
    projects: list[dict] = []
    certifications: list[dict] = []
    achievements: list[str] = []
