"""
Aura — Actions orchestration route.

POST /actions/execute
  Core orchestration endpoint.  Receives a structured action payload,
  evaluates policy, requests a scoped token from Auth0, and either
  executes immediately or returns an approval-required response.
  Every stage is immutably audited.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.utils.auth import get_current_user
from app.models.schemas import (
    ActionType,
    ApiResponse,
    PlannerOutput,
    PolicyDecision,
)
from app.config import get_settings
from app.services import (
    audit_service,
    auth0_service,
    github_service,
    policy_service,
)

settings = get_settings()
router = APIRouter(prefix="/actions", tags=["actions"])


def _execute_github_action(
    action: ActionType,
    token: str,
    target_repo: str | None,
) -> dict:
    """
    Dispatch to the correct github_service function based on action type.
    """
    if action == ActionType.READ_REPOS:
        repos = github_service.read_repos(token)
        return {"repos": repos, "count": len(repos)}

    if action == ActionType.CREATE_REPO:
        if not target_repo:
            raise HTTPException(status_code=400, detail="target_repo is required for create_repo.")
        return github_service.create_repo(token, target_repo)

    if action == ActionType.ARCHIVE_REPO:
        if not target_repo:
            raise HTTPException(status_code=400, detail="target_repo is required for archive_repo.")
        return github_service.archive_repo(token, target_repo)

    if action == ActionType.DELETE_REPO:
        if not target_repo:
            raise HTTPException(status_code=400, detail="target_repo is required for delete_repo.")
        return github_service.delete_repo(token, target_repo)

    raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")


@router.post("/execute", response_model=ApiResponse)
async def execute_action(
    payload: PlannerOutput,
    db: Session = Depends(get_db),
    user_sub: str = Depends(get_current_user)
) -> ApiResponse:
    """
    Orchestrate the full plan → policy → auth → execute → audit pipeline.

    Flow
    ----
    1. Evaluate policy
    2. Log policy evaluation
    3. Request scoped token from Auth0
    4. If approved  → execute GitHub action, log result
    5. If approval_required → return approval-required response, log blocked
    """
    # ── 1. Policy evaluation ──────────────────────────────
    policy = policy_service.evaluate_policy(payload)

    audit_service.log_event(
        db=db,
        event_type="policy_evaluated",
        action=payload.action.value,
        target_repo=payload.target_repo,
        decision=policy.decision.value,
        actor=user_sub,
        metadata={
            "risk": policy.risk.value,
            "policy_reason": policy.policy_reason,
            "required_scope": policy.required_scope,
            "confidence": payload.confidence,
        },
    )

    # ── 2. Request scoped token from Auth0 ────────────────
    token_result = auth0_service.request_scoped_token(
        user_sub=user_sub,
        scope=policy.required_scope,
    )

    # ── 3. Handle approval-required ───────────────────────
    if token_result["status"] == "approval_required":
        audit_service.log_event(
            db=db,
            event_type="approval_requested",
            action=payload.action.value,
            target_repo=payload.target_repo,
            decision="blocked_pending_approval",
            actor=user_sub,
            metadata={
                "approval_reference": token_result.get("approval_reference"),
                "message": token_result.get("message"),
                "required_scope": policy.required_scope,
            },
        )

        return ApiResponse(
            success=False,
            message="Action requires human approval via step-up authentication.",
            data={
                "status": "approval_required",
                "action": payload.action.value,
                "target_repo": payload.target_repo,
                "risk": policy.risk.value,
                "approval_reference": token_result.get("approval_reference"),
                "policy_reason": policy.policy_reason,
            },
        )

    # ── 4. Token approved — execute GitHub action ─────────
    access_token = token_result["access_token"]

    try:
        result = _execute_github_action(
            action=payload.action,
            token=access_token,
            target_repo=payload.target_repo,
        )
    except HTTPException as exc:
        audit_service.log_event(
            db=db,
            event_type="action_failed",
            action=payload.action.value,
            target_repo=payload.target_repo,
            decision="execution_failed",
            actor=user_sub,
            metadata={"error": exc.detail},
        )
        raise

    # ── 5. Log success ────────────────────────────────────
    audit_service.log_event(
        db=db,
        event_type="action_executed",
        action=payload.action.value,
        target_repo=payload.target_repo,
        decision="executed",
        actor=user_sub,
        metadata={"result": result},
    )

    return ApiResponse(
        success=True,
        message=f"Action '{payload.action.value}' executed successfully.",
        data={
            "action": payload.action.value,
            "target_repo": payload.target_repo,
            "risk": policy.risk.value,
            "result": result,
        },
    )
