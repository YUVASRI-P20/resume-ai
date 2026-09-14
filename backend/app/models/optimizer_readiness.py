import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, DateTime, JSON, Uuid
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.user import User
from app.resume.models.resume import Resume

class ResumeOptimization(Base):
    __tablename__ = "resume_optimizations"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(Uuid(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String(255), nullable=False)
    target_company = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=True)
    overall_score = Column(Float, nullable=False, default=0.0)
    ats_score = Column(Float, nullable=False, default=0.0)
    role_match_score = Column(Float, nullable=False, default=0.0)
    summary_optimization = Column(JSON, nullable=True)
    experience_optimizations = Column(JSON, nullable=True)
    project_optimizations = Column(JSON, nullable=True)
    skill_optimization = Column(JSON, nullable=True)
    ats_analysis = Column(JSON, nullable=True)
    company_match = Column(JSON, nullable=True)
    improvement_report = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resume = relationship(Resume, backref="optimizations")
    user = relationship(User, backref="resume_optimizations")

class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(Uuid(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    original_content = Column(Text, nullable=False)
    optimized_content = Column(Text, nullable=False)
    changes_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resume = relationship(Resume, backref="versions")
    user = relationship(User, backref="resume_versions")

class InterviewReadinessReport(Base):
    __tablename__ = "interview_readiness_reports"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Uuid(as_uuid=True), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    target_role = Column(String(255), nullable=False)
    target_company = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=True)
    overall_readiness_score = Column(Float, nullable=False, default=0.0)
    confidence_level = Column(String(50), nullable=False, default="Moderate")
    technical_readiness = Column(JSON, nullable=True)
    coding_readiness = Column(JSON, nullable=True)
    communication_readiness = Column(JSON, nullable=True)
    resume_readiness = Column(JSON, nullable=True)
    project_readiness = Column(JSON, nullable=True)
    strong_areas = Column(JSON, nullable=True)
    weak_areas = Column(JSON, nullable=True)
    missing_evidence = Column(JSON, nullable=True)
    knowledge_gaps = Column(JSON, nullable=True)
    recommended_topics = Column(JSON, nullable=True)
    action_plan = Column(JSON, nullable=True)
    company_readiness_scores = Column(JSON, nullable=True)
    career_insights = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship(User, backref="readiness_reports")
