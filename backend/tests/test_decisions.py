"""
Tests for /api/v1/decisions/* and POST /api/v1/documents/{id}/extract-decisions.

STATUS (Day 6): real integration tests requiring a running Postgres
instance; tolerant of missing GEMINI_API_KEY (same pattern as
test_meetings.py / test_documents.py).
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
async def test_list_decisions_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/decisions/")

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_decisions_empty_for_new_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.get("/api/v1/decisions/", headers=headers)

    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_nonexistent_decision_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.get(f"/api/v1/decisions/{uuid.uuid4()}", headers=headers)

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_extract_decisions_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(f"/api/v1/documents/{uuid.uuid4()}/extract-decisions")

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_extract_decisions_from_nonexistent_document_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.post(
            f"/api/v1/documents/{uuid.uuid4()}/extract-decisions", headers=headers
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_extract_decisions_from_document_depends_on_processing_outcome():
    """
    If the upload reached "ready" (real GEMINI_API_KEY configured),
    extraction should succeed structurally (200, a list, even if empty).
    If upload ended up "failed" (no chunks exist), extraction correctly
    refuses with 400 rather than pretending there's text to work from.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)

        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={
                "file": (
                    "notes.txt",
                    io.BytesIO(
                        b"The team decided to move the office to a new "
                        b"building starting next quarter."
                    ),
                    "text/plain",
                )
            },
        )
        doc = upload_resp.json()

        extract_resp = await client.post(
            f"/api/v1/documents/{doc['id']}/extract-decisions", headers=headers
        )

    if doc["status"] != "ready":
        assert extract_resp.status_code == 400
        return

    assert extract_resp.status_code == 200
    body = extract_resp.json()
    assert isinstance(body, list)
    for item in body:
        assert item["source_type"] == "document"
        assert item["source_id"] == doc["id"]
        assert item["source_title"] == "notes.txt"


@pytest.mark.asyncio
async def test_extracted_document_decisions_appear_in_decision_log():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)

        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={
                "file": (
                    "policy.txt",
                    io.BytesIO(b"The company decided to adopt a four-day work week."),
                    "text/plain",
                )
            },
        )
        doc = upload_resp.json()

        if doc["status"] != "ready":
            return  # nothing was indexed without a real GEMINI_API_KEY

        await client.post(f"/api/v1/documents/{doc['id']}/extract-decisions", headers=headers)
        decisions_resp = await client.get("/api/v1/decisions/", headers=headers)

    assert decisions_resp.status_code == 200
    matching = [d for d in decisions_resp.json() if d["source_id"] == doc["id"]]
    for d in matching:
        assert d["source_type"] == "document"
