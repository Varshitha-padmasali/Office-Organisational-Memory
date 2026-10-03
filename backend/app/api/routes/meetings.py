"""
Meetings routes.

STATUS (Day 6): implemented for real. Creating a meeting synchronously
summarizes it and extracts any decisions (see
app.services.meeting_service.process_meeting), mirroring the document
upload pipeline's pattern from Day 3 - so this can take a few seconds,
and `status` will already be "summarized" or "failed" by the time the
response comes back.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingOut
from app.services import decision_service, meeting_service

router = APIRouter(prefix="/meetings", tags=["meetings"])


async def _get_owned_meeting_or_404(
    db: AsyncSession, owner_id: uuid.UUID, meeting_id: uuid.UUID
):
    meeting = await meeting_service.get_meeting_for_user(db, owner_id, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")
    return meeting


@router.post("/", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    payload: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeetingOut:
    meeting = await meeting_service.create_meeting(
        db,
        owner_id=current_user.id,
        title=payload.title,
        raw_notes=payload.raw_notes,
        meeting_date=payload.meeting_date,
    )
    return await meeting_service.process_meeting(db, meeting)


@router.get("/", response_model=list[MeetingOut])
async def list_meetings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MeetingOut]:
    meetings = await meeting_service.list_meetings_for_user(db, current_user.id)
    return list(meetings)


@router.get("/{meeting_id}", response_model=MeetingOut)
async def get_meeting(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeetingOut:
    return await _get_owned_meeting_or_404(db, current_user.id, meeting_id)


@router.post("/{meeting_id}/reprocess", response_model=MeetingOut)
async def reprocess_meeting(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeetingOut:
    meeting = await _get_owned_meeting_or_404(db, current_user.id, meeting_id)
    await decision_service.delete_decisions_for_meeting(db, meeting_id)
    return await meeting_service.process_meeting(db, meeting)
