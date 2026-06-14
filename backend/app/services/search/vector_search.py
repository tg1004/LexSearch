"""Qdrant vector search with metadata filters."""

from __future__ import annotations

import logging
from functools import lru_cache

from qdrant_client import AsyncQdrantClient

from app.config import Settings, get_settings
from app.schemas.search import SearchFilters
from app.services.search.filter_builder import (
    VECTOR_TOP_K,
    build_qdrant_filter,
    matches_year_filter,
    normalized_year_bounds,
)
from app.services.search.models import ChunkResult

logger = logging.getLogger(__name__)


class VectorSearch:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        api_key = self.settings.qdrant_api_key_or_none
        self.client = AsyncQdrantClient(url=self.settings.qdrant_url, api_key=api_key)

    async def search(
        self,
        embedding: list[float],
        filters: SearchFilters,
        top_k: int = VECTOR_TOP_K,
    ) -> list[ChunkResult]:
        query_filter = build_qdrant_filter(filters)
        year_from, year_to = normalized_year_bounds(filters)

        # Fetch extra candidates when year post-filtering is active.
        fetch_limit = top_k * 3 if (year_from is not None or year_to is not None) else top_k

        try:
            points = await self.client.search(
                collection_name=self.settings.qdrant_collection_name,
                query_vector=embedding,
                query_filter=query_filter,
                limit=fetch_limit,
                with_payload=True,
            )
        except Exception as exc:
            logger.error("Qdrant search failed: %s", exc)
            return []

        results: list[ChunkResult] = []
        for point in points:
            payload = point.payload or {}
            date_value = payload.get("date")
            if not matches_year_filter(
                str(date_value) if date_value is not None else None,
                year_from,
                year_to,
            ):
                continue

            results.append(
                ChunkResult(
                    document_id=str(payload.get("document_id", "")),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    text=str(payload.get("text", "")),
                    title=str(payload.get("title", "")),
                    court=payload.get("court"),
                    date=str(date_value) if date_value is not None else None,
                    case_type=payload.get("case_type"),
                    score=float(point.score or 0.0),
                )
            )
            if len(results) >= top_k:
                break

        return results

    async def close(self) -> None:
        await self.client.close()


@lru_cache
def get_vector_search() -> VectorSearch:
    return VectorSearch()


async def close_vector_search() -> None:
    if get_vector_search.cache_info().currsize:
        await get_vector_search().close()
        get_vector_search.cache_clear()
