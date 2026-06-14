from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_meta import Document
from app.schemas.document import DocumentResponse, HighlightResponse
from app.services.document.document_store import DocumentStore, get_document_store

logger = logging.getLogger(__name__)


def derive_bench_size(judges: list[str] | None) -> str | None:
    if not judges:
        return None
    count = len(judges)
    if count == 1:
        return "Single Judge"
    if count == 2:
        return "Division Bench"
    if count >= 3:
        return "Full Bench"
    return None


class DocumentService:
    def __init__(self, store: DocumentStore | None = None) -> None:
        self.store = store or get_document_store()

    async def get_document(
        self,
        db: AsyncSession,
        document_id: str,
        cached_summary: str | None = None,
    ) -> DocumentResponse:
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        full_text = self.store.get_full_text(document_id)
        if not full_text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document text not available",
            )

        judges = document.judges or []
        return DocumentResponse(
            id=document.id,
            title=document.title,
            court=document.court,
            date=document.date,
            judges=judges,
            case_type=document.case_type,
            outcome=document.outcome,
            bench_size=derive_bench_size(judges),
            full_text=full_text,
            summary=cached_summary,
            url=document.url,
        )

    def get_highlight(self, document_id: str, chunk_index: int) -> HighlightResponse:
        chunk = self.store.get_chunk(document_id, chunk_index)
        if chunk is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk not found")

        return HighlightResponse(
            document_id=document_id,
            chunk_index=chunk.chunk_index,
            highlighted_passage=chunk.text,
            position=chunk.char_start,
            char_end=chunk.char_end,
        )


def get_document_service() -> DocumentService:
    return DocumentService()
