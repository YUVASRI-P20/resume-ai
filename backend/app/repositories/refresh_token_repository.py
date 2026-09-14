from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken, replaced_by_hash: str | None = None) -> None:
        token.revoked = True
        if replaced_by_hash:
            token.replaced_by_token_hash = replaced_by_hash
        await self.session.flush()

    async def revoke_all_for_user(self, user_id) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True)
        )
        await self.session.flush()

    async def purge_expired(self) -> int:
        """Delete expired/revoked tokens. Intended for a periodic Celery job."""
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(RefreshToken).where(
                (RefreshToken.expires_at < now) | (RefreshToken.revoked.is_(True))
            )
        )
        stale = result.scalars().all()
        for token in stale:
            await self.session.delete(token)
        await self.session.flush()
        return len(stale)
