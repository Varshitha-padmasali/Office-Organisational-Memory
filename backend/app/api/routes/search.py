"""
Search routes.

STATUS (Day 4): implemented for real — semantic search over the
signed-in user's own "ready" documents, using pgvector cosine similarity
(app.services.retrieval_service). Returns ranked raw passages, not a
generated answer — turning these into one written answer with inline
citations is Day 5 (app.services.rag_service, still a stub).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.search import SearchResponse
from app.services import retrieval_service
from app.services.embedding_service import EmbeddingError

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Natural-language search query"),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    try:
        results = await retrieval_service.search_chunks(db, current_user.id, q, top_k=top_k)
    except EmbeddingError as exc:
        # Most commonly: GEMINI_API_KEY isn't configured. This is a
        # configuration problem, not a client error, hence 503 rather
        # than 400 — the request itself was fine.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return SearchResponse(query=q, results=results)
