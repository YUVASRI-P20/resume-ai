"""add feedback and roadmap tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-07

"""
import uuid
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- interview_feedbacks ----
    op.create_table(
        "interview_feedbacks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("interview_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("technical_score", sa.Float(), nullable=False),
        sa.Column("communication_score", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("coding_score", sa.Float(), nullable=False),
        sa.Column("interview_summary", sa.Text(), nullable=False),
        sa.Column("detailed_feedback", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_interview_feedbacks_interview_id", "interview_feedbacks", ["interview_id"], unique=True)
    op.create_index("ix_interview_feedbacks_user_id", "interview_feedbacks", ["user_id"])

    # ---- feedback_categories ----
    op.create_table(
        "feedback_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("feedback_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_name", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["feedback_id"], ["interview_feedbacks.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_feedback_categories_feedback_id", "feedback_categories", ["feedback_id"])

    # ---- knowledge_gaps ----
    op.create_table(
        "knowledge_gaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interview_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("topic", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.Enum("Low", "Medium", "High", "Critical", name="feedbackseverity"), nullable=False),
        sa.Column("repeated_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_knowledge_gaps_user_id", "knowledge_gaps", ["user_id"])

    # ---- strengths ----
    op.create_table(
        "strengths",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("feedback_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["feedback_id"], ["interview_feedbacks.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_strengths_feedback_id", "strengths", ["feedback_id"])

    # ---- weaknesses ----
    op.create_table(
        "weaknesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("feedback_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["feedback_id"], ["interview_feedbacks.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_weaknesses_feedback_id", "weaknesses", ["feedback_id"])

    # ---- hallucination_findings ----
    op.create_table(
        "hallucination_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("feedback_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("concept", sa.String(length=150), nullable=False),
        sa.Column("candidate_claim", sa.Text(), nullable=False),
        sa.Column("correct_explanation", sa.Text(), nullable=False),
        sa.Column("severity", sa.Enum("Low", "Medium", "High", "Critical", name="feedbackseverity_hal"), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["feedback_id"], ["interview_feedbacks.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_hallucination_findings_feedback_id", "hallucination_findings", ["feedback_id"])

    # ---- knowledge_nodes ----
    op.create_table(
        "knowledge_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic_name", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False),
        sa.Column("status", sa.Enum("Not Started", "In Progress", "Mastered", "Weak", name="nodestatus"), nullable=False),
        sa.Column("is_strength", sa.Boolean(), nullable=False),
        sa.Column("is_weakness", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_knowledge_nodes_user_id", "knowledge_nodes", ["user_id"])

    # ---- knowledge_edges ----
    op.create_table(
        "knowledge_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_node_id"], ["knowledge_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_node_id"], ["knowledge_nodes.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_knowledge_edges_user_id", "knowledge_edges", ["user_id"])

    # ---- learning_roadmaps ----
    op.create_table(
        "learning_roadmaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("total_weeks", sa.Integer(), nullable=False),
        sa.Column("completion_percentage", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_learning_roadmaps_user_id", "learning_roadmaps", ["user_id"], unique=True)

    # ---- roadmap_weeks ----
    op.create_table(
        "roadmap_weeks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("roadmap_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=200), nullable=False),
        sa.Column("objectives", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["learning_roadmaps.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_roadmap_weeks_roadmap_id", "roadmap_weeks", ["roadmap_id"])

    # ---- roadmap_tasks ----
    op.create_table(
        "roadmap_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("week_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("task_title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("study_time_hours", sa.Float(), nullable=False),
        sa.Column("priority", sa.Enum("Low", "Medium", "High", "Critical", name="taskpriority"), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=False),
        sa.Column("resources", sa.JSON(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["week_id"], ["roadmap_weeks.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_roadmap_tasks_week_id", "roadmap_tasks", ["week_id"])

    # ---- learning_progresses ----
    op.create_table(
        "learning_progresses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_tasks", sa.Integer(), nullable=False),
        sa.Column("completed_tasks", sa.Integer(), nullable=False),
        sa.Column("streak_days", sa.Integer(), nullable=False),
        sa.Column("last_activity_date", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_learning_progresses_user_id", "learning_progresses", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("learning_progresses")
    op.drop_table("roadmap_tasks")
    op.drop_table("roadmap_weeks")
    op.drop_table("learning_roadmaps")
    op.drop_table("knowledge_edges")
    op.drop_table("knowledge_nodes")
    op.drop_table("hallucination_findings")
    op.drop_table("weaknesses")
    op.drop_table("strengths")
    op.drop_table("knowledge_gaps")
    op.drop_table("feedback_categories")
    op.drop_table("interview_feedbacks")
