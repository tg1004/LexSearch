from __future__ import annotations

import logging
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_meta import Document
from app.schemas.document import DocumentResponse, HighlightResponse
from app.services.document.document_store import DocumentStore, StoredChunk, get_document_store
from app.services.document.elasticsearch_store import (
    ElasticsearchDocumentStore,
    get_elasticsearch_document_store,
)

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


def _coerce_judges(value: object) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return [str(value)]


def _parse_date(value: object) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _document_from_es_metadata(
    document_id: str,
    metadata: dict,
    full_text: str,
    cached_summary: str | None,
) -> DocumentResponse:
    judges = _coerce_judges(metadata.get("judges"))
    return DocumentResponse(
        id=document_id,
        title=str(metadata.get("title") or document_id)[:500],
        court=metadata.get("court"),
        date=_parse_date(metadata.get("date")),
        judges=judges,
        case_type=metadata.get("case_type"),
        outcome=metadata.get("outcome"),
        bench_size=derive_bench_size(judges),
        full_text=full_text,
        summary=cached_summary,
        url=metadata.get("url"),
    )


class DocumentService:
    def __init__(
        self,
        store: DocumentStore | None = None,
        es_store: ElasticsearchDocumentStore | None = None,
    ) -> None:
        self.store = store or get_document_store()
        self.es_store = es_store or get_elasticsearch_document_store()

    async def _resolve_full_text(self, document_id: str) -> str | None:
        text = self.store.get_full_text(document_id)
        if text:
            return text
        return await self.es_store.get_full_text(document_id)

    async def _resolve_chunk(self, document_id: str, chunk_index: int) -> StoredChunk | None:
        chunk = self.store.get_chunk(document_id, chunk_index)
        if chunk:
            return chunk
        return await self.es_store.get_chunk(document_id, chunk_index)

    async def get_document(
        self,
        db: AsyncSession,
        document_id: str,
        cached_summary: str | None = None,
    ) -> DocumentResponse:
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        full_text = await self._resolve_full_text(document_id)
        es_meta = None
        if not full_text or document is None:
            es_meta = await self.es_store.get_document_metadata(document_id)
            if not full_text and es_meta is not None:
                full_text = await self.es_store.get_full_text(document_id)

        if not full_text:
            if document is None and es_meta is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document text not available",
            )

        if document is None:
            if es_meta is None:
                es_meta = await self.es_store.get_document_metadata(document_id)
            if es_meta is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            return _document_from_es_metadata(document_id, es_meta, full_text, cached_summary)

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

    async def get_highlight(self, document_id: str, chunk_index: int) -> HighlightResponse:
        chunk = await self._resolve_chunk(document_id, chunk_index)
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
