"""Module 4 — AI Resume Analyzer models."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeAnalysis(Base):
    """One AI analysis run for a resume. History is maintained by keeping all rows."""
    __tablename__ = "resume_analyses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    status: Mapped[AnalysisStatus] = mapped_column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ats_compatibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    professional_summary_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    grammar_suggestions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    formatting_suggestions: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Raw AI response kept for audit/debugging (never exposes API key, just content)
    raw_ai_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="analyses")  # noqa: F821
    section_scores: Mapped[list["ResumeScore"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
    suggestions: Mapped[list["ResumeSuggestion"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
    keywords: Mapped[list["ResumeKeyword"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")


class ResumeSectionName(str, enum.Enum):
    SUMMARY = "summary"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    ACHIEVEMENTS = "achievements"


class ResumeScore(Base):
    """Section-wise score belonging to a specific analysis run."""
    __tablename__ = "resume_scores"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=False, index=True)

    section: Mapped[ResumeSectionName] = mapped_column(Enum(ResumeSectionName), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis: Mapped["ResumeAnalysis"] = relationship(back_populates="section_scores")


class SuggestionType(str, enum.Enum):
    GRAMMAR = "grammar"
    FORMATTING = "formatting"
    CONTENT = "content"
    KEYWORD = "keyword"
    ACHIEVEMENT = "achievement"


class SuggestionSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResumeSuggestion(Base):
    __tablename__ = "resume_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=False, index=True)

    suggestion_type: Mapped[SuggestionType] = mapped_column(Enum(SuggestionType), nullable=False)
    section: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity: Mapped[SuggestionSeverity] = mapped_column(Enum(SuggestionSeverity), default=SuggestionSeverity.MEDIUM, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis: Mapped["ResumeAnalysis"] = relationship(back_populates="suggestions")


class KeywordStatus(str, enum.Enum):
    PRESENT = "present"
    MISSING = "missing"


class ResumeKeyword(Base):
    __tablename__ = "resume_keywords"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=False, index=True)

    keyword: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[KeywordStatus] = mapped_column(Enum(KeywordStatus), nullable=False)
    relevance: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-1 relevance weight

    analysis: Mapped["ResumeAnalysis"] = relationship(back_populates="keywords")


class CompanyMatch(Base):
    """Company/role match result. History maintained by keeping all rows per resume+company."""
    __tablename__ = "company_matches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_role: Mapped[str | None] = mapped_column(String(150), nullable=True)

    role_match_score: Mapped[float] = mapped_column(Float, nullable=False)
    resume_compatibility_score: Mapped[float] = mapped_column(Float, nullable=False)

    required_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    matched_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    relevant_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    improvement_suggestions: Mapped[list | None] = mapped_column(JSON, nullable=True)

    raw_ai_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="company_matches")  # noqa: F821
