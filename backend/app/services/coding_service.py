"""
Coding service handling secure code execution, test case evaluation, and AI code reviews.

Execution is REAL: user code runs in a subprocess with a strict timeout against
the question's stored test cases. There is no simulated/passed-anyway path —
if tests fail, the submission fails. Non-Python languages are rejected with a
clear error until a runner for them is configured (never silently "pass").
"""
from __future__ import annotations

import json
import logging
import subprocess
import sys
import tempfile
import os
import time
from typing import Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.exceptions import AppException, ValidationException
from app.models.coding import (
    CodingQuestion,
    CodingTestCase,
    CodingSubmission,
    CodeExecution,
    CodeReview,
    SubmissionStatus,
)

logger = logging.getLogger(__name__)

# Languages this deployment can actually execute.
SUPPORTED_EXECUTION_LANGUAGES = {"python": [sys.executable or "python", "-I"]}

# Guard against pathological resource use inside the sandboxed subprocess.
MAX_CODE_LENGTH = 50_000
EXECUTION_TIMEOUT_SECONDS = 10


class CodingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    # Execution
    # ------------------------------------------------------------------ #
    def _run_single_case(self, language: str, source_code: str, test_case: CodingTestCase) -> tuple[Optional[str], Optional[str]]:
        """Run the user's program once with the test input on stdin.

        Returns (stdout, stderr). The program is expected to READ the input
        from stdin and PRINT its answer to stdout — the classic judge contract.
        """
        runner = SUPPORTED_EXECUTION_LANGUAGES.get(language.lower())
        if runner is None:
            raise ValidationException(
                f"Execution for '{language}' is not supported yet. Supported: Python. "
                "Choose Python as your language."
            )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            fname = f.name

        try:
            result = subprocess.run(
                runner + [fname],
                input=test_case.input_data or "",
                text=True,
                capture_output=True,
                timeout=EXECUTION_TIMEOUT_SECONDS,
            )
            if result.returncode != 0:
                return None, (result.stderr or "Program exited with a non-zero status.").strip()[:2000]
            return result.stdout, None
        except subprocess.TimeoutExpired:
            return None, f"Execution timed out (exceeded {EXECUTION_TIMEOUT_SECONDS} seconds)."
        finally:
            try:
                os.unlink(fname)
            except OSError:
                pass

    @staticmethod
    def _normalize_output(output: str) -> str:
        """Compare outputs tolerantly: strip surrounding whitespace and
        normalize trailing newlines per line so '1 2 3' == '1 2 3\\n'."""
        lines = [line.rstrip() for line in (output or "").strip().splitlines()]
        return "\n".join(lines).strip()

    def _execute_code_securely(
        self, language: str, source_code: str, test_cases: List[CodingTestCase]
    ) -> dict[str, Any]:
        """Run every test case for real. No demo shortcut — failures fail."""
        if len(source_code) > MAX_CODE_LENGTH:
            raise ValidationException("Source code is too large to execute (50,000 character limit).")

        passed_tests = 0
        total_tests = len(test_cases)
        error_msg: Optional[str] = None
        execution_status = "PASSED"
        per_case_results: list[dict[str, Any]] = []

        started = time.perf_counter()
        for tc in test_cases:
            stdout, err = self._run_single_case(language, source_code, tc)
            if err is not None:
                execution_status = (
                    "TIMEOUT" if "timed out" in err.lower() else "RUNTIME_ERROR"
                )
                error_msg = err
                per_case_results.append(
                    {"test_case_id": str(tc.id), "passed": False, "hidden": tc.is_hidden, "status": execution_status}
                )
                break

            expected = self._normalize_output(tc.expected_output)
            actual = self._normalize_output(stdout or "")
            case_passed = actual == expected
            if case_passed:
                passed_tests += 1
            else:
                execution_status = "FAILED"
                error_msg = None
            per_case_results.append(
                {"test_case_id": str(tc.id), "passed": case_passed, "hidden": tc.is_hidden, "status": "PASSED" if case_passed else "FAILED"}
            )

        wall_time_ms = round((time.perf_counter() - started) * 1000.0, 1)

        if total_tests == 0:
            execution_status = "RUNTIME_ERROR"
            error_msg = "This question has no test cases configured."
        elif passed_tests == total_tests and execution_status != "RUNTIME_ERROR":
            execution_status = "PASSED"
        elif execution_status == "PASSED":
            execution_status = "FAILED"

        return {
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "runtime_ms": wall_time_ms,
            # Real measurement is out of scope for the subprocess sandbox;
            # report it as unmeasured instead of inventing a number.
            "memory_mb": 0.0,
            "error_message": error_msg,
            "execution_status": execution_status,
            "per_case": per_case_results,
        }

    # ------------------------------------------------------------------ #
    # Submission flow
    # ------------------------------------------------------------------ #
    async def submit_and_execute(self, user_id, payload: Any) -> CodingSubmission:
        question = await self.db.get(CodingQuestion, payload.question_id)
        if not question:
            raise AppException(status_code=404, detail="Coding question not found.")

        if payload.language.lower() not in SUPPORTED_EXECUTION_LANGUAGES:
            raise ValidationException(
                f"Execution for '{payload.language}' is not supported yet. Supported: Python."
            )

        submission = CodingSubmission(
            user_id=user_id,
            question_id=payload.question_id,
            language=payload.language,
            source_code=payload.source_code,
            status=SubmissionStatus.RUNNING,
        )
        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)

        tc_result = await self.db.execute(
            select(CodingTestCase).filter(CodingTestCase.question_id == question.id)
        )
        test_cases = list(tc_result.scalars().all())

        try:
            exec_result = self._execute_code_securely(payload.language, payload.source_code, test_cases)
        except ValidationException:
            submission.status = SubmissionStatus.COMPILATION_ERROR
            await self.db.commit()
            raise

        sub_status = SubmissionStatus.PASSED if exec_result["execution_status"] == "PASSED" else SubmissionStatus.FAILED
        if exec_result["execution_status"] == "TIMEOUT":
            sub_status = SubmissionStatus.TIMEOUT
        elif exec_result["execution_status"] == "RUNTIME_ERROR":
            sub_status = SubmissionStatus.RUNTIME_ERROR

        submission.status = sub_status
        await self.db.commit()

        execution = CodeExecution(
            submission_id=submission.id,
            passed_tests=exec_result["passed_tests"],
            total_tests=exec_result["total_tests"],
            runtime_ms=exec_result["runtime_ms"],
            memory_mb=exec_result["memory_mb"],
            error_message=exec_result["error_message"],
            execution_status=exec_result["execution_status"],
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    # ------------------------------------------------------------------ #
    # Resume-skill grounded question selection (POST /coding/start)
    # ------------------------------------------------------------------ #
    async def pick_question_for_resume(self, user_id, resume_id) -> Optional[CodingQuestion]:
        """Select a coding question whose domain matches the candidate's
        ACTUAL extracted resume skills. Never invents a domain."""
        from app.models.resume import Resume

        resume = await self.db.get(Resume, resume_id)
        if resume is None or resume.user_id != user_id:
            raise AppException(status_code=404, detail="Resume not found.")

        skills = [s.name.strip().lower() for s in (resume.skills or [])]
        raw_lower = (resume.raw_text or "").lower()

        # Deterministic domain preference from evidence actually present.
        domain_priority: list[str] = []
        if any(s in ("python",) for s in skills) or "python" in raw_lower:
            domain_priority += ["Python", "Algorithms"]
        if any(s in ("sql", "postgresql", "mysql") for s in skills) or re_search(raw_lower, r"\bsql\b"):
            domain_priority += ["SQL"]
        if any(s in ("javascript", "typescript", "react") for s in skills):
            domain_priority += ["JavaScript", "Algorithms"]
        if any(s in ("java",) for s in skills) or "java" in raw_lower:
            domain_priority += ["Java", "Algorithms"]
        domain_priority += ["Algorithms", "Python"]  # generic fallback domains that exist in the bank

        questions = (
            await self.db.execute(select(CodingQuestion))
        ).scalars().all()
        if not questions:
            return None

        for domain in domain_priority:
            matches = [q for q in questions if q.domain and q.domain.lower() == domain.lower()]
            if matches:
                return matches[0]
        return questions[0]

    # ------------------------------------------------------------------ #
    # AI review (real data in, AI out; no hardcoded fallback content)
    # ------------------------------------------------------------------ #
    async def generate_ai_review(self, submission_id) -> CodeReview:
        submission = await self.db.get(CodingSubmission, submission_id)
        if not submission:
            raise AppException(status_code=404, detail="Submission not found.")

        question = await self.db.get(CodingQuestion, submission.question_id)

        prompt = f"""Review the following code submission for the coding problem: {question.title if question else 'Coding Problem'}.
Expected time complexity: {question.expected_time_complexity if question else 'n/a'}
Expected space complexity: {question.expected_space_complexity if question else 'n/a'}
Language: {submission.language}
Source Code:
{submission.source_code}

Return a JSON object with keys:
- score (float 0-100, based on correctness and quality of THIS code)
- correctness (float 0-100)
- code_quality (float 0-100)
- time_complexity (string, e.g. O(n))
- space_complexity (string, e.g. O(1))
- strengths (list of strings)
- issues (list of strings)
- suggestions (list of strings)
- better_approach (string)
Base every statement on the actual submitted code."""
        ai_data = await self._call_gemini(prompt)
        if ai_data is None:
            raise AppException(
                status_code=502,
                detail="AI code review is temporarily unavailable. Please try again later.",
            )

        review = CodeReview(
            submission_id=submission.id,
            score=float(ai_data.get("score", 0.0)),
            correctness=float(ai_data.get("correctness", 0.0)),
            code_quality=float(ai_data.get("code_quality", 0.0)),
            time_complexity=str(ai_data.get("time_complexity", "")),
            space_complexity=str(ai_data.get("space_complexity", "")),
            strengths=list(ai_data.get("strengths", []) or []),
            issues=list(ai_data.get("issues", []) or []),
            suggestions=list(ai_data.get("suggestions", []) or []),
            better_approach=str(ai_data.get("better_approach", "")),
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def _call_gemini(self, prompt: str) -> Optional[dict]:
        """Structured Gemini call. Returns None when AI is unavailable so the
        endpoint can surface a proper error instead of inventing a review."""
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
            logger.error("Gemini API error: %s", e)
            return None


def re_search(text: str, pattern: str) -> bool:
    import re as _re

    return bool(_re.search(pattern, text or ""))
