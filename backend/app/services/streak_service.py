"""
Streak service — real, per-user login streaks.

- record_login(user_id): called on every successful login. Inserts a
  LoginEvent and updates UserStreak:
    * first ever login  -> streak_days = 1  ("Day 1")
    * activity today    -> unchanged
    * yesterday         -> +1
    * older gap         -> reset to 1
- get_streak(user_id): read the current state (creates Day-0 state lazily
  for users who registered but the login event write was skipped).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.streak import LoginEvent, UserStreak

logger = get_logger(__name__)


def _today() -> date:
    return datetime.now(timezone.utc).date()


async def record_login(
    db: AsyncSession,
    user_id: uuid.UUID,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> UserStreak:
    """Record a login event and advance the user's streak.

    Flushes but does NOT commit — the caller owns transaction boundaries
    (this keeps it safe to embed inside the login flow with a savepoint).
    Returns the updated (or newly created) streak row.
    """
    today = _today()

    db.add(LoginEvent(user_id=user_id, login_date=today, ip_address=ip_address, user_agent=user_agent))

    streak = (await db.execute(select(UserStreak).where(UserStreak.user_id == user_id))).scalar_one_or_none()
    if streak is None:
        streak = UserStreak(user_id=user_id, streak_days=1, longest_streak_days=1, last_activity_date=today)
        db.add(streak)
        await db.flush()
        return streak

    last = streak.last_activity_date
    if last == today:
        pass  # same-day repeat: no change
    elif last == today - timedelta(days=1):
        streak.streak_days += 1
        streak.longest_streak_days = max(streak.longest_streak_days, streak.streak_days)
        streak.last_activity_date = today
    else:
        streak.streak_days = 1
        streak.last_activity_date = today

    await db.flush()
    return streak


async def get_streak(db: AsyncSession, user_id: uuid.UUID) -> dict:
    """Return the user's streak as a plain dict (never cross-user)."""
    streak = (await db.execute(select(UserStreak).where(UserStreak.user_id == user_id))).scalar_one_or_none()
    if streak is None:
        return {
            "streak_days": 0,
            "longest_streak_days": 0,
            "last_activity_date": None,
        }
    return {
        "streak_days": streak.streak_days,
        "longest_streak_days": streak.longest_streak_days,
        "last_activity_date": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
    }
