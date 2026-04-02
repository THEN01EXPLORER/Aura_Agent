"use client";

import type { ActionExecutionResponse } from "@/lib/types";

interface ApprovalPanelProps {
  response: ActionExecutionResponse;
  onRetry?: () => void;
}

export default function ApprovalPanel({ response, onRetry }: ApprovalPanelProps) {
  const data = response.data;

  // Guard: if data is null, show fallback
  if (!data) {
    return (
      <div className="card animate-slide-up border-red-500/30 bg-red-500/5">
        <div className="flex items-center gap-3">
          <span className="text-lg">✕</span>
          <div>
            <h3 className="text-sm font-semibold text-red-400">No Data</h3>
            <p className="text-xs text-aura-muted">{response.message}</p>
          </div>
        </div>
      </div>
    );
  }

  const status = data.status;

  // ── Approval Required ──────────────────────────────────
  if (status === "approval_required") {
    return (
      <div className="card animate-slide-up border-red-500/30 bg-red-500/5">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/15">
            <span className="text-lg">⊘</span>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-red-400">
              Action Blocked — Approval Required
            </h3>
            <p className="text-xs text-aura-muted">
              Step-up authentication is required to proceed.
            </p>
          </div>
        </div>

        <div className="space-y-3">
          {data.approval_reference && (
            <div className="rounded-lg bg-aura-surface px-4 py-3">
              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
                Approval Reference
              </p>
              <p className="font-mono text-sm text-red-400">
                {data.approval_reference}
              </p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            {data.action && (
              <div className="rounded-lg bg-aura-surface px-4 py-3">
                <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
                  Action
                </p>
                <p className="font-mono text-sm text-aura-text">
                  {data.action}
                </p>
              </div>
            )}
            {data.risk && (
              <div className="rounded-lg bg-aura-surface px-4 py-3">
                <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
                  Risk Level
                </p>
                <p className={`font-mono text-sm font-semibold badge-${data.risk} inline-block`}>
                  {data.risk.toUpperCase()}
                </p>
              </div>
            )}
          </div>

          {data.policy_reason && (
            <div className="rounded-lg bg-aura-surface px-4 py-3">
              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
                Policy Reason
              </p>
              <p className="text-sm text-aura-text">{data.policy_reason}</p>
            </div>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between rounded-lg border border-aura-border bg-aura-card px-4 py-3">
          <p className="text-xs text-aura-muted">
            Complete MFA in Auth0 to approve this action, then retry.
          </p>
          {onRetry && (
            <button onClick={onRetry} className="btn-ghost text-xs">
              Retry after approval
            </button>
          )}
        </div>
      </div>
    );
  }

  // ── Executed Successfully ──────────────────────────────
  if (status === "executed" || response.success) {
    return (
      <div className="card animate-slide-up border-emerald-500/30 bg-emerald-500/5">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/15">
            <span className="text-lg">✓</span>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-emerald-400">
              Action Executed Successfully
            </h3>
            <p className="text-xs text-aura-muted">{response.message}</p>
          </div>
        </div>

        {data?.result && (
          <div className="rounded-lg bg-aura-surface px-4 py-3">
            <p className="mb-2 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
              Result
            </p>
            <pre className="overflow-x-auto font-mono text-xs text-aura-text">
              {JSON.stringify(data.result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  }

  // ── Fallback error state ───────────────────────────────
  return (
    <div className="card animate-slide-up border-red-500/30 bg-red-500/5">
      <div className="flex items-center gap-3">
        <span className="text-lg">✕</span>
        <div>
          <h3 className="text-sm font-semibold text-red-400">
            Unexpected Response
          </h3>
          <p className="text-xs text-aura-muted">{response.message}</p>
        </div>
      </div>
    </div>
  );
}
