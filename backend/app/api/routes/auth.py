"""
Auth routes.

STATUS (Day 1): stubbed. Endpoints exist so the API surface and frontend
contract are visible from day one, but they return HTTP 501 rather than
pretending to authenticate anyone. Real implementation (password
verification via app.core.security, JWT issuance, user lookup via
app.db.database) is planned for Day 2.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login is not implemented yet. Planned for Day 2.",
    )


@router.post("/register", response_model=TokenResponse)
async def register(payload: LoginRequest) -> TokenResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration is not implemented yet. Planned for Day 2.",
    )
