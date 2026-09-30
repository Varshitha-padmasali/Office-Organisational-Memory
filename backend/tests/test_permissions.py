"""
Tests for cross-user permission enforcement.

STATUS (Day 2): basic ownership enforcement now exists (documents are
strictly scoped to owner_id) — these tests are real, not skipped, and
require a running Postgres instance like test_auth.py / test_documents.py.
"""

import io
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


async def _register(client: AsyncClient) -> dict:
    email = _unique_email()
    resp = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "s3cret-pass"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_document():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers_a = await _register(client)
        headers_b = await _register(client)

        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers_a,
            files={"file": ("private.txt", io.BytesIO(b"secret"), "text/plain")},
        )
        doc_id = upload_resp.json()["id"]

        resp = await client.get(f"/api/v1/documents/{doc_id}", headers=headers_b)

    # 404, not 403 — we don't reveal that another user's document exists.
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_user_document_list_is_scoped_to_owner():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers_a = await _register(client)
        headers_b = await _register(client)

        await client.post(
            "/api/v1/documents/upload",
            headers=headers_a,
            files={"file": ("a.txt", io.BytesIO(b"a"), "text/plain")},
        )

        b_list = await client.get("/api/v1/documents/", headers=headers_b)

    assert b_list.status_code == 200
    assert b_list.json() == []
