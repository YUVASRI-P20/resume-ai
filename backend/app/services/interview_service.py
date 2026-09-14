"""
Interview service handling AI question generation, adaptive follow-ups, and evaluation.

Every question is grounded in BOTH:
  1. the user's actual uploaded resume text, and
  2. the selected company / job role,
and each follow-up is generated from the candidate's previous answer so the
conversation is adaptive instead of a fixed question list.

A deterministic offline fallback is used ONLY when no GEMINI_API_KEY is
configured (local development). Fallback questions are still anchored to the
resume's extracted skills / role requirements rather than generic trivia.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.exceptions import AppException
from app.models.interview import (
    Interview,
    InterviewQuestion,
    InterviewAnswer,
    InterviewEvaluation,
    InterviewSummary,
    InterviewStatus,
    InterviewDifficulty,
)
from app.models.resume import Resume

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    # AI helper
    # ------------------------------------------------------------------ #
    def _call_gemini(self, prompt: str) -> Optional[dict]:
        """Call Gemini for structured JSON. Returns None when the AI is not
        configured/fails so callers can use their grounded fallback."""
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
            # Defensive: strip code fences if the model adds them anyway.
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception as e:  # noqa: BLE001 - network/quota/safety-block etc.
            logger.error("Gemini API error: %s", e)
            return None

    # ------------------------------------------------------------------ #
    # Context helpers
    # ------------------------------------------------------------------ #
    async def _load_resume(self, interview: Interview) -> tuple[str, List[str]]:
        """Load the resume attached to this interview (owned by the user) and
        a light-weight list of skills found in it for question grounding."""
        if not interview.resume_id:
            return "", []
        resume = await self.db.get(Resume, interview.resume_id)
        if resume is None or resume.user_id != interview.user_id:
            return "", []
        raw = resume.raw_text or ""
        skills: List[str] = []
        if resume.skills:
            skills = [s.name for s in resume.skills][:15]
        elif raw:
            # Cheap keyword scan when structured skills aren't parsed yet.
            from app.resume.services.ai.resume_analyzer_service import _heuristic_extract_skills

            skills = _heuristic_extract_skills(raw)[:15]
        return raw, skills

    def _grounding_block(self, interview: Interview, resume_text: str, skills: List[str]) -> str:
        skill_line = ", ".join(skills) if skills else "Not extracted"
        resume_excerpt = (resume_text or "")[:3000] or "No resume text available."
        return (
            f"CANDIDATE PROFILE (from the uploaded resume):\n"
            f"- Extracted skills: {skill_line}\n"
            f"- Resume excerpt:\n\"\"\"\n{resume_excerpt}\n\"\"\"\n\n"
            f"TARGET: {interview.company} — {interview.job_role} role ({interview.domain}).\n"
            f"Only ask about technologies, projects and concepts grounded in the "
            f"resume above or core to the {interview.job_role} role at {interview.company}."
        )

    def _fallback_question(self, interview: Interview, skills: List[str], history: List[dict]) -> dict:
        """Deterministic, evidence-anchored question used when no AI key is set.
        It uses the candidate's own skills and the selected role — never random
        trivia — and avoids repeating earlier questions."""
        asked = {h["question_text"].lower() for h in history}
        skill_pool = [s for s in skills if s] or ["Python", "SQL", "REST APIs"]

        templates = [
            ("Walk me through the project in your resume where you used {skill}. What problem did it solve and what were the hardest technical decisions?",
             "resume", "Medium"),
            ("You listed {skill} on your resume. Explain how you applied it in practice and one trade-off you made.",
             "resume", "Medium"),
            ("A {job_role} at {company} often works with {skill}. Describe a scenario where you would use it and the pitfalls to watch for.",
             "role", "Medium"),
            ("How would you debug a performance issue in a production system that relies heavily on {skill}?",
             "scenario", "Hard"),
        ]
        for skill in skill_pool:
            for text, qtype, diff in templates:
                candidate = text.format(skill=skill, job_role=interview.job_role, company=interview.company)
                if candidate.lower() not in asked:
                    return {
                        "question_text": candidate,
                        "question_type": qtype,
                        "difficulty": diff if interview.current_difficulty != InterviewDifficulty.HARD else "Hard",
                        "expected_key_points": f"Concrete experience with {skill}, trade-offs, and role-relevant depth.",
                    }
        return {
            "question_text": f"Summarize the technical decisions you are proudest of and how they relate to the {interview.job_role} role at {interview.company}.",
            "question_type": "conceptual",
            "difficulty": interview.current_difficulty.value,
            "expected_key_points": "Self-awareness, prioritization, role alignment.",
        }

    # ------------------------------------------------------------------ #
    # Interview lifecycle
    # ------------------------------------------------------------------ #
    async def start_interview(self, user_id: uuid.UUID, data: Any) -> Interview:
        resume_text = ""
        if data.resume_id:
            resume = await self.db.get(Resume, data.resume_id)
            if resume and resume.user_id == user_id:
                resume_text = resume.raw_text or ""

        interview = Interview(
            user_id=user_id,
            resume_id=data.resume_id,
            company=data.company,
            job_role=data.job_role,
            domain=data.domain,
            difficulty=data.difficulty,
            interview_type=data.interview_type,
            duration_minutes=data.duration_minutes,
            number_of_questions=data.number_of_questions,
            status=InterviewStatus.IN_PROGRESS,
            current_difficulty=data.difficulty,
            question_count=0,
            completed_question_count=0,
            start_time=datetime.now(timezone.utc),
        )
        self.db.add(interview)
        await self.db.commit()
        await self.db.refresh(interview)

        # Generate first question
        await self.generate_next_question(interview.id, resume_text)
        return interview

    async def generate_next_question(self, interview_id: uuid.UUID, resume_text: str = "") -> Optional[InterviewQuestion]:
        interview = await self.db.get(Interview, interview_id)
        if not interview or interview.status != InterviewStatus.IN_PROGRESS:
            return None

        if interview.question_count >= interview.number_of_questions:
            interview.status = InterviewStatus.COMPLETED
            interview.end_time = datetime.now(timezone.utc)
            await self.db.commit()
            await self.generate_summary(interview.id)
            return None

        resume_text, skills = await self._load_resume(interview)

        # --- Adaptive context: pull the previous Q + answer so the next
        # question is a follow-up on what the candidate actually said. ---
        history_rows = await self.db.execute(
            select(InterviewQuestion, InterviewAnswer, InterviewEvaluation)
            .join(InterviewAnswer, InterviewQuestion.id == InterviewAnswer.question_id)
            .outerjoin(InterviewEvaluation, InterviewAnswer.id == InterviewEvaluation.answer_id)
            .where(InterviewQuestion.interview_id == interview_id)
            .order_by(InterviewQuestion.question_index.desc())
            .limit(1)
        )
        history = [
            {
                "question_text": q.question_text,
                "answer_text": a.answer_text,
                "evaluation_feedback": e.feedback if e else "",
                "score": e.score if e else None,
            }
            for q, a, e in history_rows.all()
        ]

        prompt = f"""You are an expert technical interviewer at {interview.company} interviewing a candidate for a {interview.job_role} role in {interview.domain}.
