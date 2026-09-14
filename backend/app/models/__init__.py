"""
Import every model here so app.database.base.Base.metadata is fully
populated wherever this package is imported — this is what Alembic's
autogenerate and Base.metadata.create_all() rely on.
"""
from app.models.role import Role, RoleName  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.interview import (  # noqa: F401
    Interview,
    InterviewQuestion,
    InterviewAnswer,
    InterviewEvaluation,
    InterviewSummary,
    InterviewStatus,
    InterviewType,
    InterviewDifficulty,
)
from app.models.coding import (  # noqa: F401
    CodingQuestion,
    CodingTestCase,
    CodingSubmission,
    CodeExecution,
    CodeReview,
    CodingDifficulty,
    SubmissionStatus,
)
from app.models.feedback import (  # noqa: F401
    InterviewFeedback,
    FeedbackCategory,
    KnowledgeGap,
    Strength,
    Weakness,
    HallucinationFinding,
    FeedbackSeverity,
)
from app.models.roadmap import (  # noqa: F401
    KnowledgeNode,
    KnowledgeEdge,
    LearningRoadmap,
    RoadmapWeek,
    RoadmapTask,
    LearningProgress,
    NodeStatus,
    TaskPriority,
)
from app.models.company import (  # noqa: F401
    Company,
    JobRole,
    RoleRequirement,
    RoleMatchResult,
    RequirementCategory,
    MatchStatus,
)
from app.models.streak import LoginEvent, UserStreak  # noqa: F401

__all__ = [
    "Role",
    "RoleName",
    "User",
    "RefreshToken",
    "Interview",
    "InterviewQuestion",
    "InterviewAnswer",
    "InterviewEvaluation",
    "InterviewSummary",
    "InterviewStatus",
    "InterviewType",
    "InterviewDifficulty",
    "CodingQuestion",
    "CodingTestCase",
    "CodingSubmission",
    "CodeExecution",
    "CodeReview",
    "CodingDifficulty",
    "SubmissionStatus",
    "Company",
    "JobRole",
    "RoleRequirement",
    "RoleMatchResult",
    "LoginEvent",
    "UserStreak",
]

from app.resume.models import *  # noqa: F401,F403
from app.models.optimizer_readiness import ResumeOptimization, ResumeVersion, InterviewReadinessReport  # noqa: F401
from app.models.recruiter_notification import Notification, RecruiterReport  # noqa: F401
