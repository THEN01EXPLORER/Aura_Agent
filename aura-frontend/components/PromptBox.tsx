"use client";

import { useState } from "react";

interface PromptBoxProps {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
}

export default function PromptBox({ onSubmit, isLoading }: PromptBoxProps) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = prompt.trim();
    if (!trimmed || isLoading) return;
    onSubmit(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <label
        htmlFor="aura-prompt"
        className="mb-2 block text-xs font-semibold uppercase tracking-wider text-aura-muted"
      >
        Agent Instruction
      </label>
      <div className="flex gap-3">
        <input
          id="aura-prompt"
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder='e.g. "Delete my stale GitHub test repo named junk-test-repo"'
          className="input-field flex-1"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!prompt.trim() || isLoading}
          className="btn-primary whitespace-nowrap"
        >
          {isLoading ? (
            <>
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Planning…
            </>
          ) : (
            "Generate Plan"
          )}
        </button>
      </div>
      <p className="mt-2 text-xs text-aura-muted">
        Aura will classify your intent and enforce approval for destructive
        actions.
      </p>
    </form>
  );
}
