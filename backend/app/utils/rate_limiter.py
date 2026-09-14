"""
Rate limiting, backed by slowapi (a Flask-Limiter-style wrapper around
FastAPI). Keyed by client IP by default. Auth endpoints use a tighter
limit (RATE_LIMIT_AUTH) to blunt credential-stuffing / brute force.

If RATE_LIMIT_ENABLED is False, the limiter is still installed (so
`@limiter.limit(...)` decorators remain valid) but slowapi's own
`enabled` flag suppresses actual throttling — handy for local dev/tests.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    enabled=settings.RATE_LIMIT_ENABLED,
)
