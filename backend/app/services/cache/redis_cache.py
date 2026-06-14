from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import Settings, get_settings
from app.schemas.search import SearchFilters, SearchResponse

logger = logging.getLogger(__name__)


def _normalized_filters_dump(filters: SearchFilters) -> dict:
    data = filters.model_dump()
    for key in ("court", "case_type", "outcome"):
        if data.get(key):
            data[key] = sorted(set(data[key]))
    return data


def build_search_cache_key(
    query: str,
    filters: SearchFilters,
    preferred_provider: str | None,
    page: int,
) -> str:
    payload = {
        "query": query.strip().lower(),
        "filters": _normalized_filters_dump(filters),
        "preferred_provider": (preferred_provider or "auto").lower(),
        "page": page,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()
    return f"lexsearch:search:{digest}"


class RedisCache:
    def __init__(self, redis_client: aioredis.Redis, settings: Settings | None = None) -> None:
        self.redis = redis_client
        self.settings = settings or get_settings()

    async def get_search_response(self, key: str) -> SearchResponse | None:
        try:
            raw = await self.redis.get(key)
            if not raw:
                return None
            data: dict[str, Any] = json.loads(raw)
            return SearchResponse.model_validate(data)
        except Exception as exc:
            logger.warning("Redis cache read failed: %s", exc)
            return None

    async def set_search_response(self, key: str, response: SearchResponse) -> None:
        try:
            await self.redis.setex(
                key,
                self.settings.search_cache_ttl_seconds,
                response.model_dump_json(),
            )
        except Exception as exc:
            logger.warning("Redis cache write failed: %s", exc)
