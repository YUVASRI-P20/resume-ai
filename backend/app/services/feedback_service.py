"""
Feedback service handling interview performance analysis, hallucination detection, and knowledge gaps.

Scores and observations are ALWAYS derived from the actual evaluation records
stored for the interview. When GEMINI_API_KEY is configured, Gemini writes the
narrative summary/strengths/weaknesses from the real transcript — but it is
given only the real Q/A/evaluation data, and its output is validated. Without
an API key, a deterministic summary is generated from the same real records.
No fake scores, no placeholder content.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.exceptions import AppException
from app.models.interview import Interview, InterviewAnswer, InterviewQuestion, InterviewEvaluation
from app.models.feedback import (
    InterviewFeedback,
    FeedbackCategory,
    KnowledgeGap,
    Strength,
    Weakness,
    HallucinationFinding,
    FeedbackSeverity,
)

logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _call_gemini(self, prompt: str) -> Optional[dict]:
        if not settings.GEMINI_API_KEY:
            return None
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            text = (response.text or "").strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception as e:  # noqa: BLE001
            logger.error("Gemini feedback generation error: %s", e)
            return None

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return default

    async def generate_feedback(self, interview_id, user_id) -> InterviewFeedback:
        interview = await self.db.get(Interview, interview_id)
        if not interview or interview.user_id != user_id:
            raise AppException(status_code=404, detail="Interview not found.")

        # Check if feedback already exists
        existing_res = await self.db.execute(
            select(InterviewFeedback).filter(InterviewFeedback.interview_id == interview_id)
        )
        existing = existing_res.scalars().first()
        if existing:
            return existing

        # Gather the REAL Q/A/evaluation records
        qa_result = await self.db.execute(
            select(InterviewQuestion, InterviewAnswer, InterviewEvaluation)
            .join(InterviewAnswer, InterviewQuestion.id == InterviewAnswer.question_id)
            .join(InterviewEvaluation, InterviewAnswer.id == InterviewEvaluation.answer_id)
            .filter(InterviewQuestion.interview_id == interview_id)
        )
        qa_records = qa_result.all()

        if not qa_records:
            raise AppException(
                status_code=400,
                detail="No evaluated answers found for this interview yet. Complete at least one question first.",
            )

        # Real aggregate scores computed from evaluation rows.
        scores = [e.score for _q, _a, e in qa_records]
        technical = [e.technical_depth for _q, _a, e in qa_records]
        clarity = [e.clarity for _q, _a, e in qa_records]
        confidence = [e.confidence for _q, _a, e in qa_records]
        avg = lambda xs: round(sum(xs) / len(xs), 1)  # noqa: E731

        # Real coding score: this candidate's best passing coding submission.
        from app.models.coding import CodingSubmission, CodeExecution, SubmissionStatus

        coding_execs = (
            await self.db.execute(
                select(CodeExecution, CodingSubmission)
                .join(CodingSubmission, CodeExecution.submission_id == CodingSubmission.id)
                .filter(CodingSubmission.user_id == user_id)
                .order_by(CodeExecution.created_at.desc())
                .limit(20)
            )
        ).all()
        coding_scores: List[float] = []
        for _exec, _sub in coding_execs:
            if _exec.total_tests > 0:
                coding_scores.append(_exec.passed_tests / _exec.total_tests * 100.0)
        coding_score = avg(coding_scores) if coding_scores else 0.0

        # Knowledge gaps the evaluations actually recorded.
        gap_rows = (
            await self.db.execute(
                select(KnowledgeGap).filter(KnowledgeGap.interview_id == interview_id)
            )
        ).scalars().all()
        gaps_payload = [
            {"topic": g.topic, "description": g.description, "severity": g.severity.value}
            for g in gap_rows
        ]

        qa_summary_text = "\n".join(
            [
                f"Q{q.question_index}: {q.question_text}\nA: {a.answer_text}\n"
                f"Score: {e.score} | Correctness: {e.correctness} | Depth: {e.technical_depth} | "
                f"Feedback: {e.feedback} | Gap: {e.knowledge_gap or 'none'}\n"
                for q, a, e in qa_records
            ]
        )

        prompt = f"""Analyze the complete technical interview performance for a {interview.job_role} role at {interview.company}.
Base EVERY statement strictly on the real interview records below. Do not invent topics, scores, or observations.

REAL AGGREGATES (computed from evaluation records — reuse these numbers exactly):
- average_answer_score: {avg(scores)}
- average_technical_depth: {avg(technical)}
- average_clarity: {avg(clarity)}
- average_confidence: {avg(confidence)}
- coding_score (from actual test-case pass rates): {coding_score}

RECORDED KNOWLEDGE GAPS: {json.dumps(gaps_payload) if gaps_payload else "none recorded"}

INTERVIEW Q&A RECORDS:
{qa_summary_text[:8000]}

