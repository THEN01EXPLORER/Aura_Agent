"use client";

import { useCallback, useEffect, useState } from "react";

import Header from "@/components/Header";
import StatusBanner from "@/components/StatusBanner";
import PromptBox from "@/components/PromptBox";
import RepoTable from "@/components/RepoTable";
import PlanCard from "@/components/PlanCard";
import PolicyCard from "@/components/PolicyCard";
import ApprovalPanel from "@/components/ApprovalPanel";
import ConfirmModal from "@/components/ConfirmModal";

import { generatePlan, executeAction, fetchRepos } from "@/lib/api";
import {
  AgentIntent,
  PolicyResult,
  ActionExecutionResponse,
  AppStatus,
  Repo,
  ActionType,
} from "@/lib/types";
import { useUser } from "@auth0/nextjs-auth0";

// ── Client-side policy derivation (mirrors backend rules) ─

function derivePolicy(intent: AgentIntent): PolicyResult {
  const policyMap: Record<
    ActionType,
    { risk: PolicyResult["risk"]; scope: string; reason: string }
  > = {
    read_repos: {
      risk: "low",
      scope: "read:repos",
      reason:
        "Listing repositories is a non-destructive read operation. Allowed without additional approval.",
    },
    create_repo: {
      risk: "low",
      scope: "public_repo",
      reason:
        "Creating a new repository is a low-risk additive operation. Allowed without additional approval.",
    },
    archive_repo: {
      risk: "medium",
      scope: "write:repos",
      reason:
        "Archiving a repository is a reversible but impactful state change. Requires explicit human approval via step-up authentication.",
    },
    delete_repo: {
      risk: "high",
      scope: "delete:repos",
      reason:
        "Deleting a repository is an irreversible destructive operation. Requires explicit human approval via MFA.",
    },
  };

  const entry = policyMap[intent.action];
  let decision: PolicyResult["decision"] =
    entry.risk === "low" ? "allow" : "require_approval";
  let reason = entry.reason;

  if (intent.confidence < 0.5) {
    decision = "require_approval";
    reason = `Planner confidence (${(intent.confidence * 100).toFixed(0)}%) is below threshold. Escalating to require human approval.`;
  }

  return {
    risk: entry.risk,
    decision,
    policy_reason: reason,
    required_scope: entry.scope,
  };
}

// ── Main Dashboard ───────────────────────────────────────

