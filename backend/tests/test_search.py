import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routers.search import get_rag_service
from app.schemas.search import CitationResult, SearchResponse, SourceResult


@pytest.mark.asyncio
async def test_search_endpoint_returns_rag_shape():
    mock_response = SearchResponse(
        search_id=uuid.uuid4(),
        answer="Bail may be granted when [1] conditions are met.",
        citations=[
            CitationResult(
                number=1,
                document_id="123",
                passage="Bail conditions...",
                title="State vs Accused",
                court="Supreme Court",
                date="2019-01-01",
            )
        ],
        sources=[
            SourceResult(
                document_id="123",
                title="State vs Accused",
                court="Supreme Court",
                date="2019-01-01",
                snippet="Bail conditions...",
                score=0.03,
                chunk_index=0,
            )
        ],
        provider_used="groq",
        result_count=1,
    )
    mock_rag = AsyncMock()
    mock_rag.search = AsyncMock(return_value=mock_response)

    app.dependency_overrides[get_rag_service] = lambda: mock_rag
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/search",
                json={
                    "query": "bail in murder cases",
                    "preferred_provider": "auto",
                    "filters": {"court": ["Supreme Court"]},
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert data["provider_used"] == "groq"
    assert len(data["citations"]) == 1
    assert len(data["sources"]) == 1
