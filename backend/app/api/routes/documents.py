"""
Documents routes.

STATUS (Day 2): upload + list + get-by-id are implemented for real,
storing files on local disk (app/utils/file_utils.py) and metadata in
Postgres. Every route requires authentication and documents are strictly
scoped to their owner. Text extraction and chunking are still Day 3 —
uploaded documents stay in "uploaded" status until then.
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.db.database import get_db
from app.models.user import User
from app.schemas.document import DocumentOut
from app.services import document_service
from app.utils.file_utils import ALLOWED_EXTENSIONS, allowed_extension

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


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
    document = await document_service.get_document_for_user(db, current_user.id, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found."
        )
    return document
