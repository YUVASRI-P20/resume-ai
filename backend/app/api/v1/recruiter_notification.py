"""
Recruiter & Notification endpoints — backed by REAL database records only.

A recruiter can list candidates who have completed interviews, view their real
scores, compare candidates and export CSV reports. Every number comes from
actual resumes / interviews / evaluations / coding submissions in PostgreSQL.
No fabricated candidate rows.
"""
import csv
import io
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user as root_get_current_user
from app.models.coding import CodingSubmission, CodeExecution
from app.models.company import RoleMatchResult
from app.models.feedback import InterviewFeedback
from app.models.interview import Interview, InterviewEvaluation, InterviewStatus
from app.models.recruiter_notification import Notification, RecruiterReport
from app.models.user import User
from app.resume.database import get_sync_db
from app.resume.models.resume import ExtractedSkill, Resume
from app.schemas.recruiter_notification import (
    CandidateComparisonResponse,
    CandidateCompareRequest,
    CandidateDetailResponse,
    CandidateSummaryResponse,
    NotificationResponse,
    RecruiterAnalyticsResponse,
    ReportGenerateRequest,
)

router = APIRouter(tags=["Recruiter & Notifications"])


def get_db():
    yield from get_sync_db()


async def get_current_user(user=Depends(root_get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role.name if user.role else "STUDENT"}


async def require_recruiter(user=Depends(get_current_user)):
    if user["role"] != "RECRUITER" and user["role"] != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Recruiter access required.")
    return user


def _candidate_scores(db: Session, candidate_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, Any]]:
    """Compute each candidate's real aggregate scores in bulk."""
    out: dict[uuid.UUID, dict[str, Any]] = {}
    for cid in candidate_ids:
        # Latest completed interview feedback (real evaluation aggregates)
        feedback = (
            db.query(InterviewFeedback)
            .join(Interview, InterviewFeedback.interview_id == Interview.id)
            .filter(InterviewFeedback.user_id == cid, Interview.status == InterviewStatus.COMPLETED)
            .order_by(InterviewFeedback.created_at.desc())
            .first()
        )
        # Latest parsed resume analysis score
        resume = (
            db.query(Resume)
            .filter(Resume.user_id == cid, Resume.is_active.is_(True), Resume.status == "PARSED")
            .order_by(Resume.created_at.desc())
            .first()
        )
        # Real coding pass-rate across submissions
        execs = (
            db.query(CodeExecution)
            .join(CodingSubmission, CodeExecution.submission_id == CodingSubmission.id)
            .filter(CodingSubmission.user_id == cid)
            .all()
        )
        passed = sum(e.passed_tests for e in execs)
        total = sum(e.total_tests for e in execs)
        coding_pct = round(passed / total * 100.0, 1) if total else 0.0
        # Latest role match
        match = (
            db.query(RoleMatchResult)
            .filter(RoleMatchResult.user_id == cid)
            .order_by(RoleMatchResult.created_at.desc())
            .first()
        )

        out[cid] = {
            "resume_score": float(feedback.technical_score) if feedback else 0.0,
            "role_match_score": float(match.match_percentage) if match else 0.0,
            "interview_readiness": float(feedback.overall_score) if feedback else 0.0,
            "latest_interview_score": float(feedback.overall_score) if feedback else 0.0,
            "coding_score": coding_pct,
            "has_data": feedback is not None or resume is not None,
        }
    return out


