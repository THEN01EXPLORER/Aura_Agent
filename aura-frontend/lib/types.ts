// ──────────────────────────────────────────────────────────
// Aura — Shared Frontend Types
// Aligned with backend Pydantic contracts
// ──────────────────────────────────────────────────────────

export type ActionType = "read_repos" | "create_repo" | "archive_repo" | "delete_repo";

export type RiskLevel = "low" | "medium" | "high";

export type Decision = "allow" | "require_approval";

export type EventType =
  | "plan_created"
  | "policy_evaluated"
  | "approval_requested"
  | "approval_granted"
  | "action_executed"
  | "action_failed";

export type AppStatus =
  | "idle"
  | "planning"
  | "planned"
  | "executing"
  | "blocked"
  | "executed"
  | "error";

// ── Planner ──────────────────────────────────────────────

export interface AgentIntent {
  action: ActionType;
  target_repo: string | null;
  reason: string;
  confidence: number;
}

// ── Policy ───────────────────────────────────────────────

export interface PolicyResult {
  risk: RiskLevel;
  decision: Decision;
  policy_reason: string;
  required_scope: string;
}

// ── GitHub ────────────────────────────────────────────────

export interface Repo {
  name: string;
  full_name: string;
  private: boolean;
  html_url?: string;
  description?: string | null;
  archived: boolean;
}

// ── Action Execution ─────────────────────────────────────

export interface ActionExecutionResponse {
  success: boolean;
  message: string;
  data: {
    status?: "approval_required" | "executed";
    action?: string;
    target_repo?: string | null;
    risk?: RiskLevel;
    approval_reference?: string;
    policy_reason?: string;
    result?: Record<string, unknown>;
  } | null;
}

// ── Audit ────────────────────────────────────────────────

export interface AuditLog {
  id: number;
  timestamp: string;
  event_type: EventType;
  action: string;
  target_repo: string | null;
  decision: string;
  actor: string;
  metadata_json: string | null;
}

// ── API Envelope ─────────────────────────────────────────

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
}
