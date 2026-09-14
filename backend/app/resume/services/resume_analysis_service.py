from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AIServiceError, ValidationException
from app.core.logging import get_logger
from app.resume.models.resume import Resume, ResumeStatus
from app.resume.models.resume_analysis import (
    AnalysisStatus,
    CompanyMatch,
    KeywordStatus,
    ResumeAnalysis,
    ResumeKeyword,
    ResumeScore,
    ResumeSectionName,
    ResumeSuggestion,
    SuggestionSeverity,
    SuggestionType,
)
from app.resume.repositories.resume_analysis_repository import CompanyMatchRepository, ResumeAnalysisRepository
from app.resume.repositories.resume_repository import ResumeRepository
from app.resume.schemas.resume_analysis import SUPPORTED_COMPANIES
from app.resume.services.ai import resume_analyzer_service

logger = get_logger(__name__)


class ResumeAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.resume_repo = ResumeRepository(db)
        self.analysis_repo = ResumeAnalysisRepository(db)
        self.match_repo = CompanyMatchRepository(db)

    def _get_analyzable_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        resume = self.resume_repo.get_owned_by_user(resume_id, user_id)
        if resume is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Resume not found.")
        if resume.status != ResumeStatus.PARSED or not resume.raw_text:
            raise ValidationException(
                "Resume must be successfully parsed before it can be analyzed. "
                f"Current status: {resume.status.value}."
            )
        return resume

    def analyze_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID, force_refresh: bool = False) -> ResumeAnalysis:
        resume = self._get_analyzable_resume(resume_id, user_id)

        if not force_refresh:
            existing = self.analysis_repo.get_latest_for_resume(resume_id)
            if existing is not None and existing.status == AnalysisStatus.COMPLETED:
                return existing

        analysis = ResumeAnalysis(
            resume_id=resume_id,
            user_id=user_id,
            status=AnalysisStatus.PENDING,
        )
        self.analysis_repo.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        try:
            result, raw = resume_analyzer_service.analyze_resume(resume.raw_text)
        except AIServiceError as exc:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(exc)
            self.db.commit()
            raise

        analysis.status = AnalysisStatus.COMPLETED
        analysis.overall_score = result.overall_score
        analysis.ats_compatibility_score = result.ats_compatibility_score
        analysis.professional_summary_analysis = result.professional_summary_analysis
        analysis.strengths = result.strengths
        analysis.weaknesses = result.weaknesses
        analysis.missing_skills = result.missing_skills
        analysis.missing_keywords = result.missing_keywords
        analysis.grammar_suggestions = result.grammar_suggestions
        analysis.formatting_suggestions = result.formatting_suggestions
        analysis.raw_ai_response = raw
        analysis.model_used = None  # set below via settings to avoid leaking key material anywhere

        from app.core.config import settings
        analysis.model_used = settings.GEMINI_MODEL

        for s in result.section_scores:
            try:
                section_enum = ResumeSectionName(s.section.lower())
            except ValueError:
                continue
            self.db.add(ResumeScore(
                analysis_id=analysis.id, section=section_enum, score=s.score, feedback=s.feedback,
            ))

        for sug in result.suggestions:
            try:
                type_enum = SuggestionType(sug.type.lower())
            except ValueError:
                type_enum = SuggestionType.CONTENT
            try:
                severity_enum = SuggestionSeverity(sug.severity.lower())
            except ValueError:
                severity_enum = SuggestionSeverity.MEDIUM
            self.db.add(ResumeSuggestion(
                analysis_id=analysis.id, suggestion_type=type_enum, section=sug.section,
                severity=severity_enum, message=sug.message, suggested_fix=sug.suggested_fix,
            ))

        for kw in result.keywords:
            try:
                status_enum = KeywordStatus(kw.status.lower())
            except ValueError:
                status_enum = KeywordStatus.MISSING
            self.db.add(ResumeKeyword(
                analysis_id=analysis.id, keyword=kw.keyword, status=status_enum, relevance=kw.relevance,
            ))

        self.db.commit()
        return self.analysis_repo.get_with_details(analysis.id)

    def get_latest_analysis(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> ResumeAnalysis:
        self._assert_owns_resume(resume_id, user_id)
        analysis = self.analysis_repo.get_latest_for_resume(resume_id)
        if analysis is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("No analysis found for this resume. Run POST /analyze first.")
        return analysis

    def get_suggestions(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> list[ResumeSuggestion]:
        analysis = self.get_latest_analysis(resume_id, user_id)
        return analysis.suggestions

    def _assert_owns_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        resume = self.resume_repo.get_owned_by_user(resume_id, user_id)
        if resume is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Resume not found.")
        return resume

    def match_company(self, resume_id: uuid.UUID, user_id: uuid.UUID, company_name: str, target_role: str | None) -> CompanyMatch:
        if company_name not in SUPPORTED_COMPANIES:
            raise ValidationException(
                f"Unsupported company '{company_name}'. Supported companies: {', '.join(SUPPORTED_COMPANIES)}."
            )
        resume = self._get_analyzable_resume(resume_id, user_id)

        result, raw = resume_analyzer_service.match_company(resume.raw_text, company_name, target_role)

        match = CompanyMatch(
            resume_id=resume_id,
            user_id=user_id,
            company_name=company_name,
            target_role=target_role,
            role_match_score=result.role_match_score,
            resume_compatibility_score=result.resume_compatibility_score,
            required_skills=result.required_skills,
            matched_skills=result.matched_skills,
            missing_skills=result.missing_skills,
            relevant_keywords=result.relevant_keywords,
            improvement_suggestions=result.improvement_suggestions,
            raw_ai_response=raw,
        )
        self.match_repo.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def get_latest_company_match(self, resume_id: uuid.UUID, user_id: uuid.UUID, company_name: str | None = None) -> list[CompanyMatch] | CompanyMatch:
        self._assert_owns_resume(resume_id, user_id)
        if company_name:
            match = self.match_repo.get_latest_for_resume_and_company(resume_id, company_name)
            if match is None:
                from app.core.exceptions import NotFoundException
                raise NotFoundException(f"No company match found for '{company_name}'. Run POST /company-match first.")
            return match
        return self.match_repo.list_for_resume(resume_id)
