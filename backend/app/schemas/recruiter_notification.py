from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Module 11: Recruiter Schemas ---

class CandidateSearchQuery(BaseModel):
    search: Optional[str] = Field(None, description="Search term for name or email")
    skills: Optional[str] = Field(None, description="Comma-separated skills filter")
    role: Optional[str] = Field(None, description="Target job role filter")
    min_resume_score: Optional[float] = Field(None, description="Minimum resume score")
    min_readiness_score: Optional[float] = Field(None, description="Minimum interview readiness score")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

class CandidateSummaryResponse(BaseModel):
    candidate_id: str
    name: str
    email: str
    relevant_skills: List[str]
    resume_score: float
    role_match_score: float
    interview_readiness: float
    latest_interview_score: float

class CandidateDetailResponse(BaseModel):
    candidate_id: str
    profile: Dict[str, Any]
    resume: Dict[str, Any]
    interview: Dict[str, Any]
    coding: Dict[str, Any]
    readiness: Dict[str, Any]

class CandidateCompareRequest(BaseModel):
    candidate_ids: List[str] = Field(..., min_items=2, max_items=5)

class CandidateComparisonResponse(BaseModel):
    compared_candidates: List[CandidateSummaryResponse]
    metrics_comparison: Dict[str, Any]
    summary_insights: List[str]

class RecruiterAnalyticsResponse(BaseModel):
    total_candidates: int
    candidates_evaluated: int
    average_resume_score: float
    average_interview_score: float
    average_readiness_score: float
    top_skills: List[str]
    readiness_distribution: Dict[str, int]
    role_distribution: Dict[str, int]

class ReportGenerateRequest(BaseModel):
    candidate_id: str
    format: str = Field("JSON", description="JSON or CSV")


# --- Module 12: Notification Schemas ---

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_read: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: str

class NotificationCreate(BaseModel):
    user_id: str
    type: str
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
