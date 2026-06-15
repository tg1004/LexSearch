from __future__ import annotations

import json
import logging
import re
import uuid

from app.schemas.search import SearchFilters, SearchResponse, SourceResult
from app.services.cache.redis_cache import RedisCache, build_search_cache_key
from app.services.llm.llm_service import AllProvidersFailedError, LLMService, get_llm_service
from app.services.rag.citation_parser import parse_citations
from app.services.rag.prompt_builder import build_rag_prompt, build_related_questions_prompt
from app.services.search.filter_builder import normalized_year_bounds
from app.services.search.models import ChunkResult
from app.services.search.search_service import SearchService, get_search_service

logger = logging.getLogger(__name__)

NO_RESULTS_ANSWER = (
    "No results found for this query. Try broader terms, check spelling, or remove filters."
)
LLM_FAILURE_ANSWER = "Service temporarily unavailable, please try again."


class RAGService:
    def __init__(
        self,
        search_service: SearchService | None = None,
        llm_service: LLMService | None = None,
        redis_cache: RedisCache | None = None,
    ) -> None:
        self.search_service = search_service or get_search_service()
        self.llm_service = llm_service or get_llm_service()
        self.redis_cache = redis_cache

    async def search(
        self,
        query: str,
        filters: SearchFilters,
        page: int = 1,
        preferred_provider: str | None = None,
    ) -> SearchResponse:
        cache_key = build_search_cache_key(query, filters, preferred_provider, page)
        if self.redis_cache:
            cached = await self.redis_cache.get_search_response(cache_key)
            if cached:
                logger.info("Cache hit for search query")
                return cached.model_copy(update={"search_id": uuid.uuid4()})

        search_id = uuid.uuid4()
        sources_page, rag_chunks, total_count = await self.search_service.retrieve_for_search(
            query=query,
            filters=filters,
            page=page,
        )

        if not rag_chunks:
            response = SearchResponse(
                answer=NO_RESULTS_ANSWER,
                citations=[],
                sources=[],
                provider_used=None,
                related_questions=[],
                search_id=search_id,
                result_count=0,
            )
            return response

        prompt = build_rag_prompt(query, rag_chunks)

        try:
            llm_response = await self.llm_service.generate(prompt, preferred_provider=preferred_provider)
            parsed = parse_citations(llm_response.text, rag_chunks)
            answer = parsed.answer_text
            citations = parsed.citations
            provider_used = llm_response.provider
        except AllProvidersFailedError as exc:
            logger.error("All LLM providers failed: %s", exc.errors)
            answer = LLM_FAILURE_ANSWER
            citations = []
            provider_used = None

        sources = [self._chunk_to_source(chunk) for chunk in sources_page]

        related_questions: list[str] = []
        if (
            provider_used
            and answer
            and answer not in (NO_RESULTS_ANSWER, LLM_FAILURE_ANSWER)
            and not self._has_active_filters(filters)
        ):
            related_questions = await self._generate_related_questions(
                query, answer, preferred_provider
            )

        response = SearchResponse(
            answer=answer,
            citations=citations,
            sources=sources,
            provider_used=provider_used,
            related_questions=related_questions,
            search_id=search_id,
            result_count=total_count,
        )

        if self.redis_cache and provider_used:
            await self.redis_cache.set_search_response(cache_key, response)

        return response

    @staticmethod
    def _has_active_filters(filters: SearchFilters) -> bool:
        year_from, year_to = normalized_year_bounds(filters)
        return bool(filters.court or filters.case_type or filters.outcome or year_from or year_to)

    async def _generate_related_questions(
        self,
        query: str,
        answer: str,
        preferred_provider: str | None,
    ) -> list[str]:
        prompt = build_related_questions_prompt(query, answer)
        try:
            llm_response = await self.llm_service.generate(prompt, preferred_provider=preferred_provider)
            return self._parse_related_questions(llm_response.text)
        except AllProvidersFailedError:
            logger.warning("Could not generate related questions — all providers failed")
            return []
        except Exception:
            logger.exception("Failed to generate related questions")
            return []

    @staticmethod
    def _parse_related_questions(text: str) -> list[str]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                questions = [str(item).strip() for item in parsed if str(item).strip()]
                return questions[:4]
        except json.JSONDecodeError:
            pass

        lines = [line.strip().strip('"').strip("'") for line in cleaned.splitlines() if line.strip()]
        questions = [line.lstrip("-•0123456789. ") for line in lines if len(line) > 10]
        return [q for q in questions if q][:4]

    @staticmethod
    def _chunk_to_source(chunk: ChunkResult) -> SourceResult:
        snippet = chunk.text[:300] + ("..." if len(chunk.text) > 300 else "")
        return SourceResult(
            document_id=chunk.document_id,
            title=chunk.title,
            court=chunk.court,
            date=chunk.date,
            snippet=snippet,
            score=round(chunk.score, 6),
            chunk_index=chunk.chunk_index,
        )


def get_rag_service() -> RAGService:
    return RAGService()
