import uuid

from fastapi import APIRouter

from app.api.deps import get_current_user
from app.resume.database import SyncDbSession, get_sync_db
from fastapi import Depends
from app.resume.schemas.resume_analysis import (
    AnalyzeResumeRequest,
    CompanyMatchOut,
    CompanyMatchRequest,
    ResumeAnalysisOut,
    ResumeSuggestionOut,
)
from app.resume.services.resume_analysis_service import ResumeAnalysisService

router = APIRouter(prefix="/resumes", tags=["resume-analysis"])


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisOut)
def analyze_resume(resume_id: uuid.UUID, payload: AnalyzeResumeRequest, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    service = ResumeAnalysisService(db)
    return service.analyze_resume(resume_id, current_user.id, force_refresh=payload.force_refresh)


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisOut)
def get_analysis(resume_id: uuid.UUID, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    service = ResumeAnalysisService(db)
    return service.get_latest_analysis(resume_id, current_user.id)


@router.get("/{resume_id}/suggestions", response_model=list[ResumeSuggestionOut])
def get_suggestions(resume_id: uuid.UUID, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    service = ResumeAnalysisService(db)
    return service.get_suggestions(resume_id, current_user.id)


@router.post("/{resume_id}/company-match", response_model=CompanyMatchOut)
def create_company_match(resume_id: uuid.UUID, payload: CompanyMatchRequest, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    service = ResumeAnalysisService(db)
    return service.match_company(resume_id, current_user.id, payload.company_name, payload.target_role)


@router.get("/{resume_id}/company-match", response_model=list[CompanyMatchOut])
def list_company_matches(resume_id: uuid.UUID, current_user: object = Depends(get_current_user), db: SyncDbSession = Depends(get_sync_db)):
    service = ResumeAnalysisService(db)
    result = service.get_latest_company_match(resume_id, current_user.id)
    return result if isinstance(result, list) else [result]
