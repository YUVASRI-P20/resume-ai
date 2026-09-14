"""
Career module endpoints: company/role selection, evidence-based
resume-vs-role matching, streak, and the user dashboard aggregate.

Every route is scoped to the authenticated user — a user can only ever
read/write their own resumes, matches, streak and progress.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.company import Company, JobRole, RoleMatchResult, RoleRequirement
from app.models.feedback import KnowledgeGap
from app.models.interview import Interview, InterviewStatus
from app.models.roadmap import LearningProgress, LearningRoadmap, RoadmapTask, RoadmapWeek
from app.models.user import User
from app.resume.database import SyncSessionLocal
from app.schemas.career import (
    CompanyOut,
    DashboardOut,
    InterviewProgressOut,
    JobRoleOut,
    KnowledgeGapOut,
    ResumeSummaryOut,
    RoleMatchRequest,
    RoleMatchResultOut,
    RoleRequirementsOut,
    StreakOut,
)
from app.services.role_match_service import compute_role_match
from app.services.streak_service import get_streak

router = APIRouter(tags=["career"])


# ---------------- Companies & Job Roles ---------------- #
@router.get("/companies", response_model=list[CompanyOut])
async def list_companies(db: AsyncSession = Depends(get_db), _u: User = Depends(get_current_active_user)):
    result = await db.execute(select(Company).where(Company.is_active.is_(True)).order_by(Company.name))
    return result.scalars().all()


@router.get("/companies/{company_id}/roles", response_model=list[JobRoleOut])
async def list_company_roles(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _u: User = Depends(get_current_active_user),
):
    company = await db.get(Company, company_id)
    if company is None or not company.is_active:
        raise HTTPException(status_code=404, detail="Company not found.")
    result = await db.execute(
        select(JobRole).where(JobRole.company_id == company_id, JobRole.is_active.is_(True)).order_by(JobRole.title)
    )
    return result.scalars().all()


@router.get("/job-roles/{job_role_id}", response_model=RoleRequirementsOut)
async def get_role_requirements(
    job_role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _u: User = Depends(get_current_active_user),
):
    role = await db.get(JobRole, job_role_id)
    if role is None or not role.is_active:
        raise HTTPException(status_code=404, detail="Job role not found.")
    company = await db.get(Company, role.company_id)
    reqs = (
        await db.execute(
            select(RoleRequirement)
            .where(RoleRequirement.job_role_id == role.id)
            .order_by(RoleRequirement.importance.desc())
        )
    ).scalars().all()
    return RoleRequirementsOut(
        role=JobRoleOut.model_validate(role),
        company=CompanyOut.model_validate(company),
        requirements=[
            {"requirement": r.requirement, "category": r.category.value, "importance": r.importance}
            for r in reqs
        ],
    )


# ---------------- Evidence-based match ---------------- #
@router.post("/resumes/{resume_id}/role-match", response_model=RoleMatchResultOut)
async def create_role_match(
    resume_id: uuid.UUID,
    payload: RoleMatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Compare the user's ACTUAL uploaded resume against the selected
    company's job role requirements with per-requirement evidence."""
    # The match engine uses the synchronous resume module session.
    sync_db = SyncSessionLocal()
    try:
        result = compute_role_match(
            sync_db,
            resume_id=resume_id,
            user_id=current_user.id,
            company_id=payload.company_id,
            job_role_id=payload.job_role_id,
        )
        db.commit()  # no-op flush of the async session state, keeps deps happy
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        sync_db.close()


@router.get("/resumes/{resume_id}/role-match", response_model=list[RoleMatchResultOut])
async def list_role_matches(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(RoleMatchResult)
        .where(RoleMatchResult.resume_id == resume_id, RoleMatchResult.user_id == current_user.id)
        .order_by(RoleMatchResult.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()


# ---------------- Streak ---------------- #
@router.get("/streak", response_model=StreakOut)
async def get_my_streak(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await get_streak(db, current_user.id)


# ---------------- Dashboard aggregate ---------------- #
@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user_id = current_user.id

    # Latest active resume
    from app.resume.models.resume import Resume

    resume_row = (
        await db.execute(
            select(Resume)
            .where(Resume.user_id == user_id, Resume.is_active.is_(True))
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    resume_summary = None
    if resume_row:
        resume_summary = ResumeSummaryOut(
            id=resume_row.id,
            original_filename=resume_row.original_filename,
            status=resume_row.status.value,
            uploaded_at=resume_row.created_at,
        )

    # Latest role match (latest across the user's resumes)
    match = (
        await db.execute(
            select(RoleMatchResult)
            .where(RoleMatchResult.user_id == user_id)
            .order_by(RoleMatchResult.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    selected_company = selected_role = None
    match_pct = None
    strong: list[str] = []
    weak: list[str] = []
    if match:
        company = await db.get(Company, match.company_id)
        role = await db.get(JobRole, match.job_role_id)
        selected_company = company.name if company else None
        selected_role = role.title if role else None
        match_pct = match.match_percentage
        strong = list(match.strong_areas or [])
        weak = list(match.weak_areas or [])

    # Interview progress
    interviews = (
        await db.execute(select(Interview).where(Interview.user_id == user_id))
    ).scalars().all()
    completed = [i for i in interviews if i.status == InterviewStatus.COMPLETED]
    in_progress = [i for i in interviews if i.status == InterviewStatus.IN_PROGRESS]
    last_score = None
    # Real last score from feedback if available
    from app.models.feedback import InterviewFeedback

    feedback = (
        await db.execute(
            select(InterviewFeedback)
            .where(InterviewFeedback.user_id == user_id)
            .order_by(InterviewFeedback.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if feedback:
        last_score = float(feedback.overall_score)

    # Knowledge gaps
    gaps_rows = (
        await db.execute(
            select(KnowledgeGap).where(KnowledgeGap.user_id == user_id).order_by(KnowledgeGap.created_at.desc()).limit(10)
        )
    ).scalars().all()
    knowledge_gaps = [KnowledgeGapOut(topic=g.topic, description=g.description) for g in gaps_rows]

    # Roadmap progress
    roadmap_progress = None
    progress = (
        await db.execute(select(LearningProgress).where(LearningProgress.user_id == user_id).limit(1))
    ).scalar_one_or_none()
    if progress and progress.total_tasks:
        roadmap_progress = round(progress.completed_tasks / progress.total_tasks * 100.0, 1)

    streak = await get_streak(db, user_id)

    return DashboardOut(
        user_name=current_user.full_name,
        email=current_user.email,
        streak=StreakOut(**streak),
        resume=resume_summary,
        selected_company=selected_company,
        selected_role=selected_role,
        match_percentage=match_pct,
        strong_areas=strong,
        weak_areas=weak,
        interview_progress=InterviewProgressOut(
            total=len(interviews),
            completed=len(completed),
            in_progress=len(in_progress),
            last_score=last_score,
        ),
        knowledge_gaps=knowledge_gaps,
        roadmap_progress=roadmap_progress,
    )
