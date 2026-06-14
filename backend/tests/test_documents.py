import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.document import DocumentResponse, HighlightResponse
from app.services.document.document_service import get_document_service
from app.routers.documents import get_summary_service


@pytest.fixture
def sample_document() -> DocumentResponse:
    return DocumentResponse(
        id="1108032",
        title="Sample Judgement",
        court="Supreme Court",
        date=date(2010, 12, 2),
        judges=["Justice A", "Justice B"],
        case_type="Criminal",
        outcome="Allowed",
        bench_size="Division Bench",
        full_text="This is a sample judgement about bail and personal liberty.",
        summary=None,
        url="https://indiankanoon.org/doc/1108032/",
    )


@pytest.mark.asyncio
async def test_get_document_endpoint(sample_document: DocumentResponse):
    mock_service = MagicMock()
    mock_service.get_document = AsyncMock(return_value=sample_document)

    mock_summary = MagicMock()
    mock_summary.get_cached_summary = AsyncMock(return_value=None)

    app.dependency_overrides[get_document_service] = lambda: mock_service

    async def override_summary(request=None, redis_cache=None):
        return mock_summary

    app.dependency_overrides[get_summary_service] = override_summary
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/documents/1108032")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1108032"
    assert data["full_text"]
    assert data["bench_size"] == "Division Bench"


@pytest.mark.asyncio
async def test_get_highlight_endpoint():
    mock_service = MagicMock()
    mock_service.get_highlight = MagicMock(
        return_value=HighlightResponse(
            document_id="1108032",
            chunk_index=3,
            highlighted_passage="Bail may be granted when conditions are met.",
            position=1200,
            char_end=1450,
        )
    )
    app.dependency_overrides[get_document_service] = lambda: mock_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/documents/1108032/highlight?chunk_index=3")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["chunk_index"] == 3
    assert data["position"] == 1200
