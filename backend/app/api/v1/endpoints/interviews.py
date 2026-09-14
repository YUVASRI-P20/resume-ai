"""
API endpoints for Module 7: AI Technical Interview Engine.
"""
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.interview import Interview, InterviewStatus
from app.schemas.modules import (
    InterviewStartRequest,
    InterviewOut,
    QuestionOut,
    AnswerSubmitRequest,
    InterviewAnswerOut,
    EvaluationOut,
    InterviewSummaryOut,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/start", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
async def start_interview(
    payload: InterviewStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = InterviewService(db)
    interview = await service.start_interview(current_user.id, payload)
    return interview


@router.get("/history", response_model=List[InterviewOut])
async def get_interview_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{interview_id}", response_model=InterviewOut)
async def get_interview(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")
    return interview


@router.post("/{interview_id}/answer", response_model=EvaluationOut)
async def submit_answer(
    interview_id: uuid.UUID,
    payload: AnswerSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    service = InterviewService(db)
    evaluation = await service.submit_answer(interview_id, payload.question_id, payload.answer_text)
    return evaluation


@router.post("/{interview_id}/next-question", response_model=QuestionOut | None)
async def next_question(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    service = InterviewService(db)
    question = await service.generate_next_question(interview_id)
    if not question:
        raise HTTPException(status_code=400, detail="Interview is completed or question could not be generated.")
    return question


@router.post("/{interview_id}/complete", response_model=InterviewSummaryOut)
async def complete_interview(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    interview.status = InterviewStatus.COMPLETED
    await db.commit()

    service = InterviewService(db)
    summary = await service.generate_summary(interview_id)
    
    # Parse comma separated fields into lists for schema
    strong_list = [s.strip() for s in summary.strong_topics.split(",")] if summary.strong_topics else []
    weak_list = [s.strip() for s in summary.weak_topics.split(",")] if summary.weak_topics else []
    prog_list = [s.strip() for s in summary.difficulty_progression.split(",")] if summary.difficulty_progression else []
    gaps_list = [s.strip() for s in summary.knowledge_gaps.split(",")] if summary.knowledge_gaps else []
    sugg_list = [s.strip() for s in summary.improvement_suggestions.split(",")] if summary.improvement_suggestions else []

    return InterviewSummaryOut(
        overall_performance=summary.overall_performance,
        technical_performance=summary.technical_performance,
        strong_topics=strong_list,
        weak_topics=weak_list,
        average_score=summary.average_score,
        difficulty_progression=prog_list,
        knowledge_gaps=gaps_list,
        improvement_suggestions=sugg_list,
    )


@router.get("/{interview_id}/results", response_model=InterviewSummaryOut)
async def get_interview_results(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Summary for a completed interview (generates it from real records if missing)."""
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")

    service = InterviewService(db)
    if interview.summary is None:
        summary = await service.generate_summary(interview_id)
    else:
        summary = interview.summary

    strong_list = [s.strip() for s in summary.strong_topics.split(",")] if summary.strong_topics else []
    weak_list = [s.strip() for s in summary.weak_topics.split(",")] if summary.weak_topics else []
    prog_list = [s.strip() for s in summary.difficulty_progression.split(",")] if summary.difficulty_progression else []
    gaps_list = [s.strip() for s in summary.knowledge_gaps.split(",")] if summary.knowledge_gaps else []
    sugg_list = [s.strip() for s in summary.improvement_suggestions.split(",")] if summary.improvement_suggestions else []

    return InterviewSummaryOut(
        overall_performance=summary.overall_performance,
        technical_performance=summary.technical_performance,
        strong_topics=strong_list,
        weak_topics=weak_list,
        average_score=summary.average_score,
        difficulty_progression=prog_list,
        knowledge_gaps=gaps_list,
        improvement_suggestions=sugg_list,
    )


@router.post("/{interview_id}/cancel", response_model=InterviewOut)
async def cancel_interview(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    interview.status = InterviewStatus.CANCELLED
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("/{interview_id}/questions", response_model=List[QuestionOut])
async def get_interview_questions(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    result = await db.execute(select(InterviewQuestion).filter(InterviewQuestion.interview_id == interview_id))
    return result.scalars().all()


@router.get("/{interview_id}/answers", response_model=List[InterviewAnswerOut])
async def get_interview_answers(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    result = await db.execute(select(InterviewAnswer).filter(InterviewAnswer.interview_id == interview_id))
    return result.scalars().all()
