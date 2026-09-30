"""
Tests for /api/v1/auth/*.

STATUS (Day 2): these are real integration tests — register/login/me now
actually hit the database, so a running Postgres instance is required:

    docker compose up -d
    cd backend && pytest tests/test_auth.py

Each test uses a fresh, randomly generated email so the suite is safe to
re-run against a persistent database.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


@pytest.mark.asyncio
async def test_register_then_login_roundtrip():
    email = _unique_email()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        register_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "s3cret-pass", "full_name": "Test User"},
        )
        assert register_resp.status_code == 201
        assert "access_token" in register_resp.json()

        login_resp = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "s3cret-pass"}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        me_resp = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == email


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409():
    email = _unique_email()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/api/v1/auth/register", json={"email": email, "password": "s3cret-pass"}
        )
        assert first.status_code == 201

        second = await client.post(
            "/api/v1/auth/register", json={"email": email, "password": "another-pass"}
        )
        assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401():
    email = _unique_email()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/auth/register", json={"email": email, "password": "s3cret-pass"}
        )
        resp = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "wrong-password"}
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/auth/me")

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_rejects_malformed_payload_with_422():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json={"email": "not-an-email"})

    assert response.status_code == 422
