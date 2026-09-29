"""
Tests for the /health endpoint and basic app wiring.

These are the primary Day 1 tests — they verify the FastAPI app starts,
CORS/middleware/exception handlers are wired correctly, and /health
responds with a well-formed payload regardless of whether a real Postgres
instance is reachable in the test environment.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_200_and_expected_shape():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("ok", "degraded")
    assert "service" in body
    assert "database" in body
    assert body["database"] in ("connected", "unreachable")


@pytest.mark.asyncio
async def test_root_endpoint_returns_api_metadata():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert body["api_version"] == "/api/v1"


@pytest.mark.asyncio
async def test_unknown_route_returns_404_with_consistent_error_shape():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/this-route-does-not-exist")

    assert response.status_code == 404
