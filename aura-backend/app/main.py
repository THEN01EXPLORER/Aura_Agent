"""
Aura — FastAPI application entry-point.

Responsibilities:
  • Create the FastAPI app instance
  • Register CORS / middleware
  • Include route routers (when they are built)
  • Expose a health-check endpoint
  • Bootstrap the database on startup
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.database import create_tables
from app.models.schemas import ApiResponse


# ─── Lifespan ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run one-time startup / shutdown logic."""
    # Startup — ensure database tables exist
    create_tables()
    yield
    # Shutdown — nothing to tear down for SQLite


# ─── App Factory ──────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "Zero-trust permission firewall for local AI agents. "
        "AI can plan actions, but cannot execute destructive actions "
        "without explicit human approval."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ─── CORS (wide-open for local dev; tighten in production) ──

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check ─────────────────────────────────────────


@app.get("/health", response_model=ApiResponse, tags=["system"])
async def health_check() -> ApiResponse:
    """Liveness probe — returns 200 when the service is up."""
    return ApiResponse(success=True, message="Aura is running.")


# ─── Route Registration ──────────────────────────────────

from app.routes import planner, actions, github, audit  # noqa: E402

app.include_router(planner.router)
app.include_router(actions.router)
app.include_router(github.router)
app.include_router(audit.router)
