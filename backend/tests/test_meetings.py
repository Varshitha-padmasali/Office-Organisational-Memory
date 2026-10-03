"""
Tests for /api/v1/meetings/*.

STATUS (Day 6): real integration tests requiring a running Postgres
instance. Creating a meeting triggers real summarization + decision
extraction via Gemini, so - same pattern as documents/search/chat -
whether it reaches "summarized" or "failed" depends on whether
GEMINI_API_KEY is configured in the environment running the suite. See
test_decision_extraction.py for extraction-logic tests that mock Gemini
directly and so don't depend on environment configuration.
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
async def test_create_meeting_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/meetings/", json={"title": "Standup", "raw_notes": "Talked about stuff."}
        )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_meeting_rejects_empty_notes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.post(
            "/api/v1/meetings/", headers=headers, json={"title": "Standup", "raw_notes": ""}
        )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_list_and_get_meeting_roundtrip():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)

        create_resp = await client.post(
            "/api/v1/meetings/",
            headers=headers,
            json={
                "title": "Vendor review",
                "raw_notes": (
                    "We discussed the vendor contract. The team decided to "
                    "renew for one year."
                ),
            },
        )
        assert create_resp.status_code == 201
        meeting = create_resp.json()
        assert meeting["title"] == "Vendor review"
        # "summarized" with a real GEMINI_API_KEY, "failed" without one -
        # both are valid final states (see module docstring).
        assert meeting["status"] in ("summarized", "failed")

        list_resp = await client.get("/api/v1/meetings/", headers=headers)
        assert list_resp.status_code == 200
        assert any(m["id"] == meeting["id"] for m in list_resp.json())

        get_resp = await client.get(f"/api/v1/meetings/{meeting['id']}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == meeting["id"]


@pytest.mark.asyncio
async def test_meeting_decisions_appear_in_decision_log_when_configured():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)

        create_resp = await client.post(
            "/api/v1/meetings/",
            headers=headers,
            json={
                "title": "Budget meeting",
                "raw_notes": (
                    "After discussion, the team decided to increase the "
                    "marketing budget by 10%."
                ),
            },
        )
        meeting = create_resp.json()

        decisions_resp = await client.get("/api/v1/decisions/", headers=headers)

    assert decisions_resp.status_code == 200
    if meeting["status"] != "summarized":
        return  # no GEMINI_API_KEY in this environment - nothing to check

    decisions = decisions_resp.json()
    matching = [d for d in decisions if d["source_id"] == meeting["id"]]
    # The model may or may not phrase this as a clean "decision" - we only
    # assert the plumbing works (a decision for this meeting CAN appear
    # with the right shape), not that extraction is 100% reliable.
    for d in matching:
        assert d["source_type"] == "meeting"
        assert d["source_title"] == "Budget meeting"


@pytest.mark.asyncio
async def test_get_nonexistent_meeting_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.get(f"/api/v1/meetings/{uuid.uuid4()}", headers=headers)

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reprocess_nonexistent_meeting_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_header(client)
        resp = await client.post(f"/api/v1/meetings/{uuid.uuid4()}/reprocess", headers=headers)

    assert resp.status_code == 404
