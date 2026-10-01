"""
Retrieval service — semantic search over a user's processed document chunks.

STATUS (Day 4): implemented. Embeds the query via the same Gemini model
used for documents (app.services.embedding_service), then runs a pgvector
cosine-similarity query scoped to the signed-in user's own "ready"
documents. The ivfflat index on chunks.embedding (created in Day 3's
migration 0003) makes this an approximate-nearest-neighbor search rather
than an exact brute-force scan, which matters once there are many chunks.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.search import SearchResultItem
from app.services.embedding_service import embed_texts


async def search_chunks(
    db: AsyncSession,
    owner_id: uuid.UUID,
    query_text: str,
    *,
    top_k: int = 5,
) -> list[SearchResultItem]:
    """
    Embed `query_text` and return the top_k most similar chunks belonging
    to `owner_id`'s own "ready" documents, ranked by cosine similarity.
    """
    # task_type="retrieval_query" (vs. documents' "retrieval_document") is
    # Gemini's recommended pairing for asymmetric search — the query and
    # the indexed passages are embedded slightly differently for best
    # retrieval quality, even though both land in the same 768-dim space.
    query_vector = embed_texts([query_text], task_type="retrieval_query")[0]

    distance = Chunk.embedding.cosine_distance(query_vector)
    stmt = (
        select(Chunk, Document.original_filename, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.owner_id == owner_id, Document.status == "ready")
        .order_by(distance)
        .limit(top_k)
    )

    rows = (await db.execute(stmt)).all()

    return [
        SearchResultItem(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_name=original_filename,
            content=chunk.content,
            # pgvector's cosine distance is defined as 1 - cosine_similarity,
            # so similarity = 1 - distance.
            score=round(1 - dist, 4),
        )
        for chunk, original_filename, dist in rows
    ]
