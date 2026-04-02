"use client";

import type { PolicyResult } from "@/lib/types";

interface PolicyCardProps {
  policy: PolicyResult;
}

const RISK_BADGE: Record<string, string> = {
  low: "badge-low",
  medium: "badge-medium",
  high: "badge-high",
};

export default function PolicyCard({ policy }: PolicyCardProps) {
  const isBlocking = policy.decision === "require_approval";

  return (
    <div className="card animate-slide-up">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-aura-muted">
          Policy Evaluation
        </h3>
        <span className={RISK_BADGE[policy.risk] || "badge"}>
          {policy.risk.toUpperCase()} RISK
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {/* Decision */}
        <div className="rounded-lg bg-aura-surface px-4 py-3">
          <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
            Decision
          </p>
          <p
            className={`font-mono text-sm font-semibold ${
              isBlocking ? "text-red-400" : "text-emerald-400"
            }`}
          >
            {policy.decision === "require_approval"
              ? "REQUIRE APPROVAL"
              : "ALLOW"}
          </p>
        </div>

        {/* Scope */}
        <div className="rounded-lg bg-aura-surface px-4 py-3">
          <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
            Required Scope
          </p>
          <p className="font-mono text-sm text-aura-accent-light">
            {policy.required_scope}
          </p>
        </div>

        {/* Reason */}
        <div className="col-span-full rounded-lg bg-aura-surface px-4 py-3">
          <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
            Policy Reason
          </p>
          <p className="text-sm text-aura-text">{policy.policy_reason}</p>
        </div>
      </div>

      {/* Visual trust indicator */}
      {isBlocking && (
        <div className="mt-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-2.5">
          <span className="text-base">🛡️</span>
          <p className="text-xs font-medium text-red-400">
            This action requires explicit human approval before execution.
          </p>
        </div>
      )}
    </div>
  );
}
