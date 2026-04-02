"use client";

import type { AgentIntent } from "@/lib/types";

interface PlanCardProps {
  intent: AgentIntent;
}

export default function PlanCard({ intent }: PlanCardProps) {
  const confidencePct = Math.round(intent.confidence * 100);

  const actionColor =
    intent.action === "delete_repo"
      ? "text-red-400"
      : intent.action === "archive_repo"
        ? "text-yellow-400"
        : "text-emerald-400";

  return (
    <div className="card animate-slide-up">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-aura-muted">
          AI Plan
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-aura-muted">Confidence</span>
          <div className="flex items-center gap-1.5">
            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-aura-surface">
              <div
                className={`h-full rounded-full transition-all ${
                  confidencePct >= 70
                    ? "bg-emerald-500"
                    : confidencePct >= 50
                      ? "bg-yellow-500"
                      : "bg-red-500"
                }`}
                style={{ width: `${confidencePct}%` }}
              />
            </div>
            <span className="font-mono text-xs text-aura-text">
              {confidencePct}%
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {/* Action */}
        <div className="rounded-lg bg-aura-surface px-4 py-3">
          <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
            Action
          </p>
          <p className={`font-mono text-sm font-semibold ${actionColor}`}>
            {intent.action}
          </p>
        </div>

        {/* Target */}
        <div className="rounded-lg bg-aura-surface px-4 py-3">
          <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
            Target Repository
          </p>
          <p className="font-mono text-sm text-aura-text">
            {intent.target_repo || "—"}
          </p>
        </div>

        {/* Reason */}
        <div className="col-span-full rounded-lg bg-aura-surface px-4 py-3">
          <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-aura-muted">
            Reason
          </p>
          <p className="text-sm text-aura-text">{intent.reason}</p>
        </div>
      </div>
    </div>
  );
}
