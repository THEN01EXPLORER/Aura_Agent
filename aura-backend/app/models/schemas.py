"""
Aura — Pydantic v2 models (schemas) for every boundary in the system.

Covers:
  • Planner input / output
  • Policy engine output
  • GitHub action results
  • Audit log records
  • Generic API envelope
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Enumerations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ActionType(str, enum.Enum):
    READ_REPOS = "read_repos"
    CREATE_REPO = "create_repo"
    ARCHIVE_REPO = "archive_repo"
    DELETE_REPO = "delete_repo"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PolicyDecision(str, enum.Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"


class EventType(str, enum.Enum):
    PLAN_CREATED = "plan_created"
    POLICY_EVALUATED = "policy_evaluated"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    ACTION_EXECUTED = "action_executed"
    ACTION_FAILED = "action_failed"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Planner
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class PlannerRequest(BaseModel):
    """User prompt forwarded to the planner LLM."""

    prompt: str = Field(
        ..., min_length=1, description="Natural-language instruction from the user"
    )


class PlannerOutput(BaseModel):
    """
    Strict JSON contract returned by the planner LLM.
    The OpenAI call MUST produce exactly this shape.
    """

    action: ActionType
    target_repo: Optional[str] = Field(
        default=None,
        description="Repository in owner/repo format; null for read actions",
    )
    reason: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)

    @field_validator("target_repo")
    @classmethod
    def read_actions_must_have_null_target(
        cls, v: Optional[str], info: Any
    ) -> Optional[str]:
        action = info.data.get("action")
        if action == ActionType.READ_REPOS and v is not None:
            raise ValueError("target_repo must be null for read_repos action")
        if action in (ActionType.CREATE_REPO, ActionType.ARCHIVE_REPO, ActionType.DELETE_REPO) and not v:
            raise ValueError(
                f"target_repo is required for {action} action"
            )
        return v


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Policy Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class PolicyResult(BaseModel):
    """Deterministic risk assessment produced by the policy engine."""

    risk: RiskLevel
    decision: PolicyDecision
    policy_reason: str
    required_scope: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GitHub Execution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class GitHubActionResult(BaseModel):
    """Standardized result envelope for every GitHub API operation."""

    success: bool
    action: ActionType
    target_repo: Optional[str] = None
    detail: str
    data: Optional[Any] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Audit Log
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class AuditEntry(BaseModel):
    """Single immutable audit record."""

    id: int
    timestamp: str = Field(
        description="UTC ISO-8601 timestamp of the event"
    )
    event_type: EventType
    action: str
    target_repo: Optional[str] = None
    decision: str
    actor: str
    metadata_json: Optional[str] = None


class AuditCreate(BaseModel):
    """Payload accepted by the audit service to create a new entry."""

    event_type: EventType
    action: str
    target_repo: Optional[str] = None
    decision: str
    actor: str = "system"
    metadata_json: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Generic API Envelope
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ApiResponse(BaseModel):
    """Uniform wrapper returned by every endpoint."""

    success: bool = True
    message: str = ""
    data: Optional[Any] = None
