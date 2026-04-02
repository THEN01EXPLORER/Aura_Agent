"use client";

import type { Repo } from "@/lib/types";

interface RepoTableProps {
  repos: Repo[];
  isLoading: boolean;
}

export default function RepoTable({ repos, isLoading }: RepoTableProps) {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="mb-3 h-4 w-32 rounded bg-aura-border" />
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-10 rounded bg-aura-surface" />
          ))}
        </div>
      </div>
    );
  }

  if (repos.length === 0) {
    return (
      <div className="card flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-aura-surface text-aura-muted">
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
        </div>
        <h4 className="text-sm font-medium text-white">No repositories found</h4>
        <p className="mt-1 max-w-xs text-xs text-aura-muted">
          Connect your GitHub account or use the agent to create your first repository.
        </p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden p-0">
      <div className="border-b border-aura-border px-5 py-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-aura-muted">
          GitHub Repositories
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-aura-border">
              <th className="table-header px-5 py-3">Name</th>
              <th className="table-header px-5 py-3">Full Name</th>
              <th className="table-header px-5 py-3">Visibility</th>
              <th className="table-header px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-aura-border/50">
            {repos.map((repo) => (
              <tr
                key={repo.full_name}
                className="group transition-colors hover:bg-aura-surface/60"
              >
                <td className="table-cell px-5 font-medium text-aura-text transition-colors group-hover:text-white">
                  {repo.name}
                </td>
                <td className="table-cell px-5">
                  <code className="rounded bg-aura-surface px-1.5 py-0.5 font-mono text-xs text-aura-accent-light">
                    {repo.full_name}
                  </code>
                </td>
                <td className="table-cell px-5">
                  <span
                    className={`badge ${
                      repo.private
                        ? "bg-yellow-500/15 text-yellow-400 ring-1 ring-yellow-500/25"
                        : "bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/25"
                    }`}
                  >
                    {repo.private ? "Private" : "Public"}
                  </span>
                </td>
                <td className="table-cell px-5">
                  {repo.archived ? (
                    <span className="badge bg-aura-muted/15 text-aura-muted ring-1 ring-aura-muted/25">
                      Archived
                    </span>
                  ) : (
                    <span className="badge bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/25">
                      Active
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
