"""
Meeting service - stores meeting notes, summarizes them, and extracts any
decisions made during the meeting.

STATUS (Day 6): implemented. Summarization and decision extraction run
synchronously right after a meeting is created, mirroring
document_service.process_document's pattern from Day 3: a failure here
(missing GEMINI_API_KEY, API error) marks the meeting "failed" rather than
raising, since the raw notes were already saved successfully and there is
no reason to lose them just because summarization didn't work.
"""

import uuid
from datetime import date
from typing import Sequence

import google.generativeai as genai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.meeting import Meeting
from app.services import decision_service

settings = get_settings()
logger = get_logger(__name__)

_SUMMARY_PROMPT = (
    "Summarize the following meeting notes in three sentences or fewer, "
    "focused on what was discussed and any outcomes. Do not add "
    "information that isn't in the notes.\n\nMeeting notes:\n{notes}\n\nSummary:"
)


async def create_meeting(
    db: AsyncSession,
    *,
    owner_id: uuid.UUID,
    title: str,
    raw_notes: str,
    meeting_date: date | None = None,
) -> Meeting:
    meeting = Meeting(
        owner_id=owner_id,
        title=title,
        raw_notes=raw_notes,
        meeting_date=meeting_date,
        status="pending",
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


def _summarize(raw_notes: str) -> str:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    response = model.generate_content(_SUMMARY_PROMPT.format(notes=raw_notes))
    return response.text.strip()


async def process_meeting(db: AsyncSession, meeting: Meeting) -> Meeting:
    """
    Summarize the meeting notes and extract any decisions from them.
    Catches its own exceptions - same reasoning as process_document: the
    notes are already saved, so a failure here degrades to "failed"
    rather than breaking the create/reprocess request.
    """
    try:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured - set it in backend/.env to enable summarization."
            )

        summary = _summarize(meeting.raw_notes)
        decisions = decision_service.extract_decisions_from_text(meeting.raw_notes)

        meeting.summary = summary
        meeting.status = "summarized"
        await db.commit()
        await db.refresh(meeting)

        if decisions:
            await decision_service.create_decisions(
                db, owner_id=meeting.owner_id, decisions=decisions, meeting_id=meeting.id
            )
    except Exception as exc:  # noqa: BLE001 - any failure here means "failed", not a 500
        logger.warning("Processing failed for meeting %s: %s", meeting.id, exc)
        meeting.status = "failed"
        await db.commit()
        await db.refresh(meeting)

    return meeting


async def list_meetings_for_user(db: AsyncSession, owner_id: uuid.UUID) -> Sequence[Meeting]:
    result = await db.execute(
        select(Meeting).where(Meeting.owner_id == owner_id).order_by(Meeting.created_at.desc())
    )
    return result.scalars().all()


async def get_meeting_for_user(
    db: AsyncSession, owner_id: uuid.UUID, meeting_id: uuid.UUID
) -> Meeting | None:
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.owner_id == owner_id)
    )
    return result.scalar_one_or_none()
