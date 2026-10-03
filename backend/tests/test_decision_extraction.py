"""
Unit tests for decision_service.extract_decisions_from_text().

The Gemini call is mocked throughout - these test OUR JSON parsing and
fence-stripping logic (already verified standalone, see Day 6 delivery
notes), not Gemini's extraction quality. No database or network needed.
"""

from types import SimpleNamespace

import pytest

from app.services import decision_service
from app.services.decision_service import DecisionExtractionError, extract_decisions_from_text


def test_extract_decisions_returns_empty_list_for_blank_text():
    assert extract_decisions_from_text("") == []
    assert extract_decisions_from_text("   \n\t  ") == []


def test_extract_decisions_raises_when_api_key_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(decision_service.settings, "GEMINI_API_KEY", "")

    with pytest.raises(DecisionExtractionError):
        extract_decisions_from_text("We decided to switch vendors.")


def _mock_gemini_response(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    monkeypatch.setattr(decision_service.settings, "GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(decision_service.genai, "configure", lambda **kwargs: None)
    fake_response = SimpleNamespace(text=text)
    monkeypatch.setattr(
        decision_service.genai,
        "GenerativeModel",
        lambda name: SimpleNamespace(generate_content=lambda p: fake_response),
    )


def test_extract_decisions_parses_plain_json(monkeypatch: pytest.MonkeyPatch):
    _mock_gemini_response(
        monkeypatch,
        '[{"summary": "Switch to Vendor B", "context": "We decided to switch to Vendor B."}]',
    )

    result = extract_decisions_from_text("We decided to switch to Vendor B.")

    assert result == [{"summary": "Switch to Vendor B", "context": "We decided to switch to Vendor B."}]


def test_extract_decisions_strips_markdown_code_fences(monkeypatch: pytest.MonkeyPatch):
    fenced = '```json\n[{"summary": "Approve budget", "context": "Budget approved."}]\n```'
    _mock_gemini_response(monkeypatch, fenced)

    result = extract_decisions_from_text("Some text.")

    assert result == [{"summary": "Approve budget", "context": "Budget approved."}]


def test_extract_decisions_returns_empty_list_when_model_finds_none(monkeypatch: pytest.MonkeyPatch):
    _mock_gemini_response(monkeypatch, "[]")

    assert extract_decisions_from_text("Just small talk, nothing decided.") == []


def test_extract_decisions_skips_items_missing_summary(monkeypatch: pytest.MonkeyPatch):
    _mock_gemini_response(
        monkeypatch,
        '[{"context": "no summary here"}, {"summary": "Valid one", "context": "ok"}]',
    )

    result = extract_decisions_from_text("Some text.")

    assert result == [{"summary": "Valid one", "context": "ok"}]


def test_extract_decisions_raises_on_malformed_json(monkeypatch: pytest.MonkeyPatch):
    _mock_gemini_response(monkeypatch, "not valid json at all")

    with pytest.raises(DecisionExtractionError):
        extract_decisions_from_text("Some text.")


def test_extract_decisions_raises_when_response_is_not_a_json_array(monkeypatch: pytest.MonkeyPatch):
    _mock_gemini_response(monkeypatch, '{"summary": "not wrapped in an array"}')

    with pytest.raises(DecisionExtractionError):
        extract_decisions_from_text("Some text.")
