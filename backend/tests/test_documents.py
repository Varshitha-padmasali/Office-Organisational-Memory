"""
Tests for /api/v1/documents/*.

STATUS (Day 2): real integration tests requiring a running Postgres
instance (see docker-compose.yml). Each test registers its own throwaway
user so the suite doesn't depend on shared fixtures/state. Text
extraction/chunking are still Day 3, so uploaded documents are only
checked for status "uploaded" here.
"""

import io
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


async def _get_auth_header(client: AsyncClient) -> dict:
    email = _unique_email()
    resp = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "s3cret-pass"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_documents_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/documents/")

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_upload_list_and_get_document_roundtrip():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)

        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("notes.txt", io.BytesIO(b"hello world"), "text/plain")},
        )
        assert upload_resp.status_code == 201
        doc = upload_resp.json()
        assert doc["original_filename"] == "notes.txt"
        assert doc["status"] == "uploaded"

        list_resp = await client.get("/api/v1/documents/", headers=headers)
        assert list_resp.status_code == 200
        assert any(d["id"] == doc["id"] for d in list_resp.json())

        get_resp = await client.get(f"/api/v1/documents/{doc['id']}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == doc["id"]


@pytest.mark.asyncio
async def test_upload_rejects_disallowed_file_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("virus.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
        )

    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_nonexistent_document_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        fake_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/documents/{fake_id}", headers=headers)

    assert resp.status_code == 404
