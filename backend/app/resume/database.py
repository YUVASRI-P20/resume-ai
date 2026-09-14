"""Synchronous SQLAlchemy session used by the legacy synchronous resume/optimizer services.
It points at the SAME DATABASE_URL as the canonical async application database.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

def _sync_url(url: str) -> str:
    return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1).replace("sqlite+aiosqlite://", "sqlite://", 1)

engine = create_engine(_sync_url(settings.DATABASE_URL), pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

SyncDbSession = Session
