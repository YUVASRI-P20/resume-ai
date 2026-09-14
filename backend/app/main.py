"""
FastAPI application factory / entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8001

Wiring order matters here:
  1. logging is configured first so startup itself is logged
  2. middleware is added innermost-to-outermost as FastAPI executes it
     in reverse registration order for requests
  3. exception handlers before routers, so every router can rely on them
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.middleware.exception_handlers import _error_body, register_exception_handlers
from app.middleware.logging_middleware import AccessLogMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.utils.rate_limiter import limiter

configure_logging()
logger = get_logger(__name__)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Render 429s in the standard error envelope.

    slowapi's default handler returns `{"error": "<string>"}`, which
    clients that expect `{ error: { message } }` cannot parse — the user
    sees a generic "Something went wrong" instead of the real reason.
    """
    return JSONResponse(
        status_code=429,
        content=_error_body(
            "rate_limit_exceeded",
            "Too many requests. Please wait a minute and try again.",
        ),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s [%s]", settings.PROJECT_NAME, settings.ENVIRONMENT)

    # Zero-setup local run: create tables + seed roles/companies when the
    # database is empty. Postgres deployments use alembic migrations instead;
    # this bootstrap is a no-op on an existing, populated database.
    if "sqlite" in str(settings.DATABASE_URL):
        try:
            from app.database.bootstrap import bootstrap_dev_database

            await bootstrap_dev_database()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Dev database bootstrap skipped: %s", exc)

    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Your Personal AI Technical Interview Coach — resume-to-role matching, adaptive AI interviews, feedback, knowledge gaps and learning roadmaps.",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # --- Rate limiting ---
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # --- Middleware (added in reverse-execution order) ---
    cors_kwargs: dict = {
        "allow_origins": [str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": ["X-Request-ID"],
    }
    # Local dev convenience: accept any loopback origin (any port) so that
    # port juggling (Next.js falling back to 3001/3002, squatted ports, etc.)
    # never breaks the browser flow. Restricted to ENVIRONMENT=local.
    if settings.ENVIRONMENT == "local":
        cors_kwargs["allow_origin_regex"] = settings.CORS_ALLOW_ORIGIN_REGEX
    app.add_middleware(CORSMiddleware, **cors_kwargs)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # --- Exception handling ---
    register_exception_handlers(app)

    # --- Routers ---
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
