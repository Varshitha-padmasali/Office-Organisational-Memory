"""
Tests for /api/v1/search/.

STATUS (Day 4): real integration tests requiring a running Postgres
instance (see docker-compose.yml). Search always embeds the query text via
the real Gemini API, so — same caveat as test_documents.py's pipeline
tests — whether a given search succeeds (200) or fails with a
configuration error (503) depends on whether GEMINI_API_KEY is set in the
environment running the suite. Tests here are written to pass either way,
except for cases that don't depend on embeddings at all (auth, validation).
"""

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
async def test_search_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/search/", params={"q": "vacation policy"})

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_search_rejects_missing_query_param():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.get("/api/v1/search/", headers=headers)

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_with_no_documents_returns_empty_or_503():
    """
    A user with zero uploaded documents should get back an empty results
    list — never an error — UNLESS the environment has no GEMINI_API_KEY
    configured, in which case embedding the query itself fails with 503
    before we even get to "no documents". Both are correct depending on
    environment; what would be wrong is getting fake results or a 500.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.get(
            "/api/v1/search/", headers=headers, params={"q": "anything at all"}
        )

    assert resp.status_code in (200, 503)
    if resp.status_code == 200:
        body = resp.json()
        assert body["query"] == "anything at all"
        assert body["results"] == []


@pytest.mark.asyncio
async def test_search_finds_uploaded_content_when_processing_succeeds():
    """
    Full end-to-end check: upload a document, then search for its exact
    content. If the environment has a real GEMINI_API_KEY and the document
    reached "ready", the uploaded chunk should come back as the top (or
    only) result. If processing ended up "failed" (no key configured),
    there's nothing to find and we just confirm search still responds
    cleanly rather than erroring.
    """
    import io

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)

        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={
                "file": (
                    "policy.txt",
                    io.BytesIO(
                        b"Employees are entitled to twenty-five days of "
                        b"paid vacation per calendar year."
                    ),
                    "text/plain",
                )
            },
        )
        doc = upload_resp.json()

        search_resp = await client.get(
            "/api/v1/search/",
            headers=headers,
            params={"q": "how many vacation days do employees get"},
        )

    if doc["status"] != "ready":
        # No GEMINI_API_KEY in this environment — nothing was indexed.
        assert search_resp.status_code in (200, 503)
        return

    assert search_resp.status_code == 200
    body = search_resp.json()
    assert len(body["results"]) > 0
    assert body["results"][0]["document_id"] == doc["id"]
    assert "vacation" in body["results"][0]["content"].lower()
    assert body["results"][0]["score"] > 0.5


@pytest.mark.asyncio
async def test_search_top_k_is_bounded():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.get(
            "/api/v1/search/", headers=headers, params={"q": "test", "top_k": 100}
        )

    # top_k has le=20 in the route — FastAPI/Pydantic rejects out-of-range
    # values with 422 before the handler (and any embedding call) runs.
    assert resp.status_code == 422
