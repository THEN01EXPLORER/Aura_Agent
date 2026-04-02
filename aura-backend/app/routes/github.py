"""
Aura — GitHub direct route.

GET /github/repos
  Convenience endpoint for reading the authenticated user's repos.
  Requests a low-risk read token from Auth0, then calls the GitHub
  service.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import get_db
from app.models.schemas import ApiResponse
from app.services import audit_service, auth0_service, github_service
from app.utils.auth import get_current_user

settings = get_settings()
router = APIRouter(prefix="/github", tags=["github"])


@router.get("/repos", response_model=ApiResponse)
async def list_repos(
    db: Session = Depends(get_db), 
    user_sub: str = Depends(get_current_user)
) -> ApiResponse:
    """List the authenticated user's GitHub repositories."""

    # Request a read-scoped token from Auth0 Token Vault
    token_result = auth0_service.request_scoped_token(
        user_sub=user_sub,
        scope="read:repos",
    )

    if token_result["status"] == "approval_required":
        audit_service.log_event(
            db=db,
            event_type="approval_requested",
            action="read_repos",
            target_repo=None,
            decision="blocked_pending_approval",
            actor=user_sub,
            metadata={"reason": "Unexpected approval required for read scope."},
        )
        return ApiResponse(
            success=False,
            message="Unexpected: approval required for read_repos.",
            data=token_result,
        )

    access_token = token_result["access_token"]
    repos = github_service.read_repos(access_token)

    audit_service.log_event(
        db=db,
        event_type="action_executed",
        action="read_repos",
        target_repo=None,
        decision="executed",
        actor=user_sub,
        metadata={"repo_count": len(repos)},
    )

    return ApiResponse(
        success=True,
        message=f"Retrieved {len(repos)} repositories.",
        data=repos,
    )
