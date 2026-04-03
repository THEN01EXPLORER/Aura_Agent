// ──────────────────────────────────────────────────────────
// Aura — API Client
// Typed fetch helpers for the FastAPI backend
// ──────────────────────────────────────────────────────────

import type {
  AgentIntent,
  ApiResponse,
  AuditLog,
  ActionExecutionResponse,
  Repo,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// ── Generic fetcher ──────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  userSub?: string | null
): Promise<T> {
  const url = `${BASE}${path}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (userSub) {
    headers.set("X-User-Sub", userSub);
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch {
      // response body not JSON — keep statusText
    }
    throw new Error(detail || `Error ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ── Planner ──────────────────────────────────────────────

export async function generatePlan(
  prompt: string,
  userSub?: string | null
): Promise<ApiResponse<AgentIntent>> {
  return apiFetch<ApiResponse<AgentIntent>>(
    "/planner/plan",
    {
      method: "POST",
      body: JSON.stringify({ prompt }),
    },
    userSub
  );
}

// ── Action Execution ─────────────────────────────────────

export async function executeAction(
  intent: AgentIntent,
  userSub?: string | null
): Promise<ActionExecutionResponse> {
  return apiFetch<ActionExecutionResponse>(
    "/actions/execute",
    {
      method: "POST",
      body: JSON.stringify(intent),
    },
    userSub
  );
}

// ── GitHub ────────────────────────────────────────────────

export async function fetchRepos(userSub?: string | null): Promise<ApiResponse<Repo[]>> {
  return apiFetch<ApiResponse<Repo[]>>("/github/repos", {}, userSub);
}

// ── Audit ────────────────────────────────────────────────

export async function fetchAuditLogs(userSub?: string | null): Promise<ApiResponse<AuditLog[]>> {
  return apiFetch<ApiResponse<AuditLog[]>>("/audit/logs", {}, userSub);
}
