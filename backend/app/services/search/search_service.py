"""Orchestrates hybrid search: embed → parallel vector + BM25 → RRF merge."""

from __future__ import annotations

import asyncio
import logging

from app.schemas.search import SearchFilters
from app.services.search.embedder import get_embedder
from app.services.search.filter_builder import (
    KEYWORD_TOP_K,
    MAX_RETRIEVE_K,
    RAG_TOP_K,
    RESULTS_PER_PAGE,
    VECTOR_TOP_K,
)
from app.services.search.hybrid_merger import reciprocal_rank_fusion
from app.services.search.keyword_search import KeywordSearch, get_keyword_search
from app.services.search.models import ChunkResult
from app.services.search.vector_search import VectorSearch, get_vector_search
from app.utils.text_utils import clean_query_text

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        vector_search: VectorSearch | None = None,
        keyword_search: KeywordSearch | None = None,
    ) -> None:
        self.embedder = get_embedder()
        self.vector_search = vector_search or get_vector_search()
        self.keyword_search = keyword_search or get_keyword_search()

    async def _retrieve_merged(self, query: str, filters: SearchFilters) -> list[ChunkResult]:
        cleaned_query = clean_query_text(query)
        if not cleaned_query:
            return []

        embedding = await self.embedder.embed_query(cleaned_query)
        retrieve_k = min(max(VECTOR_TOP_K, KEYWORD_TOP_K), MAX_RETRIEVE_K)

        vector_results, keyword_results = await asyncio.gather(
            self.vector_search.search(embedding, filters, top_k=retrieve_k),
            self.keyword_search.search(cleaned_query, filters, top_k=retrieve_k),
        )

        if not vector_results and not keyword_results:
            logger.info("No results from Qdrant or Elasticsearch for query: %s", cleaned_query)
            return []

        return reciprocal_rank_fusion([vector_results, keyword_results])

    async def retrieve_for_search(
        self,
        query: str,
        filters: SearchFilters,
        page: int = 1,
    ) -> tuple[list[ChunkResult], list[ChunkResult], int]:
        """
        Hybrid retrieve + RRF merge.
        Returns (sources_page, rag_chunks, total_merged_count).
        RAG always uses global top RAG_TOP_K; sources are paginated separately.
        """
        merged = await self._retrieve_merged(query, filters)
        if not merged:
            return [], [], 0

        rag_chunks = merged[:RAG_TOP_K]
        start = (page - 1) * RESULTS_PER_PAGE
        end = start + RESULTS_PER_PAGE
        return merged[start:end], rag_chunks, len(merged)

    async def retrieve_chunks(
        self,
        query: str,
        filters: SearchFilters,
        page: int = 1,
    ) -> tuple[list[ChunkResult], int]:
        """Backward-compatible: returns paginated sources only."""
        sources_page, _, total_count = await self.retrieve_for_search(query, filters, page)
        return sources_page, total_count


def get_search_service() -> SearchService:
    return SearchService()
