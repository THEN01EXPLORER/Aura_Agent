"use client";

import type { AuditLog } from "@/lib/types";

interface AuditTableProps {
  logs: AuditLog[];
  isLoading: boolean;
}

const EVENT_COLORS: Record<string, string> = {
  plan_created: "text-indigo-400",
  policy_evaluated: "text-aura-accent-light",
  approval_requested: "text-yellow-400",
  approval_granted: "text-emerald-400",
  action_executed: "text-emerald-400",
  action_failed: "text-red-400",
};

function formatTimestamp(ts: string): string {
  try {
    const d = new Date(ts);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return ts;
  }
}

function MetadataDisplay({ raw }: { raw: string | null }) {
  if (!raw) return <span className="text-aura-muted">—</span>;
  try {
    const parsed = JSON.parse(raw);
    const entries = Object.entries(parsed);
    if (entries.length === 0) return <span className="text-aura-muted">{}</span>;

    return (
      <div className="grid grid-cols-1 gap-y-1 py-1">
        {entries.map(([key, val]) => (
          <div key={key} className="flex gap-2">
            <span className="shrink-0 font-mono text-[10px] font-bold uppercase tracking-tight text-aura-muted">
              {key.replace("_", " ")}:
            </span>
            <span className="truncate font-mono text-[10px] text-aura-text">
              {typeof val === "object" ? JSON.stringify(val) : String(val)}
            </span>
          </div>
        ))}
      </div>
    );
  } catch {
    return (
      <span className="font-mono text-[10px] text-red-400 opacity-70">
        Invalid Metadata
      </span>
    );
  }
}

export default function AuditTable({ logs, isLoading }: AuditTableProps) {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="mb-3 h-4 w-40 rounded bg-aura-border" />
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 rounded bg-aura-surface" />
          ))}
        </div>
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="card">
        <p className="text-sm text-aura-muted">No audit events recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden p-0">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-aura-border">
              <th className="table-header px-4 py-3">ID</th>
              <th className="table-header px-4 py-3">Timestamp</th>
              <th className="table-header px-4 py-3">Event</th>
              <th className="table-header px-4 py-3">Action</th>
              <th className="table-header px-4 py-3">Target</th>
              <th className="table-header px-4 py-3">Decision</th>
              <th className="table-header px-4 py-3">Actor</th>
              <th className="table-header px-4 py-3">Metadata</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-aura-border/50">
            {logs.map((log) => (
              <tr
                key={log.id}
                className="transition-colors hover:bg-aura-surface/50"
              >
                <td className="table-cell px-4 font-mono text-xs text-aura-muted">
                  #{log.id}
                </td>
                <td className="table-cell px-4 whitespace-nowrap font-mono text-xs">
                  {formatTimestamp(log.timestamp)}
                </td>
                <td className="table-cell px-4">
                  <span
                    className={`font-mono text-xs font-medium ${
                      EVENT_COLORS[log.event_type] || "text-aura-text"
                    }`}
                  >
                    {log.event_type}
                  </span>
                </td>
                <td className="table-cell px-4 font-mono text-xs">
                  {log.action}
                </td>
                <td className="table-cell px-4">
                  {log.target_repo ? (
                    <code className="rounded bg-aura-surface px-1.5 py-0.5 font-mono text-xs text-aura-accent-light">
                      {log.target_repo}
                    </code>
                  ) : (
                    <span className="text-xs text-aura-muted">—</span>
                  )}
                </td>
                <td className="table-cell px-4 font-mono text-xs">
                  {log.decision}
                </td>
                <td className="table-cell px-4 text-xs text-aura-muted">
                  {log.actor}
                </td>
                <td className="table-cell max-w-[240px] px-4 py-2">
                  <MetadataDisplay raw={log.metadata_json} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
