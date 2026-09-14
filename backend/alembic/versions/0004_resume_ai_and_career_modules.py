"""add integrated resume, optimizer, readiness and recruiter modules

Revision ID: 0004
Revises: 0003
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on = None

def uuid_col():
    return postgresql.UUID(as_uuid=True)

def upgrade() -> None:
    resume_status = sa.Enum("UPLOADED", "PARSING", "PARSED", "PARSE_FAILED", name="resume_status")
    resume_section_type = sa.Enum("CONTACT","SUMMARY","SKILLS","EDUCATION","EXPERIENCE","PROJECTS","CERTIFICATIONS","ACHIEVEMENTS", name="resume_section_type")
    skill_category = sa.Enum("LANGUAGE","FRAMEWORK","TOOL","DATABASE","CLOUD","SOFT_SKILL","OTHER", name="skill_category")
    analysis_status = sa.Enum("PENDING","COMPLETED","FAILED", name="analysis_status")
    section_name = sa.Enum("SUMMARY","SKILLS","EXPERIENCE","PROJECTS","EDUCATION","CERTIFICATIONS","ACHIEVEMENTS", name="resume_section_name")
    suggestion_type = sa.Enum("GRAMMAR","FORMATTING","CONTENT","KEYWORD","ACHIEVEMENT", name="suggestion_type")
    suggestion_severity = sa.Enum("LOW","MEDIUM","HIGH", name="suggestion_severity")
    keyword_status = sa.Enum("PRESENT","MISSING", name="keyword_status")

    op.create_table("resumes",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("storage_backend", sa.String(50), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("status", resume_status, nullable=False),
        sa.Column("parse_error", sa.Text()),
        sa.Column("raw_text", sa.Text()),
        sa.Column("full_name", sa.String(255)), sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)), sa.Column("location", sa.String(255)),
        sa.Column("linkedin_url", sa.String(512)), sa.Column("github_url", sa.String(512)),
        sa.Column("portfolio_url", sa.String(512)), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_table("resume_sections",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section_type", resume_section_type, nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("content_text", sa.Text()), sa.Column("content_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_resume_sections_resume_id", "resume_sections", ["resume_id"])
    op.create_table("extracted_skills",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False), sa.Column("category", skill_category, nullable=False),
        sa.Column("proficiency_hint", sa.String(50)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_extracted_skills_resume_id", "extracted_skills", ["resume_id"])
    op.create_table("resume_analyses",
        sa.Column("id", uuid_col(), primary_key=True),
        sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", analysis_status, nullable=False), sa.Column("error_message", sa.Text()),
        sa.Column("overall_score", sa.Float()), sa.Column("ats_compatibility_score", sa.Float()),
        sa.Column("professional_summary_analysis", sa.Text()), sa.Column("strengths", sa.JSON()),
        sa.Column("weaknesses", sa.JSON()), sa.Column("missing_skills", sa.JSON()), sa.Column("missing_keywords", sa.JSON()),
        sa.Column("grammar_suggestions", sa.JSON()), sa.Column("formatting_suggestions", sa.JSON()),
        sa.Column("raw_ai_response", sa.JSON()), sa.Column("model_used", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_resume_analyses_resume_id", "resume_analyses", ["resume_id"])
    op.create_index("ix_resume_analyses_user_id", "resume_analyses", ["user_id"])
    op.create_table("resume_scores",
        sa.Column("id", uuid_col(), primary_key=True), sa.Column("analysis_id", uuid_col(), sa.ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section", section_name, nullable=False), sa.Column("score", sa.Float(), nullable=False), sa.Column("feedback", sa.Text()))
    op.create_index("ix_resume_scores_analysis_id", "resume_scores", ["analysis_id"])
    op.create_table("resume_suggestions",
        sa.Column("id", uuid_col(), primary_key=True), sa.Column("analysis_id", uuid_col(), sa.ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("suggestion_type", suggestion_type, nullable=False), sa.Column("section", sa.String(100)),
        sa.Column("severity", suggestion_severity, nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("suggested_fix", sa.Text()))
    op.create_index("ix_resume_suggestions_analysis_id", "resume_suggestions", ["analysis_id"])
    op.create_table("resume_keywords",
        sa.Column("id", uuid_col(), primary_key=True), sa.Column("analysis_id", uuid_col(), sa.ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("keyword", sa.String(150), nullable=False), sa.Column("status", keyword_status, nullable=False), sa.Column("relevance", sa.Float()))
    op.create_index("ix_resume_keywords_analysis_id", "resume_keywords", ["analysis_id"])
    op.create_table("company_matches",
        sa.Column("id", uuid_col(), primary_key=True), sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("company_name", sa.String(100), nullable=False),
        sa.Column("target_role", sa.String(150)), sa.Column("role_match_score", sa.Float(), nullable=False), sa.Column("resume_compatibility_score", sa.Float(), nullable=False),
        sa.Column("required_skills", sa.JSON()), sa.Column("matched_skills", sa.JSON()), sa.Column("missing_skills", sa.JSON()),
        sa.Column("relevant_keywords", sa.JSON()), sa.Column("improvement_suggestions", sa.JSON()), sa.Column("raw_ai_response", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_company_matches_resume_id", "company_matches", ["resume_id"])
    op.create_index("ix_company_matches_user_id", "company_matches", ["user_id"])

    for table, cols in [
        ("resume_optimizations", [
            sa.Column("id", uuid_col(), primary_key=True), sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("target_role", sa.String(255), nullable=False),
            sa.Column("target_company", sa.String(255)), sa.Column("job_description", sa.Text()), sa.Column("overall_score", sa.Float(), nullable=False),
            sa.Column("ats_score", sa.Float(), nullable=False), sa.Column("role_match_score", sa.Float(), nullable=False),
            sa.Column("summary_optimization", sa.JSON()), sa.Column("experience_optimizations", sa.JSON()), sa.Column("project_optimizations", sa.JSON()),
            sa.Column("skill_optimization", sa.JSON()), sa.Column("ats_analysis", sa.JSON()), sa.Column("company_match", sa.JSON()), sa.Column("improvement_report", sa.JSON()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now())]),
        ("resume_versions", [
            sa.Column("id", uuid_col(), primary_key=True), sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("version_number", sa.Integer(), nullable=False),
            sa.Column("original_content", sa.Text(), nullable=False), sa.Column("optimized_content", sa.Text(), nullable=False), sa.Column("changes_summary", sa.JSON()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now())]),
        ("interview_readiness_reports", [
            sa.Column("id", uuid_col(), primary_key=True), sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("resume_id", uuid_col(), sa.ForeignKey("resumes.id", ondelete="SET NULL")), sa.Column("target_role", sa.String(255), nullable=False),
            sa.Column("target_company", sa.String(255)), sa.Column("job_description", sa.Text()), sa.Column("overall_readiness_score", sa.Float(), nullable=False),
            sa.Column("confidence_level", sa.String(50), nullable=False), sa.Column("technical_readiness", sa.JSON()), sa.Column("coding_readiness", sa.JSON()),
            sa.Column("communication_readiness", sa.JSON()), sa.Column("resume_readiness", sa.JSON()), sa.Column("project_readiness", sa.JSON()),
            sa.Column("strong_areas", sa.JSON()), sa.Column("weak_areas", sa.JSON()), sa.Column("missing_evidence", sa.JSON()), sa.Column("knowledge_gaps", sa.JSON()),
            sa.Column("recommended_topics", sa.JSON()), sa.Column("action_plan", sa.JSON()), sa.Column("company_readiness_scores", sa.JSON()), sa.Column("career_insights", sa.JSON()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now())]),
    ]:
        op.create_table(table, *cols)

    op.create_table("notifications",
        sa.Column("id", uuid_col(), primary_key=True), sa.Column("user_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("notification_metadata", sa.JSON()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("recruiter_reports",
        sa.Column("id", uuid_col(), primary_key=True), sa.Column("recruiter_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_id", uuid_col(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("report_data", sa.JSON(), nullable=False),
        sa.Column("format_type", sa.String(20), server_default="JSON"), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))

def downgrade() -> None:
    for name in ["recruiter_reports","notifications","interview_readiness_reports","resume_versions","resume_optimizations","company_matches","resume_keywords","resume_suggestions","resume_scores","resume_analyses","extracted_skills","resume_sections","resumes"]:
        op.drop_table(name)
    for name in ["keyword_status","suggestion_severity","suggestion_type","resume_section_name","analysis_status","skill_category","resume_section_type","resume_status"]:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
