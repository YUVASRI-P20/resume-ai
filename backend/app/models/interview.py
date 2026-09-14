"""
Module 7 — AI Technical Interview Engine models.
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


class InterviewStatus(str, enum.Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InterviewType(str, enum.Enum):
    TECHNICAL = "Technical"
    RESUME_BASED = "Resume Based"
    COMPANY_SPECIFIC = "Company Specific"
    MIXED = "Mixed"


class InterviewDifficulty(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True)

    company: Mapped[str] = mapped_column(String(150), nullable=False)
    job_role: Mapped[str] = mapped_column(String(150), nullable=False)
    domain: Mapped[str] = mapped_column(String(150), nullable=False)
    difficulty: Mapped[InterviewDifficulty] = mapped_column(Enum(InterviewDifficulty), default=InterviewDifficulty.MEDIUM, nullable=False)
    interview_type: Mapped[InterviewType] = mapped_column(Enum(InterviewType), default=InterviewType.TECHNICAL, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    number_of_questions: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    status: Mapped[InterviewStatus] = mapped_column(Enum(InterviewStatus), default=InterviewStatus.CREATED, nullable=False)
    current_difficulty: Mapped[InterviewDifficulty] = mapped_column(Enum(InterviewDifficulty), default=InterviewDifficulty.MEDIUM, nullable=False)
    question_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_question_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="interviews")  # type: ignore[name-defined]
    resume: Mapped["Resume | None"] = relationship(foreign_keys=[resume_id])  # type: ignore[name-defined]
    questions: Mapped[list["InterviewQuestion"]] = relationship(back_populates="interview", cascade="all, delete-orphan")
    summary: Mapped["InterviewSummary | None"] = relationship(back_populates="interview", uselist=False, cascade="all, delete-orphan")
    feedback: Mapped["InterviewFeedback | None"] = relationship(back_populates="interview", uselist=False, cascade="all, delete-orphan")  # type: ignore[name-defined]


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)

    question_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)  # conceptual, scenario, problem_solving, resume, company
    difficulty: Mapped[InterviewDifficulty] = mapped_column(Enum(InterviewDifficulty), nullable=False)
    expected_key_points: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON or comma-separated string

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    interview: Mapped["Interview"] = relationship(back_populates="questions")
    answer: Mapped["InterviewAnswer | None"] = relationship(back_populates="question", uselist=False, cascade="all, delete-orphan")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False, unique=True)

    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    question: Mapped["InterviewQuestion"] = relationship(back_populates="answer")
    evaluation: Mapped["InterviewEvaluation | None"] = relationship(back_populates="answer", uselist=False, cascade="all, delete-orphan")


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_answers.id", ondelete="CASCADE"), nullable=False, unique=True)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    correctness: Mapped[float] = mapped_column(Float, nullable=False)
    technical_depth: Mapped[float] = mapped_column(Float, nullable=False)
    clarity: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_gap: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_difficulty: Mapped[InterviewDifficulty] = mapped_column(Enum(InterviewDifficulty), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    answer: Mapped["InterviewAnswer"] = relationship(back_populates="evaluation")


class InterviewSummary(Base):
    __tablename__ = "interview_summaries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True)

    overall_performance: Mapped[str] = mapped_column(Text, nullable=False)
    technical_performance: Mapped[str] = mapped_column(Text, nullable=False)
    strong_topics: Mapped[str] = mapped_column(Text, nullable=False)  # Stored as comma-separated or JSON
    weak_topics: Mapped[str] = mapped_column(Text, nullable=False)
    average_score: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty_progression: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_gaps: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvement_suggestions: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    interview: Mapped["Interview"] = relationship(back_populates="summary")
