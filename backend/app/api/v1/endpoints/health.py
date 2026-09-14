"""Liveness/readiness check. Kept dependency-free from the DB so it
reflects "is the process up" — swap in a DB ping here if you want a
true readiness probe instead."""
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check")
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