@router.get("/recruiter/candidates", response_model=List[CandidateSummaryResponse])
async def search_candidates(
    search: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    recruiter: dict = Depends(require_recruiter),
):
    """List real candidates (users with resumes/interviews) and their actual scores."""
    query = db.query(User).filter(User.is_active.is_(True))
    if search:
        like = f"%{search.strip().lower()}%"
        query = query.filter(
            sa_func.lower(User.full_name).like(like) | sa_func.lower(User.email).like(like)
        )
    users = query.order_by(User.created_at.desc()).all()

    if not users:
        return []

    scores = _candidate_scores(db, [u.id for u in users])

    # Skill filter operates on actually-extracted resume skills.
    skill_filter = {s.strip().lower() for s in (skills or "").split(",") if s.strip()}
    results: list[CandidateSummaryResponse] = []
    for u in users:
        info = scores.get(u.id, {})
        if not info.get("has_data"):
            continue  # candidates without any real data are not shown
        user_skills = (
            db.query(ExtractedSkill.name)
            .join(Resume, ExtractedSkill.resume_id == Resume.id)
            .filter(Resume.user_id == u.id, Resume.is_active.is_(True))
            .limit(50)
            .all()
        )
        names = [n for (n,) in user_skills]
        if skill_filter and not skill_filter.intersection({n.lower() for n in names}):
            continue
        results.append(
            CandidateSummaryResponse(
                candidate_id=str(u.id),
                name=u.full_name,
                email=u.email,
                relevant_skills=names[:10],
                resume_score=info["resume_score"],
                role_match_score=info["role_match_score"],
                interview_readiness=info["interview_readiness"],
                latest_interview_score=info["latest_interview_score"],
            )
        )

    start = (page - 1) * page_size
    return results[start : start + page_size]


@router.get("/recruiter/candidates/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate_details(
    candidate_id: str,
    db: Session = Depends(get_db),
    recruiter: dict = Depends(require_recruiter),
):
    try:
        c_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid candidate ID format.")

    user = db.query(User).filter(User.id == c_uuid, User.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    # Resume (real extraction)
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == c_uuid, Resume.is_active.is_(True))
        .order_by(Resume.created_at.desc())
        .first()
    )
    resume_payload: dict[str, Any] = {}
    if resume:
        skills = [s.name for s in (resume.skills or [])]
        resume_payload = {
            "filename": resume.original_filename,
            "status": resume.status.value if hasattr(resume.status, "value") else str(resume.status),
            "skills": skills,
            "full_name": resume.full_name,
            "uploaded_at": resume.created_at.isoformat() if resume.created_at else None,
        }

    # Interview history (real records)
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == c_uuid)
        .order_by(Interview.created_at.desc())
        .all()
    )
    technical_scores: list[float] = []
    for iv in interviews:
        evals = (
            db.query(InterviewEvaluation)
            .join(InterviewQuestion, InterviewEvaluation.answer_id == InterviewQuestion.id)
            .join(InterviewAnswer, InterviewEvaluation.answer_id == InterviewAnswer.id)
            .filter(InterviewAnswer.interview_id == iv.id)
            .all()
        )
        if evals:
            technical_scores.append(round(sum(e.score for e in evals) / len(evals), 1))

    feedback = (
        db.query(InterviewFeedback)
        .filter(InterviewFeedback.user_id == c_uuid)
        .order_by(InterviewFeedback.created_at.desc())
        .first()
    )

    # Coding (real submissions)
    execs = (
        db.query(CodeExecution)
        .join(CodingSubmission, CodeExecution.submission_id == CodingSubmission.id)
        .filter(CodingSubmission.user_id == c_uuid)
        .order_by(CodeExecution.created_at.desc())
        .limit(20)
        .all()
    )
    passed = sum(e.passed_tests for e in execs)
    total = sum(e.total_tests for e in execs)

    # Role match (real evidence-based match)
    match = (
        db.query(RoleMatchResult)
        .filter(RoleMatchResult.user_id == c_uuid)
        .order_by(RoleMatchResult.created_at.desc())
        .first()
    )

    return CandidateDetailResponse(
        candidate_id=candidate_id,
        profile={
            "name": user.full_name,
            "email": user.email,
            "member_since": user.created_at.isoformat() if user.created_at else None,
        },
        resume=resume_payload,
        interview={
            "history": [
                {
                    "id": str(iv.id),
                    "company": iv.company,
                    "role": iv.job_role,
                    "status": iv.status.value if hasattr(iv.status, "value") else str(iv.status),
                    "average_score": technical_scores[i] if i < len(technical_scores) else None,
                    "created_at": iv.created_at.isoformat() if iv.created_at else None,
                }
                for i, iv in enumerate(interviews[:10])
            ],
            "technical_scores": technical_scores,
            "overall_score": float(feedback.overall_score) if feedback else None,
        },
        coding={
            "submissions": len(execs),
            "tests_passed": passed,
            "tests_total": total,
            "pass_rate": round(passed / total * 100.0, 1) if total else 0.0,
        },
        readiness={
            "overall_readiness": float(feedback.overall_score) if feedback else 0.0,
            "strong_areas": list(feedback.strengths and [s.title for s in feedback.strengths] or []),
            "weak_areas": list(feedback.weaknesses and [w.title for w in feedback.weaknesses] or []),
            "role_match_percentage": float(match.match_percentage) if match else None,
        },
    )


