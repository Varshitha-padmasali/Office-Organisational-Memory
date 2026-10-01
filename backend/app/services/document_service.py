"""
Document service — orchestrates document upload/storage, listing, and (as
of Day 3) the extraction -> chunking -> embedding processing pipeline.
"""

import uuid
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.chunk import Chunk
from app.models.document import Document
from app.services import chunking_service, embedding_service, extraction_service
from app.utils.file_utils import safe_filename, save_upload_bytes

logger = get_logger(__name__)


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


async def process_document(db: AsyncSession, document: Document) -> Document:
    """
    Run the extraction -> chunking -> embedding pipeline for one document.

    STATUS (Day 3): implemented, and called automatically right after
    upload (see app/api/routes/documents.py). This function deliberately
    catches its own exceptions: a failure here (missing GEMINI_API_KEY, a
    corrupt or image-only file, etc.) marks the document "failed" rather
    than propagating — the file WAS saved successfully; only the
    RAG-readiness step failed, and that's reflected honestly in
    `document.status` instead of turning a successful upload into a 500.
    """
    try:
        text = extraction_service.extract_text(document.storage_path, document.original_filename)
        pieces = chunking_service.chunk_text(text)
        if not pieces:
            raise ValueError("Chunking produced no chunks from the extracted text.")

        vectors = embedding_service.embed_texts(pieces)

        for index, (piece, vector) in enumerate(zip(pieces, vectors)):
            db.add(
                Chunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=piece,
                    embedding=vector,
                )
            )

        document.status = "ready"
    except Exception as exc:  # noqa: BLE001 - any failure here means "failed", not a 500
        logger.warning("Processing failed for document %s: %s", document.id, exc)
        document.status = "failed"

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


async def list_chunks_for_document(db: AsyncSession, document_id: uuid.UUID) -> Sequence[Chunk]:
    result = await db.execute(
        select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index)
    )
    return result.scalars().all()


async def delete_chunks_for_document(db: AsyncSession, document_id: uuid.UUID) -> None:
    """Used before reprocessing, so a retry doesn't duplicate chunks."""
    await db.execute(delete(Chunk).where(Chunk.document_id == document_id))
    await db.commit()
