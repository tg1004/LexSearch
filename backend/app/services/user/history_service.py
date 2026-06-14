from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_history import SearchHistory

logger = logging.getLogger(__name__)

MAX_HISTORY_ITEMS = 50


async def save_search_history(
    db: AsyncSession,
    user_id: UUID,
    query: str,
    provider_used: str | None,
    result_count: int,
) -> None:
    entry = SearchHistory(
        user_id=user_id,
        query=query.strip(),
        provider_used=provider_used,
        result_count=result_count,
    )
    db.add(entry)
    await db.flush()

    subquery = (
        select(SearchHistory.id)
        .where(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.searched_at.desc())
        .offset(MAX_HISTORY_ITEMS)
    )
    stale_ids = (await db.execute(subquery)).scalars().all()
    if stale_ids:
        await db.execute(delete(SearchHistory).where(SearchHistory.id.in_(stale_ids)))


async def list_search_history(db: AsyncSession, user_id: UUID) -> list[SearchHistory]:
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.searched_at.desc())
        .limit(MAX_HISTORY_ITEMS)
    )
    return list(result.scalars().all())


async def delete_search_history_entry(db: AsyncSession, user_id: UUID, entry_id: UUID) -> bool:
    result = await db.execute(
        select(SearchHistory).where(
            SearchHistory.id == entry_id,
            SearchHistory.user_id == user_id,
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        return False
    await db.delete(entry)
    return True


async def clear_search_history(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        delete(SearchHistory).where(SearchHistory.user_id == user_id).returning(SearchHistory.id)
    )
    return len(result.scalars().all())
