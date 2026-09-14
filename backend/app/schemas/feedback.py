"""
Pydantic schemas for Module 9 (AI Feedback Engine).
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.feedback import FeedbackSeverity


class FeedbackCategoryOut(BaseModel):
    id: uuid.UUID
    category_name: str
    score: float
    comments: str

    class Config:
        from_attributes = True


class StrengthOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str

    class Config:
        from_attributes = True


class WeaknessOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str

    class Config:
        from_attributes = True


class HallucinationFindingOut(BaseModel):
    id: uuid.UUID
    concept: str
    candidate_claim: str
    correct_explanation: str
    severity: FeedbackSeverity
    confidence: float

    class Config:
        from_attributes = True


class KnowledgeGapOut(BaseModel):
    id: uuid.UUID
    topic: str
    description: str
    severity: FeedbackSeverity
    repeated_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewFeedbackOut(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    user_id: uuid.UUID
    overall_score: float
    technical_score: float
    communication_score: float
    confidence_score: float
    coding_score: float
    interview_summary: str
    detailed_feedback: str
    created_at: datetime
    categories: List[FeedbackCategoryOut] = []
    strengths: List[StrengthOut] = []
    weaknesses: List[WeaknessOut] = []
    hallucinations: List[HallucinationFindingOut] = []

    class Config:
        from_attributes = True