export default function DashboardPage() {
  const [status, setStatus] = useState<AppStatus>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // Data state
  const [repos, setRepos] = useState<Repo[]>([]);
  const [reposLoading, setReposLoading] = useState(true);
  const [intent, setIntent] = useState<AgentIntent | null>(null);
  const [policy, setPolicy] = useState<PolicyResult | null>(null);
  const [executionResult, setExecutionResult] =
    useState<ActionExecutionResponse | null>(null);

  // Confirmation state
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  const { user, isLoading: authLoading } = useUser();

  // ── Load repos on mount or auth change ─────────
  const refreshRepos = useCallback(async (sub: string) => {
    try {
      console.log("[Aura] Fetching repos for user:", sub);
      const res = await fetchRepos(sub);
      console.log("[Aura] Repos response:", res);
      setRepos(res.data ?? []);
    } catch (err) {
      console.error("[Aura] Failed to fetch repos:", err);
      setRepos([]);
    } finally {
      setReposLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authLoading) return;
    
    // Don't attempt to fetch repos if user is not logged in
    if (!user?.sub) {
      setReposLoading(false);
      return;
    }

    refreshRepos(user.sub);
  }, [user?.sub, authLoading, refreshRepos]);

  // ── Handle plan generation ─────────────────────────────
  const handlePlan = useCallback(async (prompt: string) => {
    setStatus("planning");
    setStatusMessage("Sending prompt to planner LLM…");
    setIntent(null);
    setPolicy(null);
    setExecutionResult(null);
    setErrorMessage("");

    try {
      const res = await generatePlan(prompt, user?.sub);
      const planData = res.data;
      setIntent(planData);
      setPolicy(derivePolicy(planData));
      setStatus("planned");
      setStatusMessage(`Plan generated: ${planData.action}`);
    } catch (err) {
      setStatus("error");
      const msg = err instanceof Error ? err.message : "Plan generation failed";
      setStatusMessage(msg);
      setErrorMessage(msg);
    }
  }, [user?.sub]);

  // ── Handle execution ───────────────────────────────────
  const handleExecute = useCallback(async () => {
    if (!intent) return;

    // Trigger confirmation for destructive actions
    if (
      (intent.action === "archive_repo" || intent.action === "delete_repo") &&
      !isConfirmOpen
    ) {
      setIsConfirmOpen(true);
      return;
    }

    // Close the confirmation modal
    setIsConfirmOpen(false);

    setStatus("executing");
    setStatusMessage(`Executing ${intent.action}…`);
    setExecutionResult(null);
    setErrorMessage("");

    try {
      const res = await executeAction(intent, user?.sub);
      setExecutionResult(res);

      if (!res.success && res.data?.status === "approval_required") {
        setStatus("blocked");
        setStatusMessage("Action blocked — step-up authentication required");
      } else {
        setStatus("executed");
        setStatusMessage(`${intent.action} completed successfully`);
        // Refresh repo list after successful data change
        if (user?.sub && (intent.action === "create_repo" || intent.action === "delete_repo" || intent.action === "archive_repo")) {
          refreshRepos(user.sub);
        }
      }
    } catch (err) {
      setStatus("error");
      const msg = err instanceof Error ? err.message : "Execution failed";
      setStatusMessage(msg);
      setErrorMessage(msg);
    }
  }, [intent, user?.sub, isConfirmOpen]);

  // ── Reset ──────────────────────────────────────────────
  const handleReset = useCallback(() => {
    setStatus("idle");
    setStatusMessage("");
    setIntent(null);
    setPolicy(null);
    setExecutionResult(null);
    setErrorMessage("");
  }, []);

  return (
    <div className="min-h-screen">
      <Header />

      <main className="mx-auto max-w-4xl space-y-6 px-6 py-8">
        {/* ── Status ────────────────────────────────── */}
        <div className="flex items-center justify-between gap-4">
          <StatusBanner status={status} message={statusMessage} />
          {status !== "idle" && (
            <button onClick={handleReset} className="btn-ghost text-xs">
              Reset
            </button>
          )}
        </div>

        {/* ── Prompt ────────────────────────────────── */}
        <PromptBox onSubmit={handlePlan} isLoading={status === "planning"} />

        {/* ── AI Plan ───────────────────────────────── */}
        {intent && <PlanCard intent={intent} />}

        {/* ── Policy Evaluation ─────────────────────── */}
        {policy && <PolicyCard policy={policy} />}

        {/* ── Execute Button ────────────────────────── */}
        {intent && !executionResult && status === "planned" && (
          <div className="flex justify-end">
            <button
              onClick={handleExecute}
              className={
                policy?.decision === "require_approval"
                  ? "btn-danger"
                  : "btn-primary"
              }
            >
              {policy?.decision === "require_approval"
                ? `Execute ${intent.action} (Requires Approval)`
                : `Execute ${intent.action}`}
            </button>
          </div>
        )}

        {/* ── Execution Result / Approval ───────────── */}
        {executionResult && (
          <ApprovalPanel response={executionResult} onRetry={handleExecute} />
        )}

        {/* ── Error ─────────────────────────────────── */}
        {errorMessage && status === "error" && !executionResult && (
          <div className="card border-red-500/30 bg-red-500/5 animate-slide-up">
            <p className="text-sm text-red-400">{errorMessage}</p>
          </div>
        )}

        {/* ── Repos ─────────────────────────────────── */}
        <RepoTable repos={repos} isLoading={reposLoading} />
      </main>

      {/* ── Confirmation Modal ────────────────────── */}
      {intent && (
        <ConfirmModal
          isOpen={isConfirmOpen}
          onClose={() => setIsConfirmOpen(false)}
          onConfirm={handleExecute}
          action={intent.action}
          targetRepo={intent.target_repo}
        />
      )}
    </div>
  );
}
