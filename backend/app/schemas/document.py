"""
Pydantic schemas for document upload/listing.

STATUS (Day 2): implemented, matching the real /api/v1/documents/* routes.
Status is currently always "uploaded" in practice — "processing"/"ready"/
"failed" are reserved for Day 3, once text extraction exists.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

DocumentStatus = Literal["uploaded", "processing", "ready", "failed"]


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus
    uploaded_at: datetime
    owner_id: uuid.UUID

    model_config = {"from_attributes": True}
