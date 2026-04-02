"use client";

import type { AppStatus } from "@/lib/types";

interface StatusBannerProps {
  status: AppStatus;
  message?: string;
}

const STATUS_CONFIG: Record<
  AppStatus,
  { label: string; color: string; bgColor: string; icon: string }
> = {
  idle: {
    label: "Ready",
    color: "text-aura-muted",
    bgColor: "bg-aura-surface",
    icon: "○",
  },
  planning: {
    label: "Generating Plan…",
    color: "text-aura-accent-light",
    bgColor: "bg-indigo-500/10",
    icon: "◌",
  },
  planned: {
    label: "Plan Generated",
    color: "text-indigo-400",
    bgColor: "bg-indigo-500/10",
    icon: "◉",
  },
  executing: {
    label: "Executing…",
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10",
    icon: "⟳",
  },
  blocked: {
    label: "Approval Required",
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    icon: "⊘",
  },
  executed: {
    label: "Executed",
    color: "text-emerald-400",
    bgColor: "bg-emerald-500/10",
    icon: "✓",
  },
  error: {
    label: "Error",
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    icon: "✕",
  },
};

export default function StatusBanner({ status, message }: StatusBannerProps) {
  const cfg = STATUS_CONFIG[status];

  return (
    <div
      className={`flex items-center gap-3 rounded-lg border border-aura-border px-4 py-2.5 ${cfg.bgColor} transition-all animate-fade-in`}
    >
      <span className={`font-mono text-base ${cfg.color}`}>{cfg.icon}</span>
      <div className="flex flex-col">
        <span className={`text-sm font-medium ${cfg.color}`}>{cfg.label}</span>
        {message && (
          <span className="text-xs text-aura-muted">{message}</span>
        )}
      </div>
    </div>
  );
}
