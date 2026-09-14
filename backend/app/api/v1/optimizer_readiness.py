from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.schemas.optimizer_readiness import (
    ResumeOptimizeRequest,
    ResumeOptimizationResponse,
    ResumeVersionResponse,
    ReadinessAnalyzeRequest,
    InterviewReadinessResponse
)
from app.models.optimizer_readiness import ResumeOptimization, ResumeVersion, InterviewReadinessReport
from app.services.ai_optimizer_readiness_service import AIOptimizerReadinessService

router = APIRouter(tags=["Optimizer & Readiness"])

from fastapi import Depends
from app.resume.database import get_sync_db
from app.api.deps import get_current_user as root_get_current_user
from app.resume.models.resume import Resume

async def get_current_user(token=None, user=Depends(root_get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role.name if user.role else "STUDENT"}

def get_db():
    yield from get_sync_db()

# --- Module 5 Endpoints ---

@router.post("/resumes/{resume_id}/optimize", response_model=ResumeOptimizationResponse)
def optimize_resume(
    resume_id: str,
    payload: ResumeOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume ID format.")

    resume = db.query(Resume).filter(
        Resume.id == resume_uuid,
        Resume.user_id == current_user["id"],
        Resume.is_active.is_(True),
    ).first()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    resume_text = resume.raw_text or ""
    if not resume_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume has no extractable text to optimize.")

    try:
        analysis = AIOptimizerReadinessService.optimize_resume(
            resume_text=resume_text,
            target_role=payload.target_role,
            target_company=payload.target_company,
            job_description=payload.job_description
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    optimization_id = str(uuid.uuid4())
    user_id = current_user["id"]

    # Save to database
    db_opt = ResumeOptimization(
        id=uuid.UUID(optimization_id),
        resume_id=resume_uuid,
        user_id=user_id,
        target_role=payload.target_role,
        target_company=payload.target_company,
        job_description=payload.job_description,
        overall_score=analysis.get("overall_score", 80.0),
        ats_score=analysis.get("ats_score", 80.0),
        role_match_score=analysis.get("role_match_score", 80.0),
        summary_optimization=analysis.get("summary_optimization"),
        experience_optimizations=analysis.get("experience_optimizations"),
        project_optimizations=analysis.get("project_optimizations"),
        skill_optimization=analysis.get("skill_optimization"),
        ats_analysis=analysis.get("ats_analysis"),
        company_match=analysis.get("company_match"),
        improvement_report=analysis.get("improvement_report")
    )
    db.add(db_opt)

    # Save version history
    db_version = ResumeVersion(
        resume_id=resume_uuid,
        user_id=user_id,
        version_number=1,
        original_content=resume_text,
        optimized_content=str(analysis.get("summary_optimization", {}).get("optimized", "")),
        changes_summary={"summary": analysis.get("summary_optimization")}
    )
    db.add(db_version)
    db.commit()

    return ResumeOptimizationResponse(
        optimization_id=optimization_id,
        resume_id=str(resume_uuid),
        user_id=str(user_id),
        target_role=payload.target_role,
        target_company=payload.target_company,
        overall_score=analysis.get("overall_score", 80.0),
        ats_score=analysis.get("ats_score", 80.0),
        role_match_score=analysis.get("role_match_score", 80.0),
        summary_optimization=analysis.get("summary_optimization"),
        experience_optimizations=analysis.get("experience_optimizations", []),
        project_optimizations=analysis.get("project_optimizations", []),
        skill_optimization=analysis.get("skill_optimization", {}),
        ats_analysis=analysis.get("ats_analysis", {}),
        company_match=analysis.get("company_match"),
        improvement_report=analysis.get("improvement_report", {}),
        created_at=datetime.utcnow().isoformat()
    )


@router.get("/resumes/{resume_id}/optimized", response_model=List[ResumeOptimizationResponse])
def get_optimized_resumes(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume ID format.")

    optimizations = db.query(ResumeOptimization).filter(
        ResumeOptimization.resume_id == resume_uuid,
        ResumeOptimization.user_id == current_user["id"],
    ).all()
    
    results = []
    for opt in optimizations:
        results.append(ResumeOptimizationResponse(
            optimization_id=str(opt.id),
            resume_id=str(opt.resume_id),
            user_id=str(opt.user_id),
            target_role=opt.target_role,
            target_company=opt.target_company,
            overall_score=opt.overall_score,
            ats_score=opt.ats_score,
            role_match_score=opt.role_match_score,
            summary_optimization=opt.summary_optimization,
            experience_optimizations=opt.experience_optimizations,
            project_optimizations=opt.project_optimizations,
            skill_optimization=opt.skill_optimization,
            ats_analysis=opt.ats_analysis,
            company_match=opt.company_match,
            improvement_report=opt.improvement_report,
            created_at=opt.created_at.isoformat() if opt.created_at else datetime.utcnow().isoformat()
        ))
    return results


@router.get("/resumes/{resume_id}/versions", response_model=List[ResumeVersionResponse])
def get_resume_versions(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume ID format.")

    versions = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == resume_uuid,
        ResumeVersion.user_id == current_user["id"],
    ).all()
    results = []
    for v in versions:
        results.append(ResumeVersionResponse(
            version_id=str(v.id),
            resume_id=str(v.resume_id),
            version_number=v.version_number,
            original_content=v.original_content,
            optimized_content=v.optimized_content,
            changes_summary=v.changes_summary or {},
            created_at=v.created_at.isoformat() if v.created_at else datetime.utcnow().isoformat()
        ))
    return results


@router.post("/resumes/{resume_id}/versions/{version_id}/restore")
def restore_resume_version(
    resume_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        v_uuid = uuid.UUID(version_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid version ID format.")

    version = db.query(ResumeVersion).filter(
        ResumeVersion.id == v_uuid,
        ResumeVersion.user_id == current_user["id"],
    ).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")

    return {
        "message": "Resume version successfully restored.",
        "version_id": version_id,
        "resume_id": resume_id,
        "restored_content": version.optimized_content
    }


# --- Module 6 Endpoints ---

@router.post("/readiness/analyze", response_model=InterviewReadinessResponse)
def analyze_readiness(
    payload: ReadinessAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    resume_text = "No resume content provided."
    if payload.resume_id:
        try:
            resume_uuid = uuid.UUID(payload.resume_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume ID format.")
        resume = db.query(Resume).filter(
            Resume.id == resume_uuid,
            Resume.user_id == current_user["id"],
            Resume.is_active.is_(True),
        ).first()
        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
        resume_text = resume.raw_text or resume_text

    try:
        analysis = AIOptimizerReadinessService.analyze_readiness(
            resume_text=resume_text,
            target_role=payload.target_role,
            target_company=payload.target_company,
            job_description=payload.job_description
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    report_id = str(uuid.uuid4())
    user_id = current_user["id"]

    db_report = InterviewReadinessReport(
        id=uuid.UUID(report_id),
        user_id=user_id,
        resume_id=uuid.UUID(payload.resume_id) if payload.resume_id else None,
        target_role=payload.target_role,
        target_company=payload.target_company,
        job_description=payload.job_description,
        overall_readiness_score=analysis.get("overall_readiness_score", 75.0),
        confidence_level=analysis.get("confidence_level", "Moderate"),
        technical_readiness=analysis.get("technical_readiness"),
        coding_readiness=analysis.get("coding_readiness"),
        communication_readiness=analysis.get("communication_readiness"),
        resume_readiness=analysis.get("resume_readiness"),
        project_readiness=analysis.get("project_readiness"),
        strong_areas=analysis.get("strong_areas"),
        weak_areas=analysis.get("weak_areas"),
        missing_evidence=analysis.get("missing_evidence"),
        knowledge_gaps=analysis.get("knowledge_gaps"),
        recommended_topics=analysis.get("recommended_topics"),
        action_plan=analysis.get("action_plan"),
        company_readiness_scores=analysis.get("company_readiness_scores"),
        career_insights=analysis.get("career_insights")
    )
    db.add(db_report)
    db.commit()

    return InterviewReadinessResponse(
        report_id=report_id,
        user_id=str(user_id),
        target_role=payload.target_role,
        target_company=payload.target_company,
        overall_readiness_score=analysis.get("overall_readiness_score", 75.0),
        confidence_level=analysis.get("confidence_level", "Moderate"),
        technical_readiness=analysis.get("technical_readiness", {}),
        coding_readiness=analysis.get("coding_readiness", {}),
        communication_readiness=analysis.get("communication_readiness", {}),
        resume_readiness=analysis.get("resume_readiness", {}),
        project_readiness=analysis.get("project_readiness", {}),
        strong_areas=analysis.get("strong_areas", []),
        weak_areas=analysis.get("weak_areas", []),
        missing_evidence=analysis.get("missing_evidence", []),
        knowledge_gaps=analysis.get("knowledge_gaps", {}),
        recommended_topics=analysis.get("recommended_topics", []),
        action_plan=analysis.get("action_plan", []),
        company_readiness_scores=analysis.get("company_readiness_scores", []),
        career_insights=analysis.get("career_insights", []),
        created_at=datetime.utcnow().isoformat()
    )


@router.get("/readiness/{user_id}", response_model=List[InterviewReadinessResponse])
def get_user_readiness_reports(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format.")

    reports = db.query(InterviewReadinessReport).filter(InterviewReadinessReport.user_id == u_uuid).all()
    results = []
    for r in reports:
        results.append(InterviewReadinessResponse(
            report_id=str(r.id),
            user_id=str(r.user_id),
            target_role=r.target_role,
            target_company=r.target_company,
            overall_readiness_score=r.overall_readiness_score,
            confidence_level=r.confidence_level,
            technical_readiness=r.technical_readiness,
            coding_readiness=r.coding_readiness,
            communication_readiness=r.communication_readiness,
            resume_readiness=r.resume_readiness,
            project_readiness=r.project_readiness,
            strong_areas=r.strong_areas,
            weak_areas=r.weak_areas,
            missing_evidence=r.missing_evidence,
            knowledge_gaps=r.knowledge_gaps,
            recommended_topics=r.recommended_topics,
            action_plan=r.action_plan,
            company_readiness_scores=r.company_readiness_scores,
            career_insights=r.career_insights,
            created_at=r.created_at.isoformat() if r.created_at else datetime.utcnow().isoformat()
        ))
    return results


@router.get("/career-insights/{user_id}")
def get_career_insights(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format.")

    report = db.query(InterviewReadinessReport).filter(InterviewReadinessReport.user_id == u_uuid).order_by(InterviewReadinessReport.created_at.desc()).first()
    if not report:
        return {"user_id": user_id, "career_insights": ["Complete a readiness analysis to receive personalized career insights."]}
    
    return {
        "user_id": user_id,
        "target_role": report.target_role,
        "career_insights": report.career_insights
    }


@router.get("/action-plan/{user_id}")
def get_action_plan(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format.")

    report = db.query(InterviewReadinessReport).filter(InterviewReadinessReport.user_id == u_uuid).order_by(InterviewReadinessReport.created_at.desc()).first()
    if not report:
        return {"user_id": user_id, "action_plan": []}

    return {
        "user_id": user_id,
        "target_role": report.target_role,
        "action_plan": report.action_plan
    }
