"""
Documents routes.

STATUS (Day 1): stubbed. This router is registered in app/main.py so the
route exists and returns a clear, honest "not implemented" response
instead of fake data. Real implementation is planned for Day 2-3.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
async def list_documents() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Documents endpoints are not implemented yet. Planned for Day 2-3.",
    )
