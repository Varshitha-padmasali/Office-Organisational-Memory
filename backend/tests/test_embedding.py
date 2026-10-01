"""
Unit tests for embedding_service.embed_texts().

The real Gemini API call is monkeypatched throughout — these tests verify
our integration contract (correct error when unconfigured, correct
dimension checking, correct pass-through of returned vectors), not
Google's embedding quality or network behavior. No network access or real
API key is needed to run this file.
"""

import pytest

from app.services import embedding_service
from app.services.embedding_service import EmbeddingError, embed_texts


def test_embed_texts_raises_when_api_key_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(embedding_service.settings, "GEMINI_API_KEY", "")

    with pytest.raises(EmbeddingError):
        embed_texts(["hello world"])


def test_embed_texts_returns_vectors_from_the_api(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(embedding_service.settings, "GEMINI_API_KEY", "fake-key-for-test")
    monkeypatch.setattr(embedding_service.genai, "configure", lambda **kwargs: None)

    fake_vector = [0.1] * embedding_service.EMBEDDING_DIMENSIONS

    def fake_embed_content(**kwargs):
        return {"embedding": fake_vector}

    monkeypatch.setattr(embedding_service.genai, "embed_content", fake_embed_content)

    result = embed_texts(["hello", "world"])

    assert result == [fake_vector, fake_vector]


def test_embed_texts_rejects_wrong_dimension_response(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(embedding_service.settings, "GEMINI_API_KEY", "fake-key-for-test")
    monkeypatch.setattr(embedding_service.genai, "configure", lambda **kwargs: None)
    monkeypatch.setattr(
        embedding_service.genai, "embed_content", lambda **kwargs: {"embedding": [0.1, 0.2]}
    )

    with pytest.raises(EmbeddingError):
        embed_texts(["hello"])
