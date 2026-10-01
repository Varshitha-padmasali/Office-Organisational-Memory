"""
Tests for /api/v1/documents/*.

STATUS (Day 3): real integration tests requiring a running Postgres
instance (see docker-compose.yml). Each test registers its own throwaway
user so the suite doesn't depend on shared fixtures/state.

Upload now triggers the full extraction -> chunking -> embedding pipeline
synchronously, which calls the real Gemini API if GEMINI_API_KEY is
configured. Since that's not guaranteed in every environment running this
suite, tests here deliberately accept EITHER "ready" or "failed" as a
valid final status rather than asserting one specific outcome — what they
check is that the pipeline *ran to a final state* and that the API
contract (chunks endpoint, status codes) holds either way. See
test_embedding.py for tests that mock the Gemini call directly.
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
        # "ready" if GEMINI_API_KEY is configured in this environment,
        # "failed" otherwise (e.g. CI without a real key) — both are
        # valid *final* states; see module docstring.
        assert doc["status"] in ("ready", "failed")

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


@pytest.mark.asyncio
async def test_get_chunks_matches_processing_outcome():
    """
    If processing ended in "ready" there should be at least one chunk; if
    it ended in "failed" (e.g. no GEMINI_API_KEY in this environment)
    there should be none. Either way, the endpoint itself must work.
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
                    io.BytesIO(b"Hello world, this is a test document with enough text."),
                    "text/plain",
                )
            },
        )
        doc = upload_resp.json()

        chunks_resp = await client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=headers)

    assert chunks_resp.status_code == 200
    if doc["status"] == "ready":
        assert len(chunks_resp.json()) > 0
    else:
        assert chunks_resp.json() == []


@pytest.mark.asyncio
async def test_reprocess_nonexistent_document_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        fake_id = uuid.uuid4()
        resp = await client.post(f"/api/v1/documents/{fake_id}/reprocess", headers=headers)

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reprocess_runs_pipeline_again():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("notes.txt", io.BytesIO(b"Some reprocessable content here."), "text/plain")},
        )
        doc_id = upload_resp.json()["id"]

        reprocess_resp = await client.post(
            f"/api/v1/documents/{doc_id}/reprocess", headers=headers
        )

    assert reprocess_resp.status_code == 200
    assert reprocess_resp.json()["status"] in ("ready", "failed")
