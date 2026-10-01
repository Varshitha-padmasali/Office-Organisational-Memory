"""
Chunking service — splits extracted text into retrieval-sized pieces.

STATUS (Day 3): implemented. Uses a simple fixed-size sliding window with
overlap, snapped forward to the next whitespace so chunks don't split a
word mid-token. This is a deliberately simple strategy for the MVP —
sentence- or paragraph-aware chunking would be a reasonable post-MVP
improvement, but isn't needed to prove out retrieval quality first.
"""

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 150

# How far past the target boundary we're willing to look for a whitespace
# to snap to, before giving up and just cutting at the target length.
_SNAP_SLACK = 50


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """
    Split `text` into overlapping chunks of at most `chunk_size` characters.

    `overlap` characters from the end of one chunk are repeated at the
    start of the next, so a fact split across a chunk boundary is still
    likely to appear whole in at least one chunk. Returns an empty list
    for empty/whitespace-only input.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and less than chunk_size")

    normalized = " ".join(text.split())  # collapse all whitespace runs to single spaces
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    length = len(normalized)

    while start < length:
        end = min(start + chunk_size, length)

        if end < length:
            next_space = normalized.find(" ", end)
            if next_space != -1 and next_space - end < _SNAP_SLACK:
                end = next_space

        piece = normalized[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= length:
            break

        start = end - overlap

    return chunks
