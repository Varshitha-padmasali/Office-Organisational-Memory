"""
Unit tests for rag_service (app.services.rag_service).

These mock both retrieval (app.services.retrieval_service.search_chunks)
and the Gemini generation call, so they run with no database and no
network. They test OUR orchestration logic (when to call the LLM, how the
prompt is built, how failures are surfaced) - not Gemini's answer quality
or pgvector's search quality (covered elsewhere: test_embedding.py, and
test_chat.py's live integration tests).
"""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas.search import SearchResultItem
from app.services import rag_service
from app.services.rag_service import GenerationError, build_prompt


def _fake_result(index: int, document_name: str = "handbook.txt") -> SearchResultItem:
    return SearchResultItem(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_name=document_name,
        content=f"Fake chunk content number {index}.",
        score=0.9 - index * 0.1,
    )


def test_build_prompt_numbers_sources_and_includes_question():
    results = [_fake_result(0, "handbook.txt"), _fake_result(1, "leave_policy.pdf")]

    prompt = build_prompt("What is the leave policy?", results)

    assert "[Source 1: handbook.txt]" in prompt
    assert "[Source 2: leave_policy.pdf]" in prompt
    assert "What is the leave policy?" in prompt
    assert "Fake chunk content number 0." in prompt


@pytest.mark.asyncio
async def test_answer_question_returns_no_context_message_when_nothing_found(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        rag_service.retrieval_service, "search_chunks", AsyncMock(return_value=[])
    )

    result = await rag_service.answer_question(db=None, owner_id=None, question="anything")

    assert result.citations == []
    assert result.answer == rag_service.NO_CONTEXT_MESSAGE


@pytest.mark.asyncio
async def test_answer_question_generates_answer_and_returns_citations(
    monkeypatch: pytest.MonkeyPatch,
):
    fake_results = [_fake_result(0)]
    monkeypatch.setattr(
        rag_service.retrieval_service, "search_chunks", AsyncMock(return_value=fake_results)
    )
    monkeypatch.setattr(rag_service.genai, "configure", lambda **kwargs: None)

    fake_response = SimpleNamespace(text="Employees get 25 days of leave. [Source 1]")

    class FakeModel:
        def generate_content(self, prompt: str):
            assert "Fake chunk content number 0." in prompt
            return fake_response

    monkeypatch.setattr(rag_service.genai, "GenerativeModel", lambda name: FakeModel())
    monkeypatch.setattr(rag_service.settings, "GEMINI_API_KEY", "fake-key-for-test")

    result = await rag_service.answer_question(db=None, owner_id=None, question="How much leave?")

    assert result.answer == "Employees get 25 days of leave. [Source 1]"
    assert len(result.citations) == 1
    assert result.citations[0].document_name == "handbook.txt"


@pytest.mark.asyncio
async def test_answer_question_wraps_generation_failures(monkeypatch: pytest.MonkeyPatch):
    fake_results = [_fake_result(0)]
    monkeypatch.setattr(
        rag_service.retrieval_service, "search_chunks", AsyncMock(return_value=fake_results)
    )
    monkeypatch.setattr(rag_service.genai, "configure", lambda **kwargs: None)

    class BrokenModel:
        def generate_content(self, prompt: str):
            raise RuntimeError("upstream API error")

    monkeypatch.setattr(rag_service.genai, "GenerativeModel", lambda name: BrokenModel())
    monkeypatch.setattr(rag_service.settings, "GEMINI_API_KEY", "fake-key-for-test")

    with pytest.raises(GenerationError):
        await rag_service.answer_question(db=None, owner_id=None, question="anything")
