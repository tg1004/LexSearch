"""Phase 7 user feature endpoint tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_feedback_endpoint_accepts_anonymous():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/feedback",
            json={
                "query": "bail in murder cases",
                "is_helpful": True,
                "provider_used": "groq",
            },
        )

    assert response.status_code == 201
    assert response.json()["message"] == "Feedback recorded"


@pytest.mark.asyncio
async def test_history_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/history")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_bookmarks_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/bookmarks")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_stats_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/stats")

    assert response.status_code == 401
