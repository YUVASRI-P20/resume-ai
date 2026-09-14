import hashlib
import os
import re

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileValidationError

# PDF files start with this magic header
PDF_MAGIC = b"%PDF-"
# DOCX files are ZIP archives
DOCX_MAGIC = b"PK"

_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\-]")

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
_ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


def sanitize_filename(filename: str) -> str:
    """Strip path components and unsafe characters from a client-supplied filename."""
    base = os.path.basename(filename or "resume.pdf")
    base = _SAFE_FILENAME_RE.sub("_", base)
    ext = os.path.splitext(base)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        base += ".pdf"
    return base[:200]


def validate_extension(filename: str) -> None:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_RESUME_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file extension '{ext}'. Allowed: {', '.join(settings.ALLOWED_RESUME_EXTENSIONS)}."
        )


def validate_content_type(content_type: str | None) -> None:
    if content_type not in settings.ALLOWED_RESUME_CONTENT_TYPES:
        raise FileValidationError(
            f"Unsupported content type '{content_type}'. Allowed: {', '.join(settings.ALLOWED_RESUME_CONTENT_TYPES)}."
        )


def validate_size(size_bytes: int) -> None:
    max_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
    if size_bytes <= 0:
        raise FileValidationError("Uploaded file is empty.")
    if size_bytes > max_bytes:
        raise FileValidationError(f"File exceeds the maximum allowed size of {settings.MAX_RESUME_SIZE_MB}MB.")


def validate_magic_bytes(content: bytes, filename: str) -> None:
    """Verify the file content matches its declared type (not just the extension)."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf" and not content.startswith(PDF_MAGIC):
        raise FileValidationError("File content is not a valid PDF.")
    if ext == ".docx" and not content.startswith(DOCX_MAGIC):
        raise FileValidationError("File content is not a valid DOCX document.")
    # .txt accepts any decodable content


def compute_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def read_and_validate_upload(file: UploadFile) -> tuple[bytes, str]:
    """
    Fully validates an UploadFile (filename, content-type, size, magic bytes)
    and returns (raw_bytes, sanitized_filename). Raises FileValidationError on
    any failure.
    """
    validate_extension(file.filename or "")
    validate_content_type(file.content_type)

    content = await file.read()
    validate_size(len(content))
    validate_magic_bytes(content, os.path.basename(file.filename or "resume.pdf"))

    safe_name = sanitize_filename(file.filename or "resume.pdf")
    return content, safe_name
