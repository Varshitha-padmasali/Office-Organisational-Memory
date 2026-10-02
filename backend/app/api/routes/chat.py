"""
Chat routes.

STATUS (Day 5): implemented for real. POST (not GET) because generating an
answer is a costly, side-effecting action (an LLM call) rather than an
idempotent lookup — this also leaves room for a future `conversation_id`
field without cramming it into query params.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.chat import ChatAnswer, ChatRequest
from app.services import rag_service
from app.services.embedding_service import EmbeddingError
from app.services.rag_service import GenerationError

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatAnswer)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatAnswer:
    try:
        return await rag_service.answer_question(
            db, current_user.id, payload.question, top_k=payload.top_k
        )
    except EmbeddingError as exc:
        # Query embedding (the retrieval step) failed — usually a missing
        # GEMINI_API_KEY. A configuration problem, not a bad request.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except GenerationError as exc:
        # Retrieval succeeded but the LLM call itself failed.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
