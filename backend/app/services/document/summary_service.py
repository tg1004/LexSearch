from __future__ import annotations

import logging

from app.config import Settings, get_settings
from app.services.cache.redis_cache import RedisCache
from app.services.llm.llm_service import AllProvidersFailedError, LLMService, get_llm_service

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """You are a legal research assistant specializing in Indian law.

Summarize the judgement below in 3 to 5 clear sentences for a law student or practicing lawyer.

Include:
1. Who the parties are (if stated)
2. The main legal issue or question before the court
3. The court's key reasoning or legal test applied
4. The outcome (allowed, dismissed, remanded, etc.) if stated

Rules:
- Use ONLY information from the judgement text below
- Write in plain English, not legalese
- Do not invent facts, case names, or outcomes
- Keep the summary under 120 words

JUDGEMENT TEXT (excerpt):
{text_excerpt}

Summary:"""

MAX_SUMMARY_INPUT_CHARS = 12000


class SummaryService:
    def __init__(
        self,
        llm_service: LLMService | None = None,
        redis_cache: RedisCache | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.llm_service = llm_service or get_llm_service()
        self.redis_cache = redis_cache
        self.settings = settings or get_settings()

    def _cache_key(self, document_id: str) -> str:
        return f"lexsearch:summary:{document_id}"

    async def get_cached_summary(self, document_id: str) -> str | None:
        if not self.redis_cache:
            return None
        try:
            return await self.redis_cache.redis.get(self._cache_key(document_id))
        except Exception as exc:
            logger.warning("Summary cache read failed: %s", exc)
            return None

    async def cache_summary(self, document_id: str, summary: str) -> None:
        if not self.redis_cache:
            return
        try:
            await self.redis_cache.redis.setex(
                self._cache_key(document_id),
                self.settings.document_summary_cache_ttl_seconds,
                summary,
            )
        except Exception as exc:
            logger.warning("Summary cache write failed: %s", exc)

    async def generate_summary(self, document_id: str, full_text: str) -> tuple[str, str | None]:
        cached = await self.get_cached_summary(document_id)
        if cached:
            return cached, None

        excerpt = full_text[:MAX_SUMMARY_INPUT_CHARS]
        if len(full_text) > MAX_SUMMARY_INPUT_CHARS:
            excerpt += "\n\n[Text truncated for summary generation]"

        prompt = SUMMARY_PROMPT.format(text_excerpt=excerpt)

        try:
            llm_response = await self.llm_service.generate(prompt)
            summary = llm_response.text.strip()
            await self.cache_summary(document_id, summary)
            return summary, llm_response.provider
        except AllProvidersFailedError as exc:
            logger.error("Summary generation failed for %s: %s", document_id, exc.errors)
            raise
