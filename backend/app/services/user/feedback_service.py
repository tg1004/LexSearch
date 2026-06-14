from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback


async def create_feedback(
    db: AsyncSession,
    query: str,
    is_helpful: bool,
    provider_used: str | None,
    user_id: UUID | None = None,
) -> Feedback:
    entry = Feedback(
        user_id=user_id,
        query=query.strip(),
        is_helpful=is_helpful,
        provider_used=provider_used,
    )
    db.add(entry)
    await db.flush()
    return entry
