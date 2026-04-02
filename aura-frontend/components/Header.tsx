"use client";

import Link from "next/link";
import { useUser } from "@auth0/nextjs-auth0";

export default function Header() {
  const { user, isLoading } = useUser();

  return (
    <header className="sticky top-0 z-50 border-b border-aura-border bg-aura-bg/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        {/* ── Brand ──────────────────────────────── */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-aura-accent font-mono text-sm font-bold text-white transition-transform group-hover:scale-105">
            A
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-white">
              Aura
            </h1>
            <p className="text-[11px] leading-none text-aura-muted">
              AI That Can&apos;t Act Without You
            </p>
          </div>
        </Link>

        {/* ── Nav ────────────────────────────────── */}
        <nav className="flex items-center gap-6">
          <Link
            href="/audit"
            className="text-sm text-aura-muted transition-colors hover:text-aura-text"
          >
            Audit Log
          </Link>

          {/* Auth0 Status */}
          <div className="flex items-center gap-3 ml-2">
            {!isLoading && !user && (
              <a
                href="/auth/login"
                className="rounded-lg border border-aura-border bg-aura-surface px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-aura-border"
              >
                Log In
              </a>
            )}
            {!isLoading && user && (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 rounded-lg border border-aura-border bg-aura-surface px-3 py-1.5">
                  <div className="h-2 w-2 rounded-full bg-aura-success animate-pulse-slow" />
                  <span className="text-xs font-medium text-aura-muted">
                    {user.nickname || user.name || "Authenticated"}
                  </span>
                </div>
                <a
                  href="/auth/logout"
                  className="text-xs font-medium text-aura-muted transition-colors hover:text-aura-text"
                >
                  Log Out
                </a>
              </div>
            )}
            {isLoading && (
              <div className="h-8 w-24 rounded-lg bg-aura-surface animate-pulse" />
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
