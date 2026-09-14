from fastapi import APIRouter
from app.resume.api.v1.endpoints import resumes, resume_analysis

router = APIRouter()
router.include_router(resumes.router)
router.include_router(resume_analysis.router)
