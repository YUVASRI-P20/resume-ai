"""
Pydantic schemas for Module 10 (Knowledge Graph + Learning Roadmap).
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.roadmap import NodeStatus, TaskPriority


class KnowledgeNodeOut(BaseModel):
    id: str
    topic_name: str
    category: str
    mastery_score: float
    status: str
    is_strength: bool
    is_weakness: bool


class KnowledgeEdgeOut(BaseModel):
    id: str
    parent_node_id: str
    child_node_id: str


class KnowledgeGraphOut(BaseModel):
    nodes: List[KnowledgeNodeOut]
    edges: List[KnowledgeEdgeOut]


class RoadmapTaskOut(BaseModel):
    id: uuid.UUID
    day_number: int
    task_title: str
    description: str
    study_time_hours: float
    priority: TaskPriority
    difficulty: str
    resources: List[Any]
    is_completed: bool

    class Config:
        from_attributes = True


class RoadmapWeekOut(BaseModel):
    id: uuid.UUID
    week_number: int
    theme: str
    objectives: str
    tasks: List[RoadmapTaskOut] = []

    class Config:
        from_attributes = True


class LearningRoadmapOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    summary: str
    total_weeks: int
    completion_percentage: float
    created_at: datetime
    weeks: List[RoadmapWeekOut] = []

    class Config:
        from_attributes = True


class TaskUpdatePatch(BaseModel):
    is_completed: bool
