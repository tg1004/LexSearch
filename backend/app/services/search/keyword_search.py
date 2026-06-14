"""Elasticsearch BM25 keyword search with metadata filters."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from elasticsearch import AsyncElasticsearch

from app.config import Settings, get_settings
from app.schemas.search import SearchFilters
from app.services.search.filter_builder import KEYWORD_TOP_K, build_elasticsearch_filters
from app.services.search.models import ChunkResult

logger = logging.getLogger(__name__)


class KeywordSearch:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        client_kwargs: dict[str, Any] = {"request_timeout": 30}
        if self.settings.elasticsearch_api_key_or_none:
            client_kwargs["api_key"] = self.settings.elasticsearch_api_key_or_none
        elif self.settings.elasticsearch_basic_auth:
            client_kwargs["basic_auth"] = self.settings.elasticsearch_basic_auth
        self.client = AsyncElasticsearch(self.settings.elasticsearch_url, **client_kwargs)

    async def search(
        self,
        query: str,
        filters: SearchFilters,
        top_k: int = KEYWORD_TOP_K,
    ) -> list[ChunkResult]:
        es_filters = build_elasticsearch_filters(filters)
        bool_query: dict[str, Any] = {
            "must": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["chunk_text^2", "title"],
                        "type": "best_fields",
                    }
                }
            ],
        }
        if es_filters:
            bool_query["filter"] = es_filters

        body = {
            "query": {"bool": bool_query},
            "size": top_k,
        }

        try:
            response = await self.client.search(index=self.settings.elasticsearch_index, body=body)
        except Exception as exc:
            logger.error("Elasticsearch search failed: %s", exc)
            return []

        results: list[ChunkResult] = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            date_value = source.get("date")
            results.append(
                ChunkResult(
                    document_id=str(source.get("document_id", "")),
                    chunk_index=int(source.get("chunk_index", 0)),
                    text=str(source.get("chunk_text", "")),
                    title=str(source.get("title", "")),
                    court=source.get("court"),
                    date=str(date_value)[:10] if date_value else None,
                    case_type=source.get("case_type"),
                    score=float(hit.get("_score") or 0.0),
                )
            )
        return results

    async def close(self) -> None:
        await self.client.close()


@lru_cache
def get_keyword_search() -> KeywordSearch:
    return KeywordSearch()


async def close_keyword_search() -> None:
    if get_keyword_search.cache_info().currsize:
        await get_keyword_search().close()
        get_keyword_search.cache_clear()
