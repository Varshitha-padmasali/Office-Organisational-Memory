"""
Unit tests for chunking_service.chunk_text().

Pure function tests — no database, no network, no external services.
"""

import pytest

from app.services.chunking_service import chunk_text


def test_chunk_text_returns_single_chunk_for_short_text():
    text = "This is a short piece of text."
    chunks = chunk_text(text, chunk_size=1000, overlap=150)

    assert chunks == [text]


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("", chunk_size=1000, overlap=150) == []
    assert chunk_text("   \n\t  ", chunk_size=1000, overlap=150) == []


def test_chunk_text_splits_long_text_into_multiple_chunks():
    text = "word " * 500  # ~2500 characters
    chunks = chunk_text(text, chunk_size=1000, overlap=150)

    assert len(chunks) > 1
    for chunk in chunks:
        # +50 allows for the whitespace-snap slack described in the docstring.
        assert len(chunk) <= 1000 + 50


def test_chunk_text_overlap_is_exact_when_no_whitespace_to_snap_to():
    """
    Uses a string with no spaces at all (unique 5-char tokens concatenated)
    so whitespace-snapping never kicks in, making the exact overlap
    boundary deterministic and checkable — a weaker test using real
    prose would be sensitive to where word boundaries happen to fall.
    """
    tokens = [f"{i:05d}" for i in range(1000)]
    text = "".join(tokens)  # 5000 chars, no whitespace at all

    chunks = chunk_text(text, chunk_size=1000, overlap=200)

    assert len(chunks) == 6
    for first, second in zip(chunks, chunks[1:]):
        assert first[-200:] == second[:200]


def test_chunk_text_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=100)
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=-1)
