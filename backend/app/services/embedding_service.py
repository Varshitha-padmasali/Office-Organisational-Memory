"""
Embedding service — turns text chunks into vectors for pgvector.

STATUS (Day 3): implemented against the Gemini embedding model
(models/text-embedding-004, 768 dimensions — matches
app.models.chunk.EMBEDDING_DIMENSIONS and the chunks table's vector
column). Requires GEMINI_API_KEY to be set; raises a clear error
otherwise rather than silently storing garbage vectors.
"""

import google.generativeai as genai

from app.core.config import get_settings
from app.models.chunk import EMBEDDING_DIMENSIONS

EMBEDDING_MODEL = "models/text-embedding-004"

settings = get_settings()


class EmbeddingError(Exception):
    """Raised when embeddings can't be generated."""


def embed_texts(texts: list[str], *, task_type: str = "retrieval_document") -> list[list[float]]:
    """
    Embed a list of text chunks, one Gemini API call per chunk.

    A per-chunk loop (rather than one batched call) trades some latency for
    simplicity and compatibility across client library versions —
    acceptable at MVP scale (a handful of chunks per document).
    """
    if not settings.GEMINI_API_KEY:
        raise EmbeddingError(
            "GEMINI_API_KEY is not configured — set it in backend/.env to enable embeddings."
        )

    genai.configure(api_key=settings.GEMINI_API_KEY)

    embeddings: list[list[float]] = []
    for text in texts:
        result = genai.embed_content(model=EMBEDDING_MODEL, content=text, task_type=task_type)
        vector = result["embedding"]
        if len(vector) != EMBEDDING_DIMENSIONS:
            raise EmbeddingError(
                f"Expected {EMBEDDING_DIMENSIONS}-dimensional embeddings, got {len(vector)}."
            )
        embeddings.append(vector)

    return embeddings
