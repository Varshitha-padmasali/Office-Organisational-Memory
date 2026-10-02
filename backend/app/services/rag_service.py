"""
RAG service — generates a grounded answer from retrieved document chunks.

STATUS (Day 5): implemented. Retrieval (app.services.retrieval_service,
Day 4) finds the most relevant chunks; this module feeds them to Gemini as
context and asks it to answer using ONLY that context, citing sources by
number (see app/prompts/rag_prompt.txt). If retrieval finds nothing, the
LLM is never called — there would be nothing to ground an answer in, and
calling it anyway would risk an ungrounded (and potentially fabricated)
response, which is exactly what this whole pipeline exists to avoid.
"""

import asyncio
import uuid
from pathlib import Path
from typing import Sequence

import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.schemas.chat import ChatAnswer, ChatCitation
from app.schemas.search import SearchResultItem
from app.services import retrieval_service

settings = get_settings()

_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "rag_prompt.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

NO_CONTEXT_MESSAGE = (
    "I couldn't find anything relevant in your documents to answer that. "
    "Try uploading a document that covers this topic, or rephrase your question."
)


class GenerationError(Exception):
    """Raised when the generation step (not retrieval) fails."""


def build_prompt(question: str, results: Sequence[SearchResultItem]) -> str:
    """
    Assemble the final prompt sent to Gemini: numbered context blocks (one
    per retrieved chunk, labeled with its source document) followed by the
    question. Pulled out as its own function so it's testable without a
    database or network — see tests/test_rag.py.
    """
    context_blocks = [
        f"[Source {i + 1}: {r.document_name}]\n{r.content}" for i, r in enumerate(results)
    ]
    return _PROMPT_TEMPLATE.format(context="\n\n".join(context_blocks), question=question)


async def answer_question(
    db: AsyncSession,
    owner_id: uuid.UUID,
    question: str,
    *,
    top_k: int = 5,
) -> ChatAnswer:
    """
    Retrieve relevant chunks, then (if any were found) ask Gemini to
    generate a grounded answer from them.

    Can raise app.services.embedding_service.EmbeddingError (from the
    retrieval step embedding the query — propagated, not caught here) or
    GenerationError (from the generation step itself). The route layer
    maps both to HTTP 503.
    """
    results = await retrieval_service.search_chunks(db, owner_id, question, top_k=top_k)

    if not results:
        return ChatAnswer(answer=NO_CONTEXT_MESSAGE, citations=[])

    prompt = build_prompt(question, results)

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)

    try:
        # generate_content is a blocking network call in the SDK; run it
        # off the event loop so this async route doesn't stall other
        # requests while waiting on Gemini.
        response = await asyncio.to_thread(model.generate_content, prompt)
        answer_text = response.text.strip()
    except Exception as exc:  # noqa: BLE001 - any SDK failure becomes a GenerationError
        raise GenerationError(f"Answer generation failed: {exc}") from exc

    citations = [
        ChatCitation(
            chunk_id=r.chunk_id,
            document_id=r.document_id,
            document_name=r.document_name,
            snippet=r.content,
            score=r.score,
        )
        for r in results
    ]

    return ChatAnswer(answer=answer_text, citations=citations)
