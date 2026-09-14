from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Module 5: Resume Optimizer Schemas ---

class ResumeOptimizeRequest(BaseModel):
    target_role: str = Field(..., description="Target job role, e.g., Python Backend Developer")
    target_company: Optional[str] = Field(None, description="Optional target company name")
    job_description: Optional[str] = Field(None, description="Optional job description text")
    target_skills: Optional[List[str]] = Field(None, description="Optional list of target skills")

class SummaryOptimization(BaseModel):
    original: str
    optimized: str
    reason: str

class ExperienceOptimizationItem(BaseModel):
    original: str
    optimized: str
    reason: str

class ProjectOptimizationItem(BaseModel):
    title: str
    original_description: str
    optimized_description: str
    technical_impact: str
    reason: str

class SkillOptimizationResult(BaseModel):
    existing_skills: List[str]
    strong_skills: List[str]
    missing_role_relevant_skills: List[str]
    missing_keywords: List[str]
    recommended_skills_to_learn: List[str]

class ATSAnalysisResult(BaseModel):
    ats_score: float
    keyword_coverage_percentage: float
    missing_keywords: List[str]
    formatting_warnings: List[str]
    section_completeness: Dict[str, bool]
    skill_alignment: float
    role_alignment: float

class CompanyMatchResult(BaseModel):
    company_name: str
    resume_compatibility_score: float
    role_match_score: float
    matching_areas: List[str]
    missing_areas: List[str]
    recommendations: List[str]

class ResumeImprovementReport(BaseModel):
    overall_resume_score: float
    ats_compatibility: float
    role_match: float
    company_job_alignment: float
    strong_sections: List[str]
    weak_sections: List[str]
    missing_keywords: List[str]
    missing_skills: List[str]
    grammar_suggestions: List[str]
    formatting_suggestions: List[str]
    summary_improvements: SummaryOptimization
    experience_improvements: List[ExperienceOptimizationItem]
    project_improvements: List[ProjectOptimizationItem]
    recommended_actions: List[str]

class ResumeOptimizationResponse(BaseModel):
    optimization_id: str
    resume_id: str
    user_id: str
    target_role: str
    target_company: Optional[str]
    overall_score: float
    ats_score: float
    role_match_score: float
    summary_optimization: SummaryOptimization
    experience_optimizations: List[ExperienceOptimizationItem]
    project_optimizations: List[ProjectOptimizationItem]
    skill_optimization: SkillOptimizationResult
    ats_analysis: ATSAnalysisResult
    company_match: Optional[CompanyMatchResult]
    improvement_report: ResumeImprovementReport
    created_at: str

class ResumeVersionResponse(BaseModel):
    version_id: str
    resume_id: str
    version_number: int
    original_content: str
    optimized_content: str
    changes_summary: Dict[str, Any]
    created_at: str


# --- Module 6: Interview Readiness Predictor Schemas ---

class ReadinessAnalyzeRequest(BaseModel):
    resume_id: Optional[str] = Field(None, description="Resume ID to base analysis on")
    target_role: str = Field(..., description="Target job role")
    target_company: Optional[str] = Field(None, description="Optional target company")
    job_description: Optional[str] = Field(None, description="Optional job description")

class TechnicalReadinessDetail(BaseModel):
    score: float
    evaluated_topics: Dict[str, str]  # topic -> status/level
    feedback: str

class CodingReadinessDetail(BaseModel):
    score: float
    problem_solving: str
    algorithmic_thinking: str
    complexity_analysis: str
    status: str

class CommunicationReadinessDetail(BaseModel):
    score: float
    clarity: str
    structure: str
    technical_explanation: str
    status: str

class ResumeReadinessDetail(BaseModel):
    score: float
    ats_compatibility: float
    summary: str

class ProjectReadinessDetail(BaseModel):
    score: float
    explanation_readiness: str
    architecture_clarity: str

class KnowledgeGapItem(BaseModel):
    strong_topics: List[str]
    weak_topics: List[str]
    missing_topics: List[str]

class ActionPlanItem(BaseModel):
    priority: int
    topic: str
    reason: str
    suggested_activity: str
    estimated_study_time: str
    difficulty: str

class CompanyReadinessItem(BaseModel):
    company_name: str
    readiness_score: float
    notes: str

class InterviewReadinessResponse(BaseModel):
    report_id: str
    user_id: str
    target_role: str
    target_company: Optional[str]
    overall_readiness_score: float
    confidence_level: str
    technical_readiness: TechnicalReadinessDetail
    coding_readiness: CodingReadinessDetail
    communication_readiness: CommunicationReadinessDetail
    resume_readiness: ResumeReadinessDetail
    project_readiness: ProjectReadinessDetail
    strong_areas: List[str]
    weak_areas: List[str]
    missing_evidence: List[str]
    knowledge_gaps: KnowledgeGapItem
    recommended_topics: List[str]
    action_plan: List[ActionPlanItem]
    company_readiness_scores: List[CompanyReadinessItem]
    career_insights: List[str]
    created_at: str
