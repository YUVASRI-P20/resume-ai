from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.resume.models.resume import ExtractedSkill, Resume, ResumeSection, ResumeSectionType, ResumeStatus, SkillCategory
from app.resume.repositories.resume_repository import ResumeRepository
from app.resume.services import resume_parser_service
from app.resume.services.ai import resume_analyzer_service
from app.resume.services.storage_service import get_storage_service
from app.resume.utils.file_validation import compute_checksum

logger = get_logger(__name__)


class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ResumeRepository(db)
        self.storage = get_storage_service()

    def upload_resume(self, user_id: uuid.UUID, content: bytes, filename: str, content_type: str) -> Resume:
        checksum = compute_checksum(content)
        storage_path = self.storage.upload(content, user_id=user_id, filename=filename)

        resume = Resume(
            user_id=user_id,
            original_filename=filename,
            storage_path=storage_path,
            storage_backend="supabase" if self._is_supabase() else "local",
            file_size_bytes=len(content),
            content_type=content_type,
            checksum_sha256=checksum,
            status=ResumeStatus.UPLOADED,
        )
        self.repo.add(resume)
        self.repo.commit()
        self.repo.refresh(resume)

        # Parse synchronously (in production this should be offloaded to a
        # Celery task; kept synchronous here to keep the module self-contained).
        self._parse_resume(resume, content)
        return resume

    def _is_supabase(self) -> bool:
        from app.core.config import settings
        return settings.STORAGE_BACKEND == "supabase"

    def _parse_resume(self, resume: Resume, content: bytes) -> None:
        resume.status = ResumeStatus.PARSING
        self.db.flush()
        try:
            raw_text = resume_parser_service.extract_raw_text_any(content, resume.original_filename)
            resume.raw_text = raw_text

            fallback_contact = resume_parser_service.extract_contact_fallbacks(raw_text)

            try:
                extraction = resume_analyzer_service.extract_resume_structure(raw_text)
                self._apply_extraction(resume, extraction, fallback_contact)
            except Exception as ai_exc:  # noqa: BLE001
                # AI extraction failing shouldn't fail the whole upload -- fall back
                # to raw text + regex contact info so the resume is still usable.
                logger.warning("AI structured extraction failed for resume %s: %s", resume.id, ai_exc)
                resume.email = resume.email or fallback_contact.get("email")
                resume.phone = resume.phone or fallback_contact.get("phone")
                resume.linkedin_url = resume.linkedin_url or fallback_contact.get("linkedin_url")
                resume.github_url = resume.github_url or fallback_contact.get("github_url")

            resume.status = ResumeStatus.PARSED
            resume.parse_error = None
        except Exception as exc:  # noqa: BLE001
            logger.exception("Resume parsing failed for resume %s", resume.id)
            resume.status = ResumeStatus.PARSE_FAILED
            resume.parse_error = str(exc)
        finally:
            self.db.commit()
            self.db.refresh(resume)

    def _apply_extraction(self, resume: Resume, extraction, fallback_contact: dict) -> None:
        resume.full_name = extraction.full_name
        resume.email = extraction.email or fallback_contact.get("email")
        resume.phone = extraction.phone or fallback_contact.get("phone")
        resume.location = extraction.location
        resume.linkedin_url = extraction.linkedin_url or fallback_contact.get("linkedin_url")
        resume.github_url = extraction.github_url or fallback_contact.get("github_url")
        resume.portfolio_url = extraction.portfolio_url

        sections: list[tuple[ResumeSectionType, str | None, object | None]] = [
            (ResumeSectionType.CONTACT, None, {
                "full_name": extraction.full_name, "email": resume.email, "phone": resume.phone,
                "location": extraction.location, "linkedin_url": resume.linkedin_url,
                "github_url": resume.github_url, "portfolio_url": extraction.portfolio_url,
            }),
            (ResumeSectionType.SUMMARY, extraction.professional_summary, None),
            (ResumeSectionType.SKILLS, None, extraction.skills),
            (ResumeSectionType.EDUCATION, None, extraction.education),
            (ResumeSectionType.EXPERIENCE, None, extraction.experience),
            (ResumeSectionType.PROJECTS, None, extraction.projects),
            (ResumeSectionType.CERTIFICATIONS, None, extraction.certifications),
            (ResumeSectionType.ACHIEVEMENTS, None, extraction.achievements),
        ]
        for idx, (section_type, text_content, json_content) in enumerate(sections):
            self.repo.add_section(ResumeSection(
                resume_id=resume.id,
                section_type=section_type,
                order_index=idx,
                content_text=text_content,
                content_json=json_content,
            ))

        for skill_name in extraction.skills:
            self.repo.add_skill(ExtractedSkill(
                resume_id=resume.id,
                name=skill_name,
                category=SkillCategory.OTHER,
            ))

    def get_owned_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        resume = self.repo.get_owned_by_user(resume_id, user_id)
        if resume is None:
            # Distinguish "not found" from "belongs to someone else" without
            # leaking existence to unauthorized users -- both return 404.
            raise NotFoundException("Resume not found.")
        return resume

    def get_owned_resume_with_details(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        details = self.repo.get_with_details(resume_id)
        if details is None or details.user_id != user_id:
            raise NotFoundException("Resume not found.")
        return details

    def list_resumes(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Resume]:
        return self.repo.list_for_user(user_id, limit=limit, offset=offset)

    def delete_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> None:
        resume = self.get_owned_resume(resume_id, user_id)
        try:
            self.storage.delete(resume.storage_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to delete stored file for resume %s: %s", resume_id, exc)
        self.repo.soft_delete(resume)
        self.repo.commit()
