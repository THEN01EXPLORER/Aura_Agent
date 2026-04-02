"""
Aura — Deterministic Policy Engine.

Evaluates a planner output and returns a risk classification,
a decision (allow / require_approval), a human-readable reason,
and the OAuth scope required to carry out the action.

This module is PURE LOGIC — no I/O, no side effects.
"""

from __future__ import annotations

from app.models.schemas import (
    ActionType,
    PlannerOutput,
    PolicyDecision,
    PolicyResult,
    RiskLevel,
)

# ─── Risk / Scope mapping ────────────────────────────────

_RISK_MAP: dict[ActionType, RiskLevel] = {
    ActionType.READ_REPOS: RiskLevel.LOW,
    ActionType.CREATE_REPO: RiskLevel.LOW,
    ActionType.ARCHIVE_REPO: RiskLevel.MEDIUM,
    ActionType.DELETE_REPO: RiskLevel.HIGH,
}

_SCOPE_MAP: dict[ActionType, str] = {
    ActionType.READ_REPOS: "read:repos",
    ActionType.CREATE_REPO: "public_repo",
    ActionType.ARCHIVE_REPO: "write:repos",
    ActionType.DELETE_REPO: "delete:repos",
}

_POLICY_REASONS: dict[ActionType, str] = {
    ActionType.READ_REPOS: (
        "Listing repositories is a non-destructive read operation. "
        "Allowed without additional approval."
    ),
    ActionType.CREATE_REPO: (
        "Creating a new repository is a low-risk additive operation. "
        "Allowed without additional approval."
    ),
    ActionType.ARCHIVE_REPO: (
        "Archiving a repository is a reversible but impactful state change. "
        "Requires explicit human approval via step-up authentication."
    ),
    ActionType.DELETE_REPO: (
        "Deleting a repository is an irreversible destructive operation. "
        "Requires explicit human approval via MFA step-up authentication."
    ),
}

# ─── Public API ───────────────────────────────────────────


def evaluate_policy(plan: PlannerOutput) -> PolicyResult:
    """
    Evaluate a structured planner output and return the corresponding
    policy result.

    Rules
    -----
    • ``read_repos``   → low risk   → allow
    • ``archive_repo`` → medium risk → require_approval
    • ``delete_repo``  → high risk  → require_approval

    Additionally, if the planner's confidence is below 0.5 for ANY
    action, the decision is escalated to ``require_approval`` regardless
    of the base risk level.
    """
    risk = _RISK_MAP[plan.action]
    scope = _SCOPE_MAP[plan.action]

    # Base decision
    if risk == RiskLevel.LOW:
        decision = PolicyDecision.ALLOW
    else:
        decision = PolicyDecision.REQUIRE_APPROVAL

    # Confidence override — low confidence always escalates
    reason = _POLICY_REASONS[plan.action]
    if plan.confidence < 0.5:
        decision = PolicyDecision.REQUIRE_APPROVAL
        reason = (
            f"Planner confidence ({plan.confidence:.2f}) is below the 0.50 "
            f"threshold. Escalating to require human approval regardless of "
            f"base risk level ({risk.value})."
        )

    return PolicyResult(
        risk=risk,
        decision=decision,
        policy_reason=reason,
        required_scope=scope,
    )
