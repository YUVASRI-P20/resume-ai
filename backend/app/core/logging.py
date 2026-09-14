"""
Application-wide logging configuration.

Provides a consistent, structured log format across the app, including
the per-request correlation ID injected by the RequestIDMiddleware.
"""
import logging
import sys
from contextvars import ContextVar

from app.core.config import settings

# Holds the current request's correlation ID so it can be woven into
# every log line emitted while handling that request.
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Injects the active request ID into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get()
        return True


def configure_logging() -> None:
    """Configure root logging handlers/formatters. Call once at startup."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.LOG_JSON:
        fmt = (
            '{"time": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "request_id": "%(request_id)s", '
            '"message": "%(message)s"}'
        )
    else:
        fmt = (
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "req_id=%(request_id)s | %(message)s"
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Quiet down noisy third-party loggers unless we're debugging.
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy_logger).setLevel(
            log_level if settings.DEBUG else logging.WARNING
        )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
