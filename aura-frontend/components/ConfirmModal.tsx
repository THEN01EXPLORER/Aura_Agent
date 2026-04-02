"use client";

import { useEffect, useState } from "react";
import { ActionType } from "@/lib/types";

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  action: ActionType;
  targetRepo: string | null;
}

export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  action,
  targetRepo,
}: ConfirmModalProps) {
  const [isRendered, setIsRendered] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsRendered(true);
    } else {
      const timer = setTimeout(() => setIsRendered(false), 200);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  if (!isRendered) return null;

  const isDestructive = action === "delete_repo";
  const actionLabel = action.replace("_", " ");

  return (
    <div
      className={`fixed inset-0 z-[100] flex items-center justify-center px-4 transition-opacity duration-200 ${
        isOpen ? "opacity-100" : "opacity-0"
      }`}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className={`relative w-full max-w-md transform overflow-hidden rounded-2xl border border-aura-border bg-aura-surface p-6 shadow-2xl transition-all duration-200 ${
          isOpen ? "scale-100 opacity-100" : "scale-95 opacity-0"
        }`}
      >
        <div className="flex items-center gap-4">
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-xl ${
              isDestructive ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"
            }`}
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-white capitalize">
              Confirm {actionLabel}
            </h3>
            <p className="text-sm text-aura-muted">
              You are about to {actionLabel}{" "}
              <span className="font-mono text-aura-text">{targetRepo}</span>.
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-4">
          <div className="rounded-lg bg-aura-bg/50 p-4 border border-aura-border/50">
            <p className="text-xs leading-relaxed text-aura-muted">
              {isDestructive
                ? "This action is PERMANENT and cannot be undone. All data, issues, and settings for this repository will be lost forever."
                : "This action will hide the repository from public view and make it read-only. This can be reversed later in GitHub settings."}
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 rounded-xl border border-aura-border bg-aura-surface py-2.5 text-sm font-medium text-white transition-colors hover:bg-aura-border"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className={`flex-1 rounded-xl py-2.5 text-sm font-bold text-white transition-all hover:scale-[1.02] active:scale-[0.98] ${
                isDestructive
                  ? "bg-gradient-to-r from-red-600 to-rose-500 shadow-lg shadow-red-500/20"
                  : "bg-gradient-to-r from-yellow-600 to-orange-500 shadow-lg shadow-yellow-500/20"
              }`}
            >
              Confirm {actionLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
