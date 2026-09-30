"""
Shared FastAPI dependencies used across route modules.

STATUS (Day 2): get_current_user is now fully implemented — it decodes
the bearer JWT (app.core.security, built on Day 1) and loads the
corresponding user from the database. Any route can now require auth by
adding `current_user: User = Depends(get_current_user)`.
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

# tokenUrl is only used to populate the "Authorize" button in /docs — our
# actual login endpoint takes JSON, not an OAuth2 form, but this scheme
# still correctly extracts `Authorization: Bearer <token>` from requests.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_error

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_error

    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise credentials_error

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_error

    return user
