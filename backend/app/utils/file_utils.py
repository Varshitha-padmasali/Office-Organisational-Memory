"""
File-handling utilities for document uploads.

STATUS (Day 2): implemented for local-disk storage — enough for the MVP.
Swapping to S3/GCS later would only require changing save_upload_bytes();
callers (document_service.py) don't need to change.
"""

import uuid
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# backend/app/utils/file_utils.py -> parents[3] is the repo root, so a
# relative UPLOAD_DIR (the default) resolves the same way regardless of
# the process's current working directory (e.g. running uvicorn from
# backend/ vs. the repo root).
_REPO_ROOT = Path(__file__).resolve().parents[3]
_configured_dir = Path(settings.UPLOAD_DIR)
UPLOAD_DIR = _configured_dir if _configured_dir.is_absolute() else _REPO_ROOT / _configured_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def allowed_extension(filename: str) -> bool:
    """Whether the file's extension is in the upload allowlist."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def safe_filename(original_filename: str) -> str:
    """
    Generate a collision-safe filename for disk storage while preserving
    the original extension. The user-facing original filename is stored
    separately (Document.original_filename) for display purposes.
    """
    suffix = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{suffix}"


def save_upload_bytes(content: bytes, safe_name: str) -> str:
    """Writes bytes to disk and returns the storage path used."""
    destination = UPLOAD_DIR / safe_name
    destination.write_bytes(content)
    return str(destination)
