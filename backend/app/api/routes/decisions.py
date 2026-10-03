"""
Decisions routes.

STATUS (Day 6): implemented for real. Decisions are created as a
side-effect of processing a meeting (app.api.routes.meetings) or
explicitly extracting them from a document
(POST /api/v1/documents/{id}/extract-decisions, in
app.api.routes.documents) - there is no direct "create decision" endpoint,
since a decision without a source document/meeting would have nothing
grounding it.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.decision import DecisionOut
from app.services import decision_service

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.get("/", response_model=list[DecisionOut])
async def list_decisions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DecisionOut]:
    rows = await decision_service.list_decisions_for_user(db, current_user.id)
    return [decision_service.to_decision_out(d, title, name) for d, title, name in rows]


@router.get("/{decision_id}", response_model=DecisionOut)
async def get_decision(
    decision_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DecisionOut:
    row = await decision_service.get_decision_for_user(db, current_user.id, decision_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")
    decision, title, name = row
    return decision_service.to_decision_out(decision, title, name)
