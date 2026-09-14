"""
API endpoints for Module 9: AI Feedback Engine.
"""
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.feedback import InterviewFeedback, KnowledgeGap
from app.schemas.feedback import InterviewFeedbackOut, KnowledgeGapOut
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/{interview_id}", response_model=InterviewFeedbackOut)
async def get_interview_feedback(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = FeedbackService(db)
    feedback = await service.generate_feedback(interview_id, current_user.id)
    return feedback


@router.get("/{interview_id}/details", response_model=InterviewFeedbackOut)
async def get_interview_feedback_details(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = FeedbackService(db)
    feedback = await service.generate_feedback(interview_id, current_user.id)
    return feedback


@router.get("/{interview_id}/report", response_model=InterviewFeedbackOut)
async def get_final_report(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Final performance report for an interview: aggregate scores, strengths,
    weaknesses, knowledge gaps and hallucination findings — all derived from
    the user's real evaluation records."""
    service = FeedbackService(db)
    feedback = await service.generate_feedback(interview_id, current_user.id)
    return feedback


@router.get("/knowledge-gaps/{user_id}", response_model=List[KnowledgeGapOut])
async def get_knowledge_gaps(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to user knowledge gaps.")

    result = await db.execute(select(KnowledgeGap).filter(KnowledgeGap.user_id == user_id))
    return result.scalars().all()