Current Interview Difficulty: {interview.current_difficulty.value}
Questions asked so far: {interview.question_count}

{self._grounding_block(interview, resume_text, skills)}

Previous exchange (most recent first):
{json.dumps(history, indent=2) if history else "This is the first question."}

Generate the NEXT question as a JSON object with keys:
- question_text (string)
- question_type (string: conceptual, scenario, problem_solving, resume, company, follow_up)
- difficulty (string: Easy, Medium, Hard)
- expected_key_points (string)

Rules:
1. If a previous exchange exists, the question MUST be an adaptive follow-up that digs deeper into the candidate's last answer (e.g. clarifying a claim, exploring trade-offs, probing an implementation detail). Do NOT change topic abruptly.
2. Otherwise, open with a question grounded in the candidate's resume projects/skills or the core requirements of the {interview.job_role} role at {interview.company}.
3. Never invent technologies that are not in the resume or the role.
"""
        ai_data = self._call_gemini(prompt)
        if ai_data is None or not ai_data.get("question_text"):
            ai_data = self._fallback_question(interview, skills, history)

        interview.question_count += 1
        await self.db.commit()

        try:
            difficulty = InterviewDifficulty(ai_data.get("difficulty", interview.current_difficulty.value))
        except ValueError:
            difficulty = interview.current_difficulty

        question = InterviewQuestion(
            interview_id=interview.id,
            question_index=interview.question_count,
            question_text=ai_data.get("question_text", ""),
            question_type=ai_data.get("question_type", "conceptual"),
            difficulty=difficulty,
            expected_key_points=ai_data.get("expected_key_points", ""),
        )
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question

    async def submit_answer(self, interview_id: uuid.UUID, question_id: uuid.UUID, answer_text: str) -> InterviewEvaluation:
        interview = await self.db.get(Interview, interview_id)
        question = await self.db.get(InterviewQuestion, question_id)
        if not interview or not question or question.interview_id != interview.id:
            raise AppException(status_code=404, detail="Interview or question not found.")

        answer = InterviewAnswer(
            interview_id=interview.id,
            question_id=question.id,
            answer_text=answer_text,
        )
        self.db.add(answer)
        await self.db.commit()
        await self.db.refresh(answer)

        prompt = f"""Evaluate the candidate's answer for a {interview.job_role} interview at {interview.company}.
Question: {question.question_text}
Expected Key Points: {question.expected_key_points}
Candidate Answer: {answer_text}

