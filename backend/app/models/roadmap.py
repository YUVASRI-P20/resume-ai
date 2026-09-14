"""
Module 10 — Knowledge Graph + Learning Roadmap models.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class NodeStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    MASTERED = "Mastered"
    WEAK = "Weak"


class TaskPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    topic_name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. Java, Python, System Design
    mastery_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    status: Mapped[NodeStatus] = mapped_column(Enum(NodeStatus), default=NodeStatus.NOT_STARTED, nullable=False)
    is_strength: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_weakness: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False)
    child_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False)


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    total_weeks: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    weeks: Mapped[list["RoadmapWeek"]] = relationship(back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapWeek(Base):
    __tablename__ = "roadmap_weeks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)

    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    theme: Mapped[str] = mapped_column(String(200), nullable=False)
    objectives: Mapped[str] = mapped_column(Text, nullable=False)

    roadmap: Mapped["LearningRoadmap"] = relationship(back_populates="weeks")
    tasks: Mapped[list["RoadmapTask"]] = relationship(back_populates="week", cascade="all, delete-orphan")


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    week_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmap_weeks.id", ondelete="CASCADE"), nullable=False, index=True)

    day_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 7 within the week
    task_title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    study_time_hours: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), default="Medium", nullable=False)
    resources: Mapped[list | dict] = mapped_column(JSON, nullable=False)  # list of URLs or books
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    week: Mapped["RoadmapWeek"] = relationship(back_populates="tasks")


class LearningProgress(Base):
    __tablename__ = "learning_progresses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    total_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
