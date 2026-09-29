"""
Knowledge gap routes.

STATUS (Day 1): stubbed. This router is registered in app/main.py so the
route exists and returns a clear, honest "not implemented" response
instead of fake data. Real implementation is planned for Day 7.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/knowledge-gaps", tags=["knowledge_gaps"])


@router.get("/")
async def list_knowledge_gaps() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Knowledge gap endpoints are not implemented yet. Planned for Day 7.",
    )