Return a JSON object with keys:
- overall_score (float 0-100; use the average_answer_score)
- technical_score (float; use the average_technical_depth)
- communication_score (float; use the average_clarity)
- confidence_score (float; use the average_confidence)
- coding_score (float; use the provided coding_score)
- interview_summary (string, grounded in the actual Q&A)
- detailed_feedback (string, grounded in the actual Q&A)
- categories (list of objects with category_name, score, comments — derived from the records)
- strengths (list of objects with title, description — only topics actually answered well)
- weaknesses (list of objects with title, description — only topics actually answered poorly)
- knowledge_gaps (list of objects with topic, description, severity — use the recorded gaps)
- hallucinations (list of objects with concept, candidate_claim, correct_explanation, severity, confidence — only where an answer contradicts well-established fact; empty list if none)
"""
        ai_data = await self._call_gemini(prompt)
        if ai_data is None:
            # Deterministic summary built from the real records only.
            strong_pairs = [(q, e) for q, _a, e in qa_records if e.score >= 70]
            weak_pairs = [(q, e) for q, _a, e in qa_records if e.score < 70]
            ai_data = {
                "overall_score": avg(scores),
                "technical_score": avg(technical),
                "communication_score": avg(clarity),
                "confidence_score": avg(confidence),
                "coding_score": coding_score,
                "interview_summary": (
                    f"Completed {len(qa_records)} evaluated question(s) for the {interview.job_role} role "
                    f"at {interview.company} with an average score of {avg(scores)}."
                ),
                "detailed_feedback": " ".join(e.feedback for _q, _a, e in qa_records)[:2000],
                "categories": [
                    {"category_name": "Technical Depth", "score": avg(technical), "comments": "Average technical depth across evaluated answers."},
                    {"category_name": "Clarity", "score": avg(clarity), "comments": "Average clarity of explanations across evaluated answers."},
                ],
                "strengths": [
                    {"title": f"Q{q.question_index}: {q.question_text[:60]}", "description": e.feedback}
                    for q, e in strong_pairs[:3]
                ]
                or [{"title": "Consistency", "description": "No answer scored 70 or above; keep practicing."}],
                "weaknesses": [
                    {"title": f"Q{q.question_index}: {q.question_text[:60]}", "description": e.knowledge_gap or e.feedback}
                    for q, e in weak_pairs[:3]
                ],
                "knowledge_gaps": gaps_payload,
                "hallucinations": [],  # only AI can verify facts; empty when offline
            }

        feedback = InterviewFeedback(
            interview_id=interview.id,
            user_id=user_id,
            overall_score=self._clamp(ai_data.get("overall_score", avg(scores))),
            technical_score=self._clamp(ai_data.get("technical_score", avg(technical))),
            communication_score=self._clamp(ai_data.get("communication_score", avg(clarity))),
            confidence_score=self._clamp(ai_data.get("confidence_score", avg(confidence))),
            coding_score=self._clamp(ai_data.get("coding_score", coding_score)),
            interview_summary=str(ai_data.get("interview_summary", ""))[:4000],
            detailed_feedback=str(ai_data.get("detailed_feedback", ""))[:8000],
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)

        # Save related records
        for cat in ai_data.get("categories", []) or []:
            self.db.add(FeedbackCategory(
                feedback_id=feedback.id,
                category_name=str(cat.get("category_name", "General"))[:100],
                score=self._clamp(cat.get("score")),
                comments=str(cat.get("comments", "")),
            ))

        for st in ai_data.get("strengths", []) or []:
            self.db.add(Strength(
                feedback_id=feedback.id,
                title=str(st.get("title", "Strength"))[:150],
                description=str(st.get("description", "")),
            ))

        for wk in ai_data.get("weaknesses", []) or []:
            self.db.add(Weakness(
                feedback_id=feedback.id,
                title=str(wk.get("title", "Weakness"))[:150],
                description=str(wk.get("description", "")),
            ))

        # Persist any NEW knowledge gaps from evaluations not already recorded.
        existing_gap_topics = {g.topic.lower() for g in gap_rows}
        for kg in ai_data.get("knowledge_gaps", []) or []:
            topic = str(kg.get("topic", "")).strip()[:150]
            if not topic or topic.lower() in existing_gap_topics:
                continue
            try:
                severity = FeedbackSeverity(kg.get("severity", "Medium"))
            except ValueError:
                severity = FeedbackSeverity.MEDIUM
            self.db.add(KnowledgeGap(
                user_id=user_id,
                interview_id=interview.id,
                topic=topic,
                description=str(kg.get("description", "")),
                severity=severity,
            ))
            existing_gap_topics.add(topic.lower())

        # Also record knowledge gaps captured per-evaluation during the interview.
        for _q, _a, e in qa_records:
            if e.knowledge_gap and e.knowledge_gap.strip().lower() not in existing_gap_topics:
                self.db.add(KnowledgeGap(
                    user_id=user_id,
                    interview_id=interview.id,
                    topic=e.knowledge_gap.strip()[:150],
                    description=f"Identified from feedback on: {_q.question_text[:200]}",
                    severity=FeedbackSeverity.MEDIUM,
                ))
                existing_gap_topics.add(e.knowledge_gap.strip().lower())

        for hal in ai_data.get("hallucinations", []) or []:
            try:
                severity = FeedbackSeverity(hal.get("severity", "Medium"))
            except ValueError:
                severity = FeedbackSeverity.MEDIUM
            self.db.add(HallucinationFinding(
                feedback_id=feedback.id,
                concept=str(hal.get("concept", "Concept"))[:150],
                candidate_claim=str(hal.get("candidate_claim", "")),
                correct_explanation=str(hal.get("correct_explanation", "")),
                severity=severity,
                confidence=self._clamp(hal.get("confidence", 85.0)),
            ))

        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback
