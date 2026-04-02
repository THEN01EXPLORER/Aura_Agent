"""
Aura — Planner route.

POST /planner/plan
  Accepts a natural-language prompt, generates a structured intent
  via the planner LLM, and returns it.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import get_db
from app.models.schemas import ApiResponse, PlannerRequest, PlannerOutput
from app.services import planner_service, audit_service
from app.utils.auth import get_current_user

settings = get_settings()
router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/plan", response_model=ApiResponse)
async def plan(
    request: PlannerRequest, 
    db: Session = Depends(get_db),
    user_sub: str = Depends(get_current_user)
) -> ApiResponse:
    """Generate a structured intent from a natural-language prompt."""
    intent: PlannerOutput = planner_service.generate_intent(request.prompt)

    # Audit: record that a plan was created
    audit_service.log_event(
        db=db,
        event_type="plan_created",
        action=intent.action.value,
        target_repo=intent.target_repo,
        decision="n/a",
        actor=user_sub,
        metadata={
            "prompt": request.prompt,
            "confidence": intent.confidence,
            "reason": intent.reason,
        },
    )

    return ApiResponse(
        success=True,
        message="Intent generated successfully.",
        data=intent.model_dump(),
    )
