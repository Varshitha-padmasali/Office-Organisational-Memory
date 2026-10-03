"""
Decision service - extracts organizational decisions from meeting notes
or documents using Gemini, and records them as searchable Decision rows.

STATUS (Day 6): implemented. Mirrors rag_service's "ask the LLM to work
only from the given text" pattern, but asks for structured JSON back
instead of prose, since decisions need to be stored as discrete records
rather than displayed as one block of text.
"""

import json
import uuid
from pathlib import Path
from typing import Sequence

import google.generativeai as genai
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.decision import Decision
from app.models.document import Document
from app.models.meeting import Meeting
from app.schemas.decision import DecisionOut

settings = get_settings()

_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "decision_prompt.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")


class DecisionExtractionError(Exception):
    """Raised when decision extraction fails (API error or unparseable response)."""


def _strip_code_fences(text: str) -> str:
    """Gemini sometimes wraps JSON in ```json ... ``` despite instructions not to."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]  # drop the opening fence line (``` or ```json)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def extract_decisions_from_text(text: str) -> list[dict]:
    """
    Ask Gemini to identify discrete decisions in `text` and return them as
    a list of {"summary": str, "context": str} dicts. Returns an empty
    list immediately for blank input, without calling the API.
    """
    if not text.strip():
        return []

    if not settings.GEMINI_API_KEY:
        raise DecisionExtractionError(
            "GEMINI_API_KEY is not configured - set it in backend/.env to enable decision extraction."
        )

    prompt = _PROMPT_TEMPLATE.format(text=text)

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)

    try:
        response = model.generate_content(prompt)
        raw = _strip_code_fences(response.text)
        parsed = json.loads(raw)
    except Exception as exc:  # noqa: BLE001 - any SDK or parse failure becomes this
        raise DecisionExtractionError(f"Decision extraction failed: {exc}") from exc

    if not isinstance(parsed, list):
        raise DecisionExtractionError("Expected a JSON array of decisions from the model.")

    decisions = []
    for item in parsed:
        if not isinstance(item, dict) or "summary" not in item:
            continue
        decisions.append(
            {
                "summary": str(item["summary"]).strip(),
                "context": str(item.get("context", "")).strip(),
            }
        )
    return decisions


async def create_decisions(
    db: AsyncSession,
    *,
    owner_id: uuid.UUID,
    decisions: list[dict],
    meeting_id: uuid.UUID | None = None,
    document_id: uuid.UUID | None = None,
) -> list[Decision]:
    """Persist extracted decisions, linked to exactly one source."""
    if (meeting_id is None) == (document_id is None):
        raise ValueError("Exactly one of meeting_id or document_id must be provided.")

    rows = [
        Decision(
            owner_id=owner_id,
            meeting_id=meeting_id,
            document_id=document_id,
            summary=d["summary"],
            context=d.get("context") or None,
        )
        for d in decisions
    ]
    db.add_all(rows)
    await db.commit()
    for row in rows:
        await db.refresh(row)
    return rows


async def list_decisions_for_user(
    db: AsyncSession, owner_id: uuid.UUID
) -> Sequence[tuple[Decision, str | None, str | None]]:
    """Returns (decision, meeting_title, document_name) tuples via outer joins."""
    stmt = (
        select(Decision, Meeting.title, Document.original_filename)
        .outerjoin(Meeting, Decision.meeting_id == Meeting.id)
        .outerjoin(Document, Decision.document_id == Document.id)
        .where(Decision.owner_id == owner_id)
        .order_by(Decision.created_at.desc())
    )
    return (await db.execute(stmt)).all()


async def get_decision_for_user(
    db: AsyncSession, owner_id: uuid.UUID, decision_id: uuid.UUID
) -> tuple[Decision, str | None, str | None] | None:
    stmt = (
        select(Decision, Meeting.title, Document.original_filename)
        .outerjoin(Meeting, Decision.meeting_id == Meeting.id)
        .outerjoin(Document, Decision.document_id == Document.id)
        .where(Decision.id == decision_id, Decision.owner_id == owner_id)
    )
    row = (await db.execute(stmt)).first()
    return row


def to_decision_out(decision: Decision, meeting_title: str | None, document_name: str | None) -> DecisionOut:
    """Collapse the two nullable source columns into one source_type/source_id/source_title trio."""
    if decision.meeting_id is not None:
        source_type: str = "meeting"
        source_id = decision.meeting_id
        source_title = meeting_title or "Untitled meeting"
    else:
        source_type = "document"
        source_id = decision.document_id
        source_title = document_name or "Unknown document"

    return DecisionOut(
        id=decision.id,
        summary=decision.summary,
        context=decision.context,
        source_type=source_type,  # type: ignore[arg-type]
        source_id=source_id,
        source_title=source_title,
        created_at=decision.created_at,
    )


async def delete_decisions_for_meeting(db: AsyncSession, meeting_id: uuid.UUID) -> None:
    await db.execute(delete(Decision).where(Decision.meeting_id == meeting_id))
    await db.commit()


async def delete_decisions_for_document(db: AsyncSession, document_id: uuid.UUID) -> None:
    await db.execute(delete(Decision).where(Decision.document_id == document_id))
    await db.commit()
