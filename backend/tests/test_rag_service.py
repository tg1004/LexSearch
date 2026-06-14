import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routers.search import get_rag_service
from app.schemas.search import SearchFilters, SearchResponse
from app.services.rag.rag_service import RAGService


@pytest.mark.asyncio
async def test_search_returns_related_questions_when_present():
    mock_response = SearchResponse(
        search_id=uuid.uuid4(),
        answer="Bail may be granted when conditions in [1] are satisfied.",
        citations=[],
        sources=[],
        provider_used="groq",
        related_questions=[
            "What are conditions for anticipatory bail?",
            "How does NDPS Act restrict bail?",
        ],
        result_count=5,
    )
    mock_rag = AsyncMock()
    mock_rag.search = AsyncMock(return_value=mock_response)

    app.dependency_overrides[get_rag_service] = lambda: mock_rag
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/search",
                json={"query": "bail in murder cases", "preferred_provider": "auto", "filters": {}},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["related_questions"]) == 2


@pytest.mark.asyncio
async def test_search_no_results_skips_llm():
    mock_search = AsyncMock()
    mock_search.retrieve_for_search = AsyncMock(return_value=([], [], 0))

    service = RAGService(search_service=mock_search, redis_cache=None)
    response = await service.search("nonexistent xyz query", filters=SearchFilters())

    assert response.result_count == 0
    assert "No results found" in response.answer
    mock_search.retrieve_for_search.assert_awaited_once()
