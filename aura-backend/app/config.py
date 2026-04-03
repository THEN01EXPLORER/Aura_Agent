"""
Aura — Centralized configuration via environment variables.
All secrets and tunables are loaded once here with explicit identity separation.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application-wide settings.
    Values are read from environment variables or a `.env` file.
    """

    # ── App ───────────────────────────────────────────────
    app_name: str = "Aura"
    debug: bool = False
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins for the API",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Handle both JSON arrays and comma-separated strings for CORS."""
        if isinstance(v, str):
            # Try parsing as JSON first (e.g. '["http://..."]')
            try:
                import json
                decoded = json.loads(v)
                if isinstance(decoded, list):
                    return [str(item).strip() for item in decoded]
            except (ValueError, TypeError):
                pass
            # Fallback to comma-separated (e.g. 'http://..., https://...')
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    default_user_sub: str = Field(
        default="demo-user",
        description="Fallback user identity for demo purposes",
    )

    # ── Database ──────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./aura.db",
        description="SQLAlchemy connection string (SQLite by default)",
    )

    # ── OpenAI ────────────────────────────────────────────
    openai_api_key: str = Field(
        ..., description="OpenAI API key for the planner LLM"
    )
    openai_model: str = Field(
        default="gpt-5-nano",
        description="Model identifier passed to the Chat Completions API",
    )

    # ── Auth0 Tenant & API ────────────────────────────────
    auth0_domain: str = Field(..., description="Auth0 tenant domain (e.g. dev-xxx.us.auth0.com)")
    auth0_audience: str = Field(
        ..., description="Auth0 API audience identifier for Aura API"
    )
    auth0_token_vault_connection: str = Field(
        default="github",
        description="Auth0 Token Vault connection name for GitHub",
    )

    # ── Auth0 Frontend App (Regular Web App) ──────────────
    # Used for user login and Session-to-Token exchange
    auth0_frontend_client_id: str = Field(
        ..., description="Auth0 Client ID for the Aura Frontend application"
    )
    auth0_frontend_client_secret: str = Field(
        ..., description="Auth0 Client Secret for the Aura Frontend application"
    )

    # ── Auth0 Backend App (M2M) ───────────────────────────
    # Used for backend management token and service-to-service calls
    auth0_backend_m2m_client_id: str = Field(
        ..., description="Auth0 Client ID for the Aura Backend (M2M) application"
    )
    auth0_backend_m2m_client_secret: str = Field(
        ..., description="Auth0 Client Secret for the Aura Backend (M2M) application"
    )

    # ── GitHub ────────────────────────────────────────────
    github_api_base: str = Field(
        default="https://api.github.com",
        description="GitHub REST API base URL",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    return Settings()  # type: ignore[call-arg]