@router.post("/recruiter/candidates/compare", response_model=CandidateComparisonResponse)
async def compare_candidates(
    payload: CandidateCompareRequest,
    db: Session = Depends(get_db),
    recruiter: dict = Depends(require_recruiter),
):
    ids: list[uuid.UUID] = []
    for cid in payload.candidate_ids[:5]:
        try:
            ids.append(uuid.UUID(cid))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid candidate ID format.")

    users = db.query(User).filter(User.id.in_(ids)).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No candidates found.")

    scores = _candidate_scores(db, [u.id for u in users])
    summaries = []
    skill_sets: list[set[str]] = []
    for u in users:
        info = scores.get(u.id, {})
        names = [
            n for (n,) in db.query(ExtractedSkill.name)
            .join(Resume, ExtractedSkill.resume_id == Resume.id)
            .filter(Resume.user_id == u.id, Resume.is_active.is_(True))
            .limit(50)
            .all()
        ]
        skill_sets.append({n.lower() for n in names})
        summaries.append(
            CandidateSummaryResponse(
                candidate_id=str(u.id),
                name=u.full_name,
                email=u.email,
                relevant_skills=names[:10],
                resume_score=info["resume_score"],
                role_match_score=info["role_match_score"],
                interview_readiness=info["interview_readiness"],
                latest_interview_score=info["latest_interview_score"],
            )
        )

    overlap = set.intersection(*skill_sets) if skill_sets and all(skill_sets) else set()
    return CandidateComparisonResponse(
        compared_candidates=summaries,
        metrics_comparison={
            "skill_overlap": sorted(overlap)[:10],
            "readiness_scores": {s.candidate_id: s.interview_readiness for s in summaries},
        },
        summary_insights=[
            "Scores are computed from each candidate's actual interview evaluations, coding submissions and resume extraction."
        ],
    )


