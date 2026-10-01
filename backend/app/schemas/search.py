"""
Pydantic schemas for semantic search.

STATUS (Day 4): implemented, matching the real GET /api/v1/search/ route.
"""

import uuid

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    content: str
    # Cosine similarity, 1 - cosine_distance: 1.0 = identical, 0.0 =
    # unrelated, negative = opposite. Rounded for readability.
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
