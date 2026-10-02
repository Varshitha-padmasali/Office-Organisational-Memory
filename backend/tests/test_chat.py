"""
Tests for POST /api/v1/chat/.

STATUS (Day 5): real integration tests requiring a running Postgres
instance. Like test_search.py, whether generation succeeds depends on
GEMINI_API_KEY being configured in the environment running the suite -
tests here accept either a real generated answer or the honest
"couldn't find anything relevant" / 503 outcomes rather than asserting one
specific result. See test_rag.py for orchestration-logic tests that mock
Gemini directly and so don't depend on environment configuration.
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
async def test_chat_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/chat/", json={"question": "hello"})

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_rejects_empty_question():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.post("/api/v1/chat/", headers=headers, json={"question": ""})

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_chat_with_no_documents_gives_honest_no_context_answer_or_503():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.post(
            "/api/v1/chat/", headers=headers, json={"question": "anything at all"}
        )

    assert resp.status_code in (200, 503)
    if resp.status_code == 200:
        body = resp.json()
        assert body["citations"] == []
        assert "couldn't find" in body["answer"].lower()


@pytest.mark.asyncio
async def test_chat_answers_from_uploaded_document_when_fully_configured():
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
                        b"The office is closed on all federal holidays, "
                        b"including New Year's Day and Thanksgiving."
                    ),
                    "text/plain",
                )
            },
        )
        doc = upload_resp.json()

        chat_resp = await client.post(
            "/api/v1/chat/",
            headers=headers,
            json={"question": "Is the office closed on Thanksgiving?"},
        )

    if doc["status"] != "ready":
        # No GEMINI_API_KEY configured in this environment - nothing was
        # indexed, so there's nothing to generate an answer from.
        assert chat_resp.status_code in (200, 503)
        return

    assert chat_resp.status_code == 200
    body = chat_resp.json()
    assert len(body["citations"]) > 0
    assert body["citations"][0]["document_id"] == doc["id"]
    assert len(body["answer"]) > 0