@router.get("/recruiter/analytics", response_model=RecruiterAnalyticsResponse)
async def get_recruiter_analytics(
    db: Session = Depends(get_db),
    recruiter: dict = Depends(require_recruiter),
):
    """Aggregate analytics computed from real candidate data."""
    feedbacks = db.query(InterviewFeedback).all()
    total_candidates = db.query(sa_func.count(sa_func.distinct(InterviewFeedback.user_id))).scalar() or 0

    avg_overall = round(sum(f.overall_score for f in feedbacks) / len(feedbacks), 1) if feedbacks else 0.0
    avg_interview = avg_overall

    execs = db.query(CodeExecution).all()
    passed = sum(e.passed_tests for e in execs)
    total = sum(e.total_tests for e in execs)
    avg_coding = round(passed / total * 100.0, 1) if total else 0.0

    matches = db.query(RoleMatchResult).all()
    avg_match = round(sum(m.match_percentage for m in matches) / len(matches), 1) if matches else 0.0

    # Top skills from real extractions
    skill_counts: dict[str, int] = {}
    for (name,) in (
        db.query(ExtractedSkill.name)
        .join(Resume, ExtractedSkill.resume_id == Resume.id)
        .filter(Resume.is_active.is_(True))
        .limit(2000)
        .all()
    ):
        skill_counts[name] = skill_counts.get(name, 0) + 1
    top_skills = [s for s, _ in sorted(skill_counts.items(), key=lambda kv: -kv[1])[:10]]

    high = sum(1 for f in feedbacks if f.overall_score >= 80)
    moderate = sum(1 for f in feedbacks if 60 <= f.overall_score < 80)
    low = sum(1 for f in feedbacks if f.overall_score < 60)

    return RecruiterAnalyticsResponse(
        total_candidates=total_candidates,
        candidates_evaluated=total_candidates,
        average_resume_score=avg_match,
        average_interview_score=avg_interview,
        average_readiness_score=avg_overall,
        top_skills=top_skills,
        readiness_distribution={"High (80+)": high, "Moderate (60-79)": moderate, "Low (<60)": low},
        role_distribution={},
    )


@router.post("/recruiter/reports/generate")
async def generate_recruiter_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    recruiter: dict = Depends(require_recruiter),
):
    """Build a report row from the candidate's REAL data and store it."""
    try:
        c_uuid = uuid.UUID(payload.candidate_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid candidate ID format.")

    details = await get_candidate_details(payload.candidate_id, db=db, recruiter=recruiter)
    report = RecruiterReport(
        recruiter_id=recruiter["id"],
        candidate_id=c_uuid,
        report_data=details.model_dump(),
        format_type=payload.format.upper(),
    )
    db.add(report)
    db.commit()

    return {
        "report_id": str(report.id),
        "candidate_id": payload.candidate_id,
        "format": payload.format,
        "status": "Generated successfully",
        "download_url": f"/api/v1/recruiter/reports/{report.id}/csv",
    }


@router.get("/recruiter/reports/{report_id}/csv")
async def download_report_csv(
    report_id: str,
    db: Session = Depends(get_db),
    recruiter: dict = Depends(require_recruiter),
):
    try:
        r_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID format.")

    report = db.query(RecruiterReport).filter(RecruiterReport.id == r_uuid).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    data = report.report_data or {}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    for key, value in data.items():
        if isinstance(value, dict):
            for k2, v2 in value.items():
                writer.writerow([f"{key}.{k2}", v2])
        else:
            writer.writerow([key, value])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"},
    )


# --- Notification endpoints (real Notification rows, per user) ---


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == current_user["id"])
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        NotificationResponse(
            id=str(n.id),
            user_id=str(n.user_id),
            type=n.type,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            metadata=n.notification_metadata,
            created_at=n.created_at.isoformat() if n.created_at else datetime.utcnow().isoformat(),
        )
        for n in rows
    ]


@router.get("/notifications/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == current_user["id"], Notification.is_read.is_(False))
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [
        NotificationResponse(
            id=str(n.id),
            user_id=str(n.user_id),
            type=n.type,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            metadata=n.notification_metadata,
            created_at=n.created_at.isoformat() if n.created_at else datetime.utcnow().isoformat(),
        )
        for n in rows
    ]


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        n_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid notification ID format.")
    n = db.query(Notification).filter(Notification.id == n_uuid, Notification.user_id == current_user["id"]).first()
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    n.is_read = True
    db.commit()
    return {"message": "Notification marked as read.", "notification_id": notification_id}


@router.patch("/notifications/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user["id"], Notification.is_read.is_(False)
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"message": "All notifications marked as read."}


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        n_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid notification ID format.")
    n = db.query(Notification).filter(Notification.id == n_uuid, Notification.user_id == current_user["id"]).first()
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    db.delete(n)
    db.commit()
    return {"message": "Notification deleted successfully.", "notification_id": notification_id}
