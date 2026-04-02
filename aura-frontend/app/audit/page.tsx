"use client";

import { useCallback, useEffect, useState } from "react";

import Header from "@/components/Header";
import AuditTable from "@/components/AuditTable";
import { fetchAuditLogs } from "@/lib/api";
import type { AuditLog } from "@/lib/types";

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadLogs = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetchAuditLogs();
      setLogs(res.data ?? []);
    } catch {
      setLogs([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  return (
    <div className="min-h-screen">
      <Header />

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        {/* ── Page Header ─────────────────────────────── */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Audit Trail</h2>
            <p className="mt-1 text-sm text-aura-muted">
              Immutable record of every action planned, evaluated, and executed
              through Aura.
            </p>
          </div>
          <button onClick={loadLogs} className="btn-ghost text-xs">
            Refresh
          </button>
        </div>

        {/* ── Stats ───────────────────────────────────── */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="card text-center">
            <p className="text-2xl font-bold text-white">{logs.length}</p>
            <p className="text-xs text-aura-muted">Total Events</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-emerald-400">
              {logs.filter((l) => l.event_type === "action_executed").length}
            </p>
            <p className="text-xs text-aura-muted">Executed</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-yellow-400">
              {logs.filter((l) => l.event_type === "approval_requested").length}
            </p>
            <p className="text-xs text-aura-muted">Approvals Requested</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-red-400">
              {logs.filter((l) => l.event_type === "action_failed").length}
            </p>
            <p className="text-xs text-aura-muted">Failed</p>
          </div>
        </div>

        {/* ── Table ───────────────────────────────────── */}
        <AuditTable logs={logs} isLoading={isLoading} />
      </main>
    </div>
  );
}
