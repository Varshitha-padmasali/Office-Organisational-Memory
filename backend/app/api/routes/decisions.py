"""
Decisions routes.

STATUS (Day 1): stubbed. This router is registered in app/main.py so the
route exists and returns a clear, honest "not implemented" response
instead of fake data. Real implementation is planned for Day 6.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.get("/")
async def list_decisions() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Decisions endpoints are not implemented yet. Planned for Day 6.",
    )
