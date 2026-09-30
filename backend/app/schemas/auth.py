"""
Pydantic schemas for auth requests/responses.

STATUS (Day 2): implemented for real — these are the exact shapes used by
the now-functional /api/v1/auth/* routes.
"""

import uuid

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None

    model_config = {"from_attributes": True}
