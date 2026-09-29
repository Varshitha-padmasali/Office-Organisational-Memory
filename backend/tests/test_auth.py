"""
Tests for /api/v1/auth/*.

STATUS (Day 1): auth is not implemented yet (see app/api/routes/auth.py),
so these tests only verify the route is honest about that — HTTP 501, not
a fake 200. Real tests (successful login, wrong password, duplicate
registration, token validation) will replace/extend this on Day 2.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_login_returns_501_not_implemented():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login", json={"email": "user@example.com", "password": "x"}
        )

    assert response.status_code == 501
    assert "day 2" in response.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_register_returns_501_not_implemented():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register", json={"email": "user@example.com", "password": "x"}
        )

    assert response.status_code == 501


@pytest.mark.asyncio
async def test_login_rejects_malformed_payload_with_422():
    """Pydantic validation should still run even though the route is a stub."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json={"email": "not-an-email"})

    assert response.status_code == 422
