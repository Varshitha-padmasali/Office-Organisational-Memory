"""
Tests for the RAG pipeline (app/services/rag_service.py).

STATUS (Day 1): the RAG service itself doesn't exist yet — retrieval,
chunking, embeddings, and Gemini generation land Day 3-5. Rather than
write tests against code that doesn't exist (or fake ones that always
pass), this file is explicitly skipped so `pytest` output honestly shows
"not implemented" instead of "passing."
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="RAG pipeline not implemented yet — planned for Day 4-5."
)


def test_answer_question_with_citations():
    ...


def test_answer_question_when_no_relevant_chunks_found():
    ...
