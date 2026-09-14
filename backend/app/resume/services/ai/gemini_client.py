"""
Dedicated AI service layer for Gemini.

- Never exposes the API key to callers/responses.
- Centralizes retry logic and error handling.
- Returns raw JSON (dict) parsed from the model's response; callers validate
  with their own Pydantic schema (see app/schemas/ai.py).
"""
from __future__ import annotations

import json
import re
import time
from typing import Any

try:
    import google.generativeai as genai
except ImportError:  # Optional until GEMINI_API_KEY is configured.
    genai = None

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)

_configured = False


def _ensure_configured() -> None:
    global _configured
    if not _configured:
        if genai is None:
            raise AIServiceError("Gemini SDK is not installed.")
        if not settings.GEMINI_API_KEY:
            raise AIServiceError("AI service is not configured (missing GEMINI_API_KEY).")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True


def _strip_code_fences(text: str) -> str:
    """Gemini sometimes wraps JSON in ```json ... ``` fences; strip them defensively."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def generate_structured_json(
    prompt: str,
    *,
    temperature: float = 0.3,
    max_retries: int | None = None,
) -> dict[str, Any]:
    """
    Calls Gemini with the given prompt, expecting a single JSON object back.
    Retries on transient failures and malformed JSON (asking implicitly via
    retry, not by re-prompting differently, to keep this generic).

    Raises AIServiceError if the model cannot be reached or never returns
    parseable JSON within the retry budget.
    """
    _ensure_configured()
    retries = max_retries if max_retries is not None else settings.GEMINI_MAX_RETRIES

    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        generation_config={
            "temperature": temperature,
            "response_mime_type": "application/json",
        },
    )

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = model.generate_content(
                prompt,
                request_options={"timeout": settings.GEMINI_TIMEOUT_SECONDS},
            )
            raw_text = (response.text or "").strip()
            if not raw_text:
                raise ValueError("Empty response from AI model.")
            cleaned = _strip_code_fences(raw_text)
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            last_error = exc
            logger.warning("Gemini returned malformed JSON (attempt %s/%s): %s", attempt, retries, exc)
        except Exception as exc:  # noqa: BLE001 - broad: network, quota, safety-block, etc.
            last_error = exc
            logger.warning("Gemini call failed (attempt %s/%s): %s", attempt, retries, exc)

        if attempt < retries:
            time.sleep(min(2 ** attempt, 8))  # exponential backoff, capped

    raise AIServiceError(f"AI service failed after {retries} attempts: {last_error}")
