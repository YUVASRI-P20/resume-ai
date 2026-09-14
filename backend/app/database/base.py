"""
Declarative base + common mixins shared by every ORM model.

Importing this module (directly or transitively via app.models) is what
registers all models on Base.metadata, which Alembic's env.py relies on
for autogenerate.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Project-wide declarative base.
    Allow legacy non-Mapped annotations from earlier generated modules while
    preserving SQLAlchemy 2.x mapped attributes.
    """
    __allow_unmapped__ = True


class UUIDPrimaryKeyMixin:
    """Adds a UUID primary key, generated application-side via uuid4()."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )


class TimestampMixin:
    """Adds created_at / updated_at columns maintained by the database."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
