"""
Pydantic schemas for the decision log.

STATUS (Day 6): implemented, matching the real /api/v1/decisions/* and
POST /api/v1/documents/{id}/extract-decisions routes.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DecisionOut(BaseModel):
    """
    Decision rows store meeting_id/document_id as two separate nullable
    columns (see app.models.decision) since a decision always comes from
    exactly one of them; this schema collapses that into a single
    source_type/source_id/source_title trio for the API, built by
    app.services.decision_service.to_decision_out() rather than
    constructed directly from the ORM row (it needs the source's title,
    which lives on a different table).
    """

    id: uuid.UUID
    summary: str
    context: str | None
    source_type: Literal["meeting", "document"]
    source_id: uuid.UUID
    source_title: str
    created_at: datetime
