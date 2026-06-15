"""Fetch document text and chunks from Elasticsearch (production fallback)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from elasticsearch import AsyncElasticsearch

from app.config import Settings, get_settings
from app.services.document.document_store import StoredChunk

logger = logging.getLogger(__name__)


class ElasticsearchDocumentStore:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        client_kwargs: dict[str, Any] = {"request_timeout": 60}
        if self.settings.elasticsearch_api_key_or_none:
            client_kwargs["api_key"] = self.settings.elasticsearch_api_key_or_none
        elif self.settings.elasticsearch_basic_auth:
            client_kwargs["basic_auth"] = self.settings.elasticsearch_basic_auth
        self.client = AsyncElasticsearch(self.settings.elasticsearch_url, **client_kwargs)

    async def get_document_chunks(self, document_id: str) -> list[dict[str, Any]]:
        try:
            response = await self.client.search(
                index=self.settings.elasticsearch_index,
                body={
                    "query": {"term": {"document_id": document_id}},
                    "sort": [{"chunk_index": "asc"}],
                    "size": 5000,
                },
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception:
            logger.exception("Failed to fetch document chunks from Elasticsearch: %s", document_id)
            return []

    async def get_document_metadata(self, document_id: str) -> dict[str, Any] | None:
        chunks = await self.get_document_chunks(document_id)
        if not chunks:
            return None
        return chunks[0]

    async def get_full_text(self, document_id: str) -> str | None:
        chunks = await self.get_document_chunks(document_id)
        if not chunks:
            return None

        parts: list[str] = []
        last_end = 0
        for chunk in chunks:
            text = str(chunk.get("chunk_text", "")).strip()
            if not text:
                continue
            char_start = int(chunk.get("char_start", 0))
            if char_start >= last_end:
                parts.append(text)
                last_end = int(chunk.get("char_end", char_start + len(text)))
            elif text not in parts[-1]:
                parts.append(text)
        return "\n\n".join(parts) if parts else None

    async def get_chunk(self, document_id: str, chunk_index: int) -> StoredChunk | None:
        try:
            response = await self.client.search(
                index=self.settings.elasticsearch_index,
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"document_id": document_id}},
                                {"term": {"chunk_index": chunk_index}},
                            ]
                        }
                    },
                    "size": 1,
                },
            )
            hits = response["hits"]["hits"]
            if not hits:
                return None
            source = hits[0]["_source"]
            return StoredChunk(
                document_id=document_id,
                chunk_index=int(source.get("chunk_index", chunk_index)),
                text=str(source.get("chunk_text", "")),
                char_start=int(source.get("char_start", 0)),
                char_end=int(source.get("char_end", 0)),
            )
        except Exception:
            logger.exception(
                "Failed to fetch chunk %s:%s from Elasticsearch",
                document_id,
                chunk_index,
            )
            return None

    async def close(self) -> None:
        await self.client.close()


@lru_cache
def get_elasticsearch_document_store() -> ElasticsearchDocumentStore:
    return ElasticsearchDocumentStore()
