"use client";

// ──────────────────────────────────────────────────────────
// Aura — Providers wrapper
//
// Structured so Auth0 (or any future context provider)
// can be plugged in without touching layout.tsx.
// ──────────────────────────────────────────────────────────

import React from "react";
import { Auth0Provider } from "@auth0/nextjs-auth0";

interface ProvidersProps {
  children: React.ReactNode;
}

export default function Providers({ children }: ProvidersProps) {
  return <Auth0Provider>{children}</Auth0Provider>;
}
