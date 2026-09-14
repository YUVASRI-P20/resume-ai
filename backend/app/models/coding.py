"""
Module 8 — Coding Interview Engine models.
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
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class CodingDifficulty(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"


class CodingQuestion(Base):
    __tablename__ = "coding_questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[CodingDifficulty] = mapped_column(Enum(CodingDifficulty), default=CodingDifficulty.MEDIUM, nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    constraints: Mapped[str] = mapped_column(Text, nullable=False)  # JSON or text list
    examples: Mapped[list | dict] = mapped_column(JSON, nullable=False)  # list of examples
    expected_time_complexity: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_space_complexity: Mapped[str] = mapped_column(String(50), nullable=False)
    supported_languages: Mapped[list] = mapped_column(JSON, nullable=False)  # ["Python", "Java", "JavaScript", "C++"]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    test_cases: Mapped[list["CodingTestCase"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    submissions: Mapped[list["CodingSubmission"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class CodingTestCase(Base):
    __tablename__ = "coding_test_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("coding_questions.id", ondelete="CASCADE"), nullable=False, index=True)

    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    question: Mapped["CodingQuestion"] = relationship(back_populates="test_cases")


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("coding_questions.id", ondelete="CASCADE"), nullable=False, index=True)

    language: Mapped[str] = mapped_column(String(50), nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    submission_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="coding_submissions")  # type: ignore[name-defined]
    question: Mapped["CodingQuestion"] = relationship(back_populates="submissions")
    execution: Mapped["CodeExecution | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
    review: Mapped["CodeReview | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")


class CodeExecution(Base):
    __tablename__ = "code_executions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("coding_submissions.id", ondelete="CASCADE"), nullable=False, unique=True)

    passed_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    runtime_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    memory_mb: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_status: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    submission: Mapped["CodingSubmission"] = relationship(back_populates="execution")


class CodeReview(Base):
    __tablename__ = "code_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("coding_submissions.id", ondelete="CASCADE"), nullable=False, unique=True)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    correctness: Mapped[float] = mapped_column(Float, nullable=False)
    code_quality: Mapped[float] = mapped_column(Float, nullable=False)
    time_complexity: Mapped[str] = mapped_column(String(50), nullable=False)
    space_complexity: Mapped[str] = mapped_column(String(50), nullable=False)
    strengths: Mapped[list | dict] = mapped_column(JSON, nullable=False)
    issues: Mapped[list | dict] = mapped_column(JSON, nullable=False)
    suggestions: Mapped[list | dict] = mapped_column(JSON, nullable=False)
    better_approach: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    submission: Mapped["CodingSubmission"] = relationship(back_populates="review")
