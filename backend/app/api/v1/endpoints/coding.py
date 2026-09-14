"""
API endpoints for Module 8: Coding Interview Engine.
"""
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.coding import CodingQuestion, CodingSubmission, CodeExecution, CodeReview
from app.schemas.modules import (
    CodingQuestionOut,
    CodingSubmissionCreate,
    CodingSubmissionOut,
    CodeReviewOut,
)
from app.services.coding_service import CodingService

router = APIRouter(prefix="/coding", tags=["coding"])


class CodingStartRequest(BaseModel):
    """Start a coding test grounded in the candidate's actual resume skills."""

    resume_id: Optional[uuid.UUID] = None


class CodingStartResponse(BaseModel):
    question: Optional[CodingQuestionOut] = None
    message: Optional[str] = None


@router.post("/start", response_model=CodingStartResponse, status_code=status.HTTP_201_CREATED)
async def start_coding_test(
    payload: CodingStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Pick a coding problem matching the candidate's REAL resume skills.
    Returns a proper message when no questions are configured — never fabricates one."""
    if not payload.resume_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload your resume before starting the personalized coding test.",
        )

    service = CodingService(db)
    question = await service.pick_question_for_resume(current_user.id, payload.resume_id)
    if question is None:
        return CodingStartResponse(
            question=None,
            message="No coding questions are available yet. Please check back later.",
        )
    return CodingStartResponse(question=CodingQuestionOut.model_validate(question))


@router.get("/questions", response_model=List[CodingQuestionOut])
async def get_coding_questions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(CodingQuestion))
    return result.scalars().all()


@router.get("/questions/{question_id}", response_model=CodingQuestionOut)
async def get_coding_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    question = await db.get(CodingQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Coding question not found.")
    return question


@router.post("/submissions", response_model=CodingSubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_code(
    payload: CodingSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = CodingService(db)
    submission = await service.submit_and_execute(current_user.id, payload)
    return submission


@router.get("/submissions", response_model=List[CodingSubmissionOut])
async def get_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(CodingSubmission).filter(CodingSubmission.user_id == current_user.id).order_by(CodingSubmission.submission_time.desc())
    )
    return result.scalars().all()


@router.get("/submissions/{submission_id}", response_model=CodingSubmissionOut)
async def get_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    submission = await db.get(CodingSubmission, submission_id)
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission


@router.get("/submissions/{submission_id}/result", response_model=CodingSubmissionOut)
async def get_submission_result(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    submission = await db.get(CodingSubmission, submission_id)
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission


@router.post("/submissions/{submission_id}/review", response_model=CodeReviewOut)
async def request_code_review(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    submission = await db.get(CodingSubmission, submission_id)
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Submission not found.")
    
    service = CodingService(db)
    try:
        review = await service.generate_ai_review(submission_id)
    except Exception as exc:  # noqa: BLE001
        detail = getattr(exc, "detail", None) or "AI code review is temporarily unavailable. Please try again."
        raise HTTPException(status_code=getattr(exc, "status_code", 502), detail=detail)
    return review
