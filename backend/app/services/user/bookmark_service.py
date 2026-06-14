from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bookmark import Bookmark
from app.models.document_meta import Document


async def list_bookmarks(db: AsyncSession, user_id: UUID) -> list[tuple[Bookmark, Document | None]]:
    result = await db.execute(
        select(Bookmark, Document)
        .outerjoin(Document, Bookmark.document_id == Document.id)
        .where(Bookmark.user_id == user_id)
        .order_by(Bookmark.folder_name.asc(), Bookmark.created_at.desc())
    )
    return list(result.all())


async def get_bookmark(db: AsyncSession, user_id: UUID, bookmark_id: UUID) -> Bookmark | None:
    result = await db.execute(
        select(Bookmark)
        .options(selectinload(Bookmark.document))
        .where(Bookmark.id == bookmark_id, Bookmark.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_bookmark(
    db: AsyncSession,
    user_id: UUID,
    document_id: str,
    folder_name: str,
    notes: str | None,
) -> Bookmark:
    bookmark = Bookmark(
        user_id=user_id,
        document_id=document_id,
        folder_name=folder_name.strip() or "General",
        notes=notes,
    )
    db.add(bookmark)
    await db.flush()
    await db.refresh(bookmark)
    return bookmark


async def update_bookmark(
    db: AsyncSession,
    bookmark: Bookmark,
    folder_name: str | None,
    notes: str | None,
) -> Bookmark:
    if folder_name is not None:
        bookmark.folder_name = folder_name.strip() or "General"
    if notes is not None:
        bookmark.notes = notes
    await db.flush()
    await db.refresh(bookmark)
    return bookmark


async def delete_bookmark(db: AsyncSession, bookmark: Bookmark) -> None:
    await db.delete(bookmark)
