"""add interview and coding engine tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-07

"""
import uuid
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- interviews ----
    op.create_table(
        "interviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("company", sa.String(length=150), nullable=False),
        sa.Column("job_role", sa.String(length=150), nullable=False),
        sa.Column("domain", sa.String(length=150), nullable=False),
        sa.Column("difficulty", sa.Enum("Easy", "Medium", "Hard", name="interviewdifficulty"), nullable=False),
        sa.Column("interview_type", sa.Enum("Technical", "Resume Based", "Company Specific", "Mixed", name="interviewtype"), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("number_of_questions", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("CREATED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="interviewstatus"), nullable=False),
        sa.Column("current_difficulty", sa.Enum("Easy", "Medium", "Hard", name="interviewdifficulty_current"), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("completed_question_count", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_interviews_user_id", "interviews", ["user_id"])

    # ---- interview_questions ----
    op.create_table(
        "interview_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("interview_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_index", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("difficulty", sa.Enum("Easy", "Medium", "Hard", name="interviewdifficulty_q"), nullable=False),
        sa.Column("expected_key_points", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_interview_questions_interview_id", "interview_questions", ["interview_id"])

    # ---- interview_answers ----
    op.create_table(
        "interview_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("interview_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["interview_questions.id"], ondelete="CASCADE"),
    )

    # ---- interview_evaluations ----
    op.create_table(
        "interview_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("answer_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("correctness", sa.Float(), nullable=False),
        sa.Column("technical_depth", sa.Float(), nullable=False),
        sa.Column("clarity", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("knowledge_gap", sa.Text(), nullable=True),
        sa.Column("next_difficulty", sa.Enum("Easy", "Medium", "Hard", name="interviewdifficulty_eval"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["answer_id"], ["interview_answers.id"], ondelete="CASCADE"),
    )

    # ---- coding_questions ----
    op.create_table(
        "coding_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.Enum("Easy", "Medium", "Hard", name="codingdifficulty"), nullable=False),
        sa.Column("domain", sa.String(length=100), nullable=False),
        sa.Column("constraints", sa.Text(), nullable=False),
        sa.Column("examples", sa.JSON(), nullable=False),
        sa.Column("expected_time_complexity", sa.String(length=50), nullable=False),
        sa.Column("expected_space_complexity", sa.String(length=50), nullable=False),
        sa.Column("supported_languages", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ---- coding_submissions ----
    op.create_table(
        "coding_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("source_code", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "RUNNING", "PASSED", "FAILED", "TIMEOUT", "COMPILATION_ERROR", "RUNTIME_ERROR", name="submissionstatus"), nullable=False),
        sa.Column("submission_time", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["coding_questions.id"], ondelete="CASCADE"),
    )

    # ---- code_executions ----
    op.create_table(
        "code_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("passed_tests", sa.Integer(), nullable=False),
        sa.Column("total_tests", sa.Integer(), nullable=False),
        sa.Column("runtime_ms", sa.Float(), nullable=False),
        sa.Column("memory_mb", sa.Float(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("execution_status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["coding_submissions.id"], ondelete="CASCADE"),
    )

    # ---- code_reviews ----
    op.create_table(
        "code_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("correctness", sa.Float(), nullable=False),
        sa.Column("code_quality", sa.Float(), nullable=False),
        sa.Column("time_complexity", sa.String(length=50), nullable=False),
        sa.Column("space_complexity", sa.String(length=50), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("issues", sa.JSON(), nullable=False),
        sa.Column("suggestions", sa.JSON(), nullable=False),
        sa.Column("better_approach", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["coding_submissions.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("code_reviews")
    op.drop_table("code_executions")
    op.drop_table("coding_submissions")
    op.drop_table("coding_questions")
    op.drop_table("interview_evaluations")
    op.drop_table("interview_answers")
    op.drop_table("interview_questions")
    op.drop_table("interviews")
