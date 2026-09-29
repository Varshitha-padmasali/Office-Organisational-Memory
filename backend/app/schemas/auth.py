"""
Pydantic schemas for auth requests/responses.

STATUS (Day 1): shapes are defined so the frontend login page and backend
route stub agree on a contract, but no route actually validates credentials
yet — see app/api/routes/auth.py.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None

    model_config = {"from_attributes": True}
