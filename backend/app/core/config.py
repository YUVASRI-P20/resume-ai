"""
Application configuration.

Centralized, typed settings loaded from environment variables via
pydantic-settings. Never hardcode secrets here — everything sensitive
comes from the environment (see .env.example).

Local-first defaults: if no .env is present the app still boots with a
sqlite database (no external services required) and the server port the
rest of this project standardizes on (8001).
"""
from functools import lru_cache
from typing import List, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- General ----
    PROJECT_NAME: str = "InterviewIQ AI"
    ENVIRONMENT: Literal["local", "development", "staging", "production"] = "local"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ---- Server ----
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # ---- Security / JWT ----
    # Dev-only fallback so `uvicorn app.main` works with no .env; always set
    # a real SECRET_KEY via the environment outside local development.
    SECRET_KEY: str = "dev-insecure-secret-key-change-me-in-env-0123456789abcdef"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # ---- Database ----
    # Defaults to sqlite for a zero-setup local run. Production deployments
    # should set a postgresql+asyncpg:// URL here.
    DATABASE_URL: str = "sqlite+aiosqlite:///./interviewiq.db"
    DATABASE_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ---- Redis / Celery ----
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ---- CORS ----
    # 3000/3001 are listed explicitly because Next.js dev auto-falls back to
    # 3001 when another process has already bound port 3000. Extra dev ports
    # are still accepted via allow_origin_regex below, which permits any
    # localhost / 127.0.0.1 / [::1] origin on any port. In production, set
    # BACKEND_CORS_ORIGINS explicitly and ENVIRONMENT != local so the regex
    # does not apply.
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    # Any loopback origin on any port (http or https), local dev only.
    CORS_ALLOW_ORIGIN_REGEX: str = (
        r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ---- Rate limiting ----
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "20/minute"

    # ---- Email (for verification / password reset) ----
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "noreply@interviewiq.ai"
    EMAILS_FROM_NAME: str = "InterviewIQ AI"
    EMAIL_ENABLED: bool = False
    # ---- Frontend ----
    FRONTEND_URL: str = "http://localhost:3000"

    # ---- Storage / Resume ----
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "storage/resumes"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_BUCKET: str = "resumes"
    MAX_RESUME_SIZE_MB: int = 10
    ALLOWED_RESUME_CONTENT_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    ALLOWED_RESUME_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]

    # ---- Gemini / AI ----
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_MAX_RETRIES: int = 3
    GEMINI_TIMEOUT_SECONDS: int = 60

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads the environment once per process."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
