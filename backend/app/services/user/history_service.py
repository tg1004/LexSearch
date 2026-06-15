from __future__ import annotations

import logging
from datetime import UTC, datetime
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
    normalized_query = query.strip()
    result = await db.execute(
        select(SearchHistory).where(
            SearchHistory.user_id == user_id,
            func.lower(SearchHistory.query) == normalized_query.lower(),
        ).order_by(SearchHistory.searched_at.desc())
    )
    matches = list(result.scalars().all())

    if matches:
        keeper = matches[0]
        keeper.query = normalized_query
        keeper.provider_used = provider_used
        keeper.result_count = result_count
        keeper.searched_at = datetime.now(UTC)
        for duplicate in matches[1:]:
            await db.delete(duplicate)
    else:
        db.add(
            SearchHistory(
                user_id=user_id,
                query=normalized_query,
                provider_used=provider_used,
                result_count=result_count,
            )
        )
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
        .limit(MAX_HISTORY_ITEMS * 2)
    )
    items = list(result.scalars().all())

    seen: set[str] = set()
    deduped: list[SearchHistory] = []
    for item in items:
        key = item.query.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= MAX_HISTORY_ITEMS:
            break
    return deduped


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
