import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.resume.models.resume import ExtractedSkill, Resume, ResumeSection
from app.resume.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    model = Resume

    def __init__(self, db: Session):
        super().__init__(db)

    def get_with_details(self, resume_id: uuid.UUID) -> Resume | None:
        stmt = (
            select(Resume)
            .where(Resume.id == resume_id, Resume.is_active.is_(True))
            .options(selectinload(Resume.sections), selectinload(Resume.skills))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_owned_by_user(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume | None:
        stmt = select(Resume).where(
            Resume.id == resume_id, Resume.user_id == user_id, Resume.is_active.is_(True)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Resume]:
        stmt = (
            select(Resume)
            .where(Resume.user_id == user_id, Resume.is_active.is_(True))
            .order_by(Resume.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(stmt).scalars().all())

    def add_section(self, section: ResumeSection) -> ResumeSection:
        self.db.add(section)
        self.db.flush()
        return section

    def add_skill(self, skill: ExtractedSkill) -> ExtractedSkill:
        self.db.add(skill)
        self.db.flush()
        return skill

    def soft_delete(self, resume: Resume) -> None:
        resume.is_active = False
        self.db.flush()
