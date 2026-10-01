"""
Text extraction service — pulls plain text out of uploaded documents.

STATUS (Day 3): implemented for the three formats the upload endpoint
accepts (.pdf, .docx, .txt). Called by document_service.process_document()
right after upload.
"""

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class ExtractionError(Exception):
    """Raised when a file's text can't be extracted."""


def extract_text(storage_path: str, original_filename: str) -> str:
    """
    Dispatch to the right extractor based on the original filename's
    extension, read the file from disk, and return its plain-text content.

    Raises ExtractionError for unsupported extensions or files that yield
    no usable text (empty files, image-only PDFs, etc.) — callers should
    treat that as a processing failure, not crash the whole request.
    """
    suffix = Path(original_filename).suffix.lower()
    path = Path(storage_path)

    if suffix == ".txt":
        text = _extract_txt(path)
    elif suffix == ".pdf":
        text = _extract_pdf(path)
    elif suffix == ".docx":
        text = _extract_docx(path)
    else:
        raise ExtractionError(f"Unsupported file type for extraction: {suffix}")

    text = text.strip()
    if not text:
        raise ExtractionError("No extractable text found in this file.")
    return text


def _extract_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def _extract_docx(path: Path) -> str:
    doc = DocxDocument(str(path))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)
