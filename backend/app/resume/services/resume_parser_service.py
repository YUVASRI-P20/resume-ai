"""
Module 3 — resume text extraction.

Text extraction uses PyMuPDF (fitz) as the primary engine (fast, reliable
layout order) and falls back to pdfplumber if PyMuPDF yields little/no text
(common for certain PDF generators). Structured section extraction (contact
info, skills, education, etc.) is delegated to the AI layer (Module 4's
Gemini client) via `ResumeExtractionAI`, since regex-only extraction is
unreliable across resume formats -- this function only prepares clean raw
text plus a few regex-based contact-info fallbacks.
"""
from __future__ import annotations

import io
import re

import fitz  # PyMuPDF
import pdfplumber

from app.core.exceptions import FileValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
_LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/[A-Za-z0-9\-_/]+", re.IGNORECASE)
_GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_/]+", re.IGNORECASE)

MIN_VIABLE_TEXT_LENGTH = 40


def _extract_with_pymupdf(content: bytes) -> str:
    text_parts: list[str] = []
    with fitz.open(stream=content, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts).strip()


def _extract_with_pdfplumber(content: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def _extract_with_docx(content: bytes) -> str:
    """Extract text from a DOCX (Word) resume using python-docx."""
    from docx import Document  # imported lazily: only needed for DOCX uploads

    document = Document(io.BytesIO(content))
    parts: list[str] = [p.text for p in document.paragraphs if p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            row_text = " ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                parts.append(row_text)
    return "\n".join(parts).strip()


def _extract_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore").strip()


def extract_raw_text_any(content: bytes, filename: str) -> str:
    """Dispatch text extraction by file extension: PDF, DOCX, or TXT."""
    from app.resume.utils.file_validation import FileValidationError  # local to avoid cycles

    lower = filename.lower()
    if lower.endswith(".docx"):
        text = _extract_with_docx(content)
    elif lower.endswith(".txt"):
        text = _extract_txt(content)
    else:
        text = extract_raw_text(content)  # PDF engines with fallbacks

    if len(text) < MIN_VIABLE_TEXT_LENGTH:
        raise FileValidationError(
            "Could not extract readable text from this file. It may be a scanned "
            "image, corrupted, or empty."
        )
    return text


def extract_raw_text(content: bytes) -> str:
    """Extract raw text from a PDF's bytes, trying PyMuPDF first, then pdfplumber."""
    try:
        text = _extract_with_pymupdf(content)
    except Exception as exc:  # noqa: BLE001
        logger.warning("PyMuPDF extraction failed: %s", exc)
        text = ""

    if len(text) < MIN_VIABLE_TEXT_LENGTH:
        try:
            fallback_text = _extract_with_pdfplumber(content)
            if len(fallback_text) > len(text):
                text = fallback_text
        except Exception as exc:  # noqa: BLE001
            logger.warning("pdfplumber extraction failed: %s", exc)

    if len(text) < MIN_VIABLE_TEXT_LENGTH:
        raise FileValidationError(
            "Could not extract readable text from this PDF. It may be a scanned "
            "image or corrupted file."
        )
    return text


def extract_contact_fallbacks(raw_text: str) -> dict:
    """Cheap regex-based contact extraction, used as a fallback / cross-check
    alongside AI extraction (Module 4)."""
    email_match = _EMAIL_RE.search(raw_text)
    phone_match = _PHONE_RE.search(raw_text)
    linkedin_match = _LINKEDIN_RE.search(raw_text)
    github_match = _GITHUB_RE.search(raw_text)
    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin_url": linkedin_match.group(0) if linkedin_match else None,
        "github_url": github_match.group(0) if github_match else None,
    }
