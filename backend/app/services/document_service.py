"""
Document service — orchestrates document upload/storage + listing.

STATUS (Day 2): implemented for local-disk storage and Postgres metadata.
Text extraction (extraction_service.py) and chunking/embeddings
(chunking_service.py, embedding_service.py) are still separate,
not-yet-implemented steps planned for Day 3.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.utils.file_utils import safe_filename, save_upload_bytes


async def create_document(
    db: AsyncSession,
    *,
    owner_id: uuid.UUID,
    original_filename: str,
    content_type: str,
    content: bytes,
) -> Document:
    """Save the file to disk and create its metadata row in one step."""
    stored_name = safe_filename(original_filename)
    storage_path = save_upload_bytes(content, stored_name)

    document = Document(
        owner_id=owner_id,
        filename=stored_name,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=len(content),
        storage_path=storage_path,
        status="uploaded",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def list_documents_for_user(db: AsyncSession, owner_id: uuid.UUID) -> Sequence[Document]:
    """Documents are always scoped to their owner — no cross-user listing."""
    result = await db.execute(
        select(Document)
        .where(Document.owner_id == owner_id)
        .order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


async def get_document_for_user(
    db: AsyncSession, owner_id: uuid.UUID, document_id: uuid.UUID
) -> Document | None:
    """
    Returns None both when the document doesn't exist and when it belongs
    to someone else — the route layer turns that into a 404 either way, so
    we never reveal that another user's document exists.
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.owner_id == owner_id)
    )
    return result.scalar_one_or_none()