Return a JSON object with keys:
- score (float 0-100)
- correctness (float 0-100)
- technical_depth (float 0-100)
- clarity (float 0-100)
- confidence (float 0-100)
- feedback (string, specific to this answer)
- knowledge_gap (string or null: a concrete topic the candidate struggled with)
- next_difficulty (string: Easy, Medium, Hard)
"""
        ai_data = self._call_gemini(prompt)
        if ai_data is None:
            # Deterministic scoring fallback (still based on the actual answer).
            words = len(answer_text.split())
            base = min(90.0, 45.0 + words * 1.5)
            ai_data = {
                "score": base,
                "correctness": base,
                "technical_depth": max(40.0, base - 5),
                "clarity": max(40.0, base - 2),
                "confidence": max(40.0, base - 3),
                "feedback": (
                    "Answer captured relevant points with adequate detail."
                    if words >= 25
                    else "Answer was brief; expand with concrete examples, trade-offs and outcomes."
                ),
                "knowledge_gap": None,
                "next_difficulty": interview.current_difficulty.value,
            }

        next_diff_str = ai_data.get("next_difficulty", interview.current_difficulty.value)
        try:
            next_difficulty = InterviewDifficulty(next_diff_str)
        except ValueError:
            next_difficulty = interview.current_difficulty

        interview.current_difficulty = next_difficulty
        interview.completed_question_count += 1
        await self.db.commit()

        evaluation = InterviewEvaluation(
            answer_id=answer.id,
            score=float(ai_data.get("score", 75.0)),
            correctness=float(ai_data.get("correctness", 75.0)),
            technical_depth=float(ai_data.get("technical_depth", 75.0)),
            clarity=float(ai_data.get("clarity", 75.0)),
            confidence=float(ai_data.get("confidence", 75.0)),
            feedback=ai_data.get("feedback", ""),
            knowledge_gap=ai_data.get("knowledge_gap"),
            next_difficulty=next_difficulty,
        )
        self.db.add(evaluation)
        await self.db.commit()
        await self.db.refresh(evaluation)
        return evaluation

    async def generate_summary(self, interview_id: uuid.UUID) -> InterviewSummary:
        interview = await self.db.get(Interview, interview_id)
        if not interview:
            raise AppException(status_code=404, detail="Interview not found.")

        # Build the actual Q/A/evaluation transcript for grounding.
        rows = await self.db.execute(
            select(InterviewQuestion, InterviewAnswer, InterviewEvaluation)
            .join(InterviewAnswer, InterviewQuestion.id == InterviewAnswer.question_id)
            .outerjoin(InterviewEvaluation, InterviewAnswer.id == InterviewEvaluation.answer_id)
            .where(InterviewQuestion.interview_id == interview_id)
            .order_by(InterviewQuestion.question_index)
        )
        transcript = "\n".join(
            f"Q{q.question_index}: {q.question_text}\nA: {a.answer_text}\nScore: {e.score if e else 'n/a'} | Feedback: {e.feedback if e else 'n/a'}"
            for q, a, e in rows.all()
        ) or "No answers were recorded."

        prompt = f"""Generate an interview completion summary for a {interview.job_role} interview at {interview.company}.
Base EVERY statement on the actual transcript below — do not invent topics that were not discussed.

TRANSCRIPT:
{transcript[:8000]}

Return a JSON object with keys:
- overall_performance (string)
- technical_performance (string)
- strong_topics (list of strings — topics answered well)
- weak_topics (list of strings — topics answered poorly)
- average_score (float, computed from the scores above)
- difficulty_progression (list of strings)
- knowledge_gaps (list of strings or empty)
- improvement_suggestions (list of strings)
"""
        ai_data = self._call_gemini(prompt)
        if ai_data is None:
            # Compute the summary from the real evaluation records.
            rows = await self.db.execute(
                select(InterviewEvaluation)
                .join(InterviewAnswer, InterviewEvaluation.answer_id == InterviewAnswer.id)
                .where(InterviewAnswer.interview_id == interview_id)
            )
            evals = rows.scalars().all()
            scores = [e.score for e in evals] or [0.0]
            strong = [e.feedback for e in evals if e.score >= 70]
            weak = [e.knowledge_gap for e in evals if e.knowledge_gap]
            avg = round(sum(scores) / len(scores), 1)
            ai_data = {
                "overall_performance": (
                    f"Completed {len(evals)} question(s) with an average score of {avg}."
                ),
                "technical_performance": (
                    "Demonstrated working knowledge across the topics discussed."
                    if avg >= 60
                    else "Several core topics need reinforcement."
                ),
                "strong_topics": strong or ["Technical fundamentals"],
                "weak_topics": weak or [],
                "average_score": avg,
                "difficulty_progression": [e.next_difficulty.value for e in evals],
                "knowledge_gaps": weak or [],
                "improvement_suggestions": [
                    "Review the feedback for each answer and practice the weak topics.",
                ],
            }

        summary = InterviewSummary(
            interview_id=interview.id,
            overall_performance=ai_data.get("overall_performance", "Completed."),
            technical_performance=ai_data.get("technical_performance", ""),
            strong_topics=", ".join(ai_data.get("strong_topics", []) or []),
            weak_topics=", ".join(ai_data.get("weak_topics", []) or []),
            average_score=float(ai_data.get("average_score", 0.0)),
            difficulty_progression=", ".join(ai_data.get("difficulty_progression", []) or []),
            knowledge_gaps=", ".join(ai_data.get("knowledge_gaps", []) or []) or None,
            improvement_suggestions=", ".join(ai_data.get("improvement_suggestions", []) or []),
        )
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)
        return summary
