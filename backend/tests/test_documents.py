"""
Tests for /api/v1/documents/.

STATUS (Day 1): document upload/listing is not implemented yet (planned
for Day 2-3). This test only guards that the route is honest about it.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_list_documents_returns_501_not_implemented():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/documents/")

    assert response.status_code == 501
    assert "not implemented" in response.json()["error"]["message"].lower()
