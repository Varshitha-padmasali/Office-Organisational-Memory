"""
Pydantic schemas for meeting notes ingestion.

STATUS (Day 6): implemented, matching the real /api/v1/meetings/* routes.
"""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

MeetingStatus = Literal["pending", "summarized", "failed"]


class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    raw_notes: str = Field(..., min_length=1)
    meeting_date: date | None = None


class MeetingOut(BaseModel):
    id: uuid.UUID
    title: str
    raw_notes: str
    summary: str | None
    meeting_date: date | None
    status: MeetingStatus
    created_at: datetime
    owner_id: uuid.UUID

    model_config = {"from_attributes": True}
