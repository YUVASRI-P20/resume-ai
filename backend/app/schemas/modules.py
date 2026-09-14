"""
Pydantic schemas for Module 7 (AI Technical Interview Engine) and Module 8 (Coding Interview Engine).
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.interview import InterviewType, InterviewDifficulty, InterviewStatus
from app.models.coding import CodingDifficulty, SubmissionStatus


# ---- Module 7: Interview Schemas ----

class InterviewStartRequest(BaseModel):
    company: str = Field(..., min_length=1, max_length=150)
    job_role: str = Field(..., min_length=1, max_length=150)
    domain: str = Field(..., min_length=1, max_length=150)
    difficulty: InterviewDifficulty = InterviewDifficulty.MEDIUM
    interview_type: InterviewType = InterviewType.TECHNICAL
    duration_minutes: int = Field(30, ge=5, le=120)
    number_of_questions: int = Field(5, ge=1, le=20)
    resume_id: Optional[uuid.UUID] = None


class QuestionOut(BaseModel):
    id: uuid.UUID
    question_index: int
    question_text: str
    question_type: str
    difficulty: InterviewDifficulty

    class Config:
        from_attributes = True


class InterviewOut(BaseModel):
    id: uuid.UUID
    company: str
    job_role: str
    domain: str
    difficulty: InterviewDifficulty
    interview_type: InterviewType
    duration_minutes: int
    number_of_questions: int
    status: InterviewStatus
    current_difficulty: InterviewDifficulty
    question_count: int
    completed_question_count: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerSubmitRequest(BaseModel):
    question_id: uuid.UUID
    answer_text: str = Field(..., min_length=1)


class EvaluationOut(BaseModel):
    id: uuid.UUID
    score: float
    correctness: float
    technical_depth: float
    clarity: float
    confidence: float
    feedback: str
    knowledge_gap: Optional[str] = None
    next_difficulty: InterviewDifficulty

    class Config:
        from_attributes = True


class InterviewAnswerOut(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    answer_text: str
    submitted_at: datetime
    evaluation: Optional[EvaluationOut] = None

    class Config:
        from_attributes = True


class InterviewSummaryOut(BaseModel):
    overall_performance: str
    technical_performance: str
    strong_topics: List[str]
    weak_topics: List[str]
    average_score: float
    difficulty_progression: List[str]
    knowledge_gaps: Optional[List[str]] = None
    improvement_suggestions: List[str]

    class Config:
        from_attributes = True


# ---- Module 8: Coding Schemas ----

class CodingQuestionOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    difficulty: CodingDifficulty
    domain: str
    constraints: str
    examples: List[Dict[str, Any]]
    expected_time_complexity: str
    expected_space_complexity: str
    supported_languages: List[str]

    class Config:
        from_attributes = True


class CodingSubmissionCreate(BaseModel):
    question_id: uuid.UUID
    language: str = Field(..., min_length=1)
    source_code: str = Field(..., min_length=1)


class CodeExecutionOut(BaseModel):
    id: uuid.UUID
    passed_tests: int
    total_tests: int
    runtime_ms: float
    memory_mb: float
    error_message: Optional[str] = None
    execution_status: str

    class Config:
        from_attributes = True


class CodeReviewOut(BaseModel):
    id: uuid.UUID
    score: float
    correctness: float
    code_quality: float
    time_complexity: str
    space_complexity: str
    strengths: List[str]
    issues: List[str]
    suggestions: List[str]
    better_approach: str

    class Config:
        from_attributes = True


class CodingSubmissionOut(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    language: str
    source_code: str
    status: SubmissionStatus
    submission_time: datetime
    execution: Optional[CodeExecutionOut] = None
    review: Optional[CodeReviewOut] = None

    class Config:
        from_attributes = True
