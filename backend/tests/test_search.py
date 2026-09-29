"""
Tests for /api/v1/search/.

STATUS (Day 1): semantic search is not implemented yet (planned for Day 4,
once embeddings + pgvector retrieval are wired up). This test only guards
that the route is honest about it rather than returning fake results.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_search_returns_501_not_implemented():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/search/")

    assert response.status_code == 501
