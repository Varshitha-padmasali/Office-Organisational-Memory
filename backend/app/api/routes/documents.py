"""
Documents routes.

STATUS (Day 3): upload now triggers the full extraction -> chunking ->
embedding pipeline synchronously (see document_service.process_document),
so a document's `status` is "ready" or "failed" by the time the upload
response comes back — there's no background worker yet, so "processing"
is never actually observable from the outside. /reprocess lets a user
retry after fixing the cause of a "failed" status (most commonly: adding
a GEMINI_API_KEY after the fact). /chunks exposes what processing
produced, for debugging/visibility ahead of Day 4's real search.
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.db.database import get_db
from app.models.user import User
from app.schemas.document import ChunkOut, DocumentOut
from app.services import document_service
from app.utils.file_utils import ALLOWED_EXTENSIONS, allowed_extension

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def _get_owned_document_or_404(
    db: AsyncSession, owner_id: uuid.UUID, document_id: uuid.UUID
):
    document = await document_service.get_document_for_user(db, owner_id, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found."
        )
    return document


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentOut:
    if not file.filename or not allowed_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty."
        )
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
        )

    document = await document_service.create_document(
        db,
        owner_id=current_user.id,
        original_filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        content=content,
    )

    # Synchronous for the MVP (no task queue yet) — see module docstring.
    document = await document_service.process_document(db, document)
    return document


@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentOut]:
    documents = await document_service.list_documents_for_user(db, current_user.id)
    return list(documents)


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentOut:
    return await _get_owned_document_or_404(db, current_user.id, document_id)


@router.post("/{document_id}/reprocess", response_model=DocumentOut)
async def reprocess_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentOut:
    document = await _get_owned_document_or_404(db, current_user.id, document_id)

    # Clear any chunks from a previous attempt so a retry doesn't duplicate them.
    await document_service.delete_chunks_for_document(db, document_id)
    return await document_service.process_document(db, document)


@router.get("/{document_id}/chunks", response_model=list[ChunkOut])
async def get_document_chunks(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChunkOut]:
    await _get_owned_document_or_404(db, current_user.id, document_id)
    chunks = await document_service.list_chunks_for_document(db, document_id)
    return list(chunks)
