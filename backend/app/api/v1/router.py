"""Aggregates every versioned endpoint module under a single v1 router.

Future modules (resume analyzer, interview engine, etc.) register their
own routers here — see the "Adding a new module" note in the README.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, users, interviews, coding, feedback, roadmap, career
from app.resume.api.v1.router import router as resume_router
from app.api.v1.optimizer_readiness import router as optimizer_readiness_router
from app.api.v1.recruiter_notification import router as recruiter_notification_router

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(interviews.router)
api_router.include_router(coding.router)
api_router.include_router(feedback.router)
api_router.include_router(roadmap.router)
api_router.include_router(career.router)

api_router.include_router(resume_router)
api_router.include_router(optimizer_readiness_router)
api_router.include_router(recruiter_notification_router)
