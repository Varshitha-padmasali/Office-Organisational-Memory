"""
Search routes.

STATUS (Day 1): stubbed. This router is registered in app/main.py so the
route exists and returns a clear, honest "not implemented" response
instead of fake data. Real implementation is planned for Day 4.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
async def list_search() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Search endpoints are not implemented yet. Planned for Day 4.",
    )
