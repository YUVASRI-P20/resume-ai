"""
API endpoints for Module 10: Knowledge Graph + Learning Roadmap.
"""
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.roadmap import (
    KnowledgeGraphOut,
    LearningRoadmapOut,
    RoadmapTaskOut,
    TaskUpdatePatch,
)
from app.services.roadmap_service import RoadmapService

router = APIRouter(tags=["knowledge-graph-roadmap"])


@router.get("/knowledge-graph/{user_id}", response_model=KnowledgeGraphOut)
async def get_knowledge_graph(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to user knowledge graph.")
    
    service = RoadmapService(db)
    graph_data = await service.get_knowledge_graph(user_id)
    return graph_data


@router.get("/roadmap/{user_id}", response_model=LearningRoadmapOut)
async def get_roadmap(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to user roadmap.")
    
    service = RoadmapService(db)
    roadmap = await service.generate_roadmap(user_id)
    return roadmap


@router.get("/interviews/{interview_id}/roadmap", response_model=LearningRoadmapOut)
async def get_interview_roadmap(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Personalized 15-day roadmap derived from this interview's results,
    the candidate's resume and the target job's requirement gaps."""
    from app.models.interview import Interview

    interview = await db.get(Interview, interview_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found.")

    service = RoadmapService(db)
    roadmap = await service.generate_roadmap(current_user.id, interview_id=interview.id)
    return roadmap


@router.post("/roadmap/generate", response_model=LearningRoadmapOut, status_code=status.HTTP_201_CREATED)
async def generate_roadmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = RoadmapService(db)
    roadmap = await service.generate_roadmap(current_user.id)
    return roadmap


@router.patch("/roadmap/tasks/{task_id}", response_model=RoadmapTaskOut)
async def update_roadmap_task(
    task_id: uuid.UUID,
    payload: TaskUpdatePatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = RoadmapService(db)
    task = await service.update_task_completion(task_id, current_user.id, payload.is_completed)
    return task


@router.post("/roadmap/regenerate", response_model=LearningRoadmapOut)
async def regenerate_roadmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = RoadmapService(db)
    roadmap = await service.regenerate_roadmap(current_user.id)
    return roadmap
