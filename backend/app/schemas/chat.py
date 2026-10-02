"""
Pydantic schemas for the chat / RAG Q&A endpoint.

STATUS (Day 5): implemented, matching the real POST /api/v1/chat/ route.
"""

import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class ChatCitation(BaseModel):
    """
    One retrieved chunk that the answer was (supposed to be) grounded on.
    Mirrors SearchResultItem but under chat-specific naming so the two
    endpoints' response shapes can evolve independently.
    """

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    snippet: str
    score: float


class ChatAnswer(BaseModel):
    answer: str
    citations: list[ChatCitation]
