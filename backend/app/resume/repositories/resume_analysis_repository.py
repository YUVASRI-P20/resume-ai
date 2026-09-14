import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.resume.models.resume_analysis import CompanyMatch, ResumeAnalysis
from app.resume.repositories.base import BaseRepository


class ResumeAnalysisRepository(BaseRepository[ResumeAnalysis]):
    model = ResumeAnalysis

    def __init__(self, db: Session):
        super().__init__(db)

    def get_with_details(self, analysis_id: uuid.UUID) -> ResumeAnalysis | None:
        stmt = (
            select(ResumeAnalysis)
            .where(ResumeAnalysis.id == analysis_id)
            .options(
                selectinload(ResumeAnalysis.section_scores),
                selectinload(ResumeAnalysis.suggestions),
                selectinload(ResumeAnalysis.keywords),
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_latest_for_resume(self, resume_id: uuid.UUID) -> ResumeAnalysis | None:
        stmt = (
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == resume_id)
            .options(
                selectinload(ResumeAnalysis.section_scores),
                selectinload(ResumeAnalysis.suggestions),
                selectinload(ResumeAnalysis.keywords),
            )
            .order_by(ResumeAnalysis.created_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_history_for_resume(self, resume_id: uuid.UUID, limit: int = 20) -> list[ResumeAnalysis]:
        stmt = (
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == resume_id)
            .order_by(ResumeAnalysis.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())


class CompanyMatchRepository(BaseRepository[CompanyMatch]):
    model = CompanyMatch

    def __init__(self, db: Session):
        super().__init__(db)

    def get_latest_for_resume_and_company(self, resume_id: uuid.UUID, company_name: str) -> CompanyMatch | None:
        stmt = (
            select(CompanyMatch)
            .where(CompanyMatch.resume_id == resume_id, CompanyMatch.company_name == company_name)
            .order_by(CompanyMatch.created_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_resume(self, resume_id: uuid.UUID, limit: int = 50) -> list[CompanyMatch]:
        stmt = (
            select(CompanyMatch)
            .where(CompanyMatch.resume_id == resume_id)
            .order_by(CompanyMatch.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
