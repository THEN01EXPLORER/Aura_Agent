"""
Aura — Audit route.

GET /audit/logs
  Returns the append-only audit log entries from the database,
  ordered by most recent first.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import ApiResponse
from app.utils.auth import get_current_user
from app.services import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=ApiResponse)
async def get_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user_sub: str = Depends(get_current_user),
) -> ApiResponse:
    """Retrieve immutable audit log entries."""
    entries = audit_service.get_audit_logs(db, actor=user_sub, limit=limit, offset=offset)

    return ApiResponse(
        success=True,
        message=f"Retrieved {len(entries)} audit log entries.",
        data=[entry.model_dump() for entry in entries],
    )
