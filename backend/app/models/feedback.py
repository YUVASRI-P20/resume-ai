"""
Module 9 — AI Feedback Engine models.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class FeedbackSeverity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class InterviewFeedback(Base):
    __tablename__ = "interview_feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    technical_score: Mapped[float] = mapped_column(Float, nullable=False)
    communication_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    coding_score: Mapped[float] = mapped_column(Float, nullable=False)

    interview_summary: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_feedback: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    interview: Mapped["Interview"] = relationship(back_populates="feedback")  # type: ignore[name-defined]
    categories: Mapped[list["FeedbackCategory"]] = relationship(back_populates="feedback", cascade="all, delete-orphan")
    strengths: Mapped[list["Strength"]] = relationship(back_populates="feedback", cascade="all, delete-orphan")
    weaknesses: Mapped[list["Weakness"]] = relationship(back_populates="feedback", cascade="all, delete-orphan")
    hallucinations: Mapped[list["HallucinationFinding"]] = relationship(back_populates="feedback", cascade="all, delete-orphan")


class FeedbackCategory(Base):
    __tablename__ = "feedback_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    feedback_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_feedbacks.id", ondelete="CASCADE"), nullable=False, index=True)

    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    comments: Mapped[str] = mapped_column(Text, nullable=False)

    feedback: Mapped["InterviewFeedback"] = relationship(back_populates="categories")


class KnowledgeGap(Base):
    __tablename__ = "knowledge_gaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("interviews.id", ondelete="SET NULL"), nullable=True, index=True)

    topic: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[FeedbackSeverity] = mapped_column(Enum(FeedbackSeverity), default=FeedbackSeverity.MEDIUM, nullable=False)
    repeated_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Strength(Base):
    __tablename__ = "strengths"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    feedback_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_feedbacks.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    feedback: Mapped["InterviewFeedback"] = relationship(back_populates="strengths")


class Weakness(Base):
    __tablename__ = "weaknesses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    feedback_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_feedbacks.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    feedback: Mapped["InterviewFeedback"] = relationship(back_populates="weaknesses")


class HallucinationFinding(Base):
    __tablename__ = "hallucination_findings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    feedback_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_feedbacks.id", ondelete="CASCADE"), nullable=False, index=True)

    concept: Mapped[str] = mapped_column(String(150), nullable=False)
    candidate_claim: Mapped[str] = mapped_column(Text, nullable=False)
    correct_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[FeedbackSeverity] = mapped_column(Enum(FeedbackSeverity), default=FeedbackSeverity.MEDIUM, nullable=False)
    confidence: float = mapped_column(Float, nullable=False)  # Evidence-based confidence 0-100

    feedback: Mapped["InterviewFeedback"] = relationship(back_populates="hallucinations")
