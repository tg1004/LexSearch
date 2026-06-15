from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document_meta import Document
from app.models.user import User
from app.schemas.bookmark import BookmarkCreate, BookmarkListResponse, BookmarkResponse, BookmarkUpdate
from app.services.document.document_service import ensure_document_record
from app.services.user import bookmark_service
from app.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


def _to_response(bookmark, document: Document | None = None) -> BookmarkResponse:
    doc = document or getattr(bookmark, "document", None)
    return BookmarkResponse(
        id=bookmark.id,
        document_id=bookmark.document_id,
        folder_name=bookmark.folder_name,
        notes=bookmark.notes,
        created_at=bookmark.created_at,
        title=doc.title if doc else None,
        court=doc.court if doc else None,
        date=doc.date.isoformat() if doc and doc.date else None,
    )


@router.get("", response_model=BookmarkListResponse)
async def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookmarkListResponse:
    rows = await bookmark_service.list_bookmarks(db, current_user.id)
    items = [_to_response(bookmark, document) for bookmark, document in rows]
    folders = sorted({item.folder_name for item in items})
    if "General" not in folders:
        folders.insert(0, "General")
    return BookmarkListResponse(items=items, folders=folders)


@router.post("", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    body: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookmarkResponse:
    doc = await ensure_document_record(db, body.document_id)
    bookmark = await bookmark_service.create_bookmark(
        db,
        current_user.id,
        body.document_id,
        body.folder_name,
        body.notes,
    )
    return _to_response(bookmark, doc)


@router.patch("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: UUID,
    body: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookmarkResponse:
    bookmark = await bookmark_service.get_bookmark(db, current_user.id, bookmark_id)
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    updated = await bookmark_service.update_bookmark(db, bookmark, body.folder_name, body.notes)
    doc = None
    if updated.document_id:
        doc = (await db.execute(select(Document).where(Document.id == updated.document_id))).scalar_one_or_none()
    return _to_response(updated, doc)


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    bookmark = await bookmark_service.get_bookmark(db, current_user.id, bookmark_id)
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    await bookmark_service.delete_bookmark(db, bookmark)
