"""
Aura — Auth0 Token Mediation Service.

Encapsulates all Auth0-specific logic:
  • Machine-to-machine token exchange
  • GitHub token retrieval via Management API (user identities)
  • Step-up authentication detection

All token lifecycle management is isolated here so the rest of
the codebase never touches Auth0 directly.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests
from fastapi import HTTPException

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ─── Auth0 endpoints derived from domain ──────────────────

_TOKEN_URL = f"https://{settings.auth0_domain}/oauth/token"
_MGMT_API_BASE = f"https://{settings.auth0_domain}/api/v2"

# ── Global Token Cache ──────────────────────────────────
_MGMT_TOKEN_CACHE: dict[str, Any] = {
    "access_token": None,
    "expires_at": 0,
}


def _get_management_token() -> str:
    """
    Obtain an Auth0 Management API access token via client-credentials
    grant.  Includes simple in-memory caching to avoid redundant requests.

    Raises
    ------
    HTTPException
    503 on any Auth0 communication failure.
    """
    global _MGMT_TOKEN_CACHE

    # Return cached token if valid (with 60s buffer)
    now = time.time()
    if _MGMT_TOKEN_CACHE["access_token"] and _MGMT_TOKEN_CACHE["expires_at"] > now + 60:
        return _MGMT_TOKEN_CACHE["access_token"]

    logger.info("Requesting new Auth0 Management API token...")
    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.auth0_backend_m2m_client_id,
        "client_secret": settings.auth0_backend_m2m_client_secret,
        "audience": f"https://{settings.auth0_domain}/api/v2/",
    }

    try:
        resp = requests.post(_TOKEN_URL, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Auth0 management token request failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Auth0 management token exchange failed: {exc}",
        ) from exc

    data = resp.json()
    token = data.get("access_token")
    expires_in = data.get("expires_in", 3600)  # Default to 1 hour if not provided

    if not token:
        raise HTTPException(
            status_code=503,
            detail="Auth0 returned no access_token in management grant.",
        )

    # Update cache
    _MGMT_TOKEN_CACHE["access_token"] = token
    _MGMT_TOKEN_CACHE["expires_at"] = now + expires_in

    return token


def _get_github_token_from_identity(user_sub: str) -> str | None:
    """
    Fetch the GitHub access token from the user's linked identity
    via the Auth0 Management API.

    When a user logs in with GitHub social connection, Auth0 stores
    the GitHub access token in the user's identity array. This method
    retrieves it without requiring Token Vault setup.
    """
    mgmt_token = _get_management_token()
    url = f"{_MGMT_API_BASE}/users/{user_sub}"
    headers = {"Authorization": f"Bearer {mgmt_token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to fetch user profile from Auth0: %s", exc)
        return None

    user_data = resp.json()
    identities = user_data.get("identities", [])

    for identity in identities:
        if identity.get("provider") == "github" and identity.get("access_token"):
            return identity["access_token"]

    return None


def request_scoped_token(user_sub: str, scope: str) -> dict:
    """
    Request a GitHub access token for the given user.

    Strategy:
      1. Try Auth0 Token Vault (tokensproxy) first.
      2. If Token Vault returns 404 (not configured), fall back to
         extracting the GitHub token from the user's linked identity.

    Parameters
    ----------
    user_sub : str
        Auth0 user identifier (``sub`` claim).
    scope : str
        OAuth scope(s) being requested (e.g. ``"read:repos"``).

    Returns
    -------
    dict
        One of:
        - ``{"status": "approved", "access_token": "..."}``
        - ``{"status": "approval_required", ...}``

    Raises
    ------
    HTTPException
        403 / 404 / 503 on various failures.
    """
    mgmt_token = _get_management_token()

    # ── Strategy 1: Try Token Vault first ─────────────────────
    connection_name = settings.auth0_token_vault_connection
    url = f"https://{settings.auth0_domain}/api/v2/tokensproxy/connections/{connection_name}/token"

    params = {"user_id": user_sub, "scope": scope}
    headers = {
        "Authorization": f"Bearer {mgmt_token}",
        "Content-Type": "application/json",
    }

    try:
        logger.info("Requesting scoped token for %s (scope: %s)", user_sub, scope)
        resp = requests.get(url, headers=headers, params=params, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            return {"status": "approved", "access_token": data["access_token"]}

        if resp.status_code == 202:
            data = resp.json()
            return {
                "status": "approval_required",
                "approval_reference": data.get("approval_reference"),
                "message": data.get("message", "Human approval or step-up authentication is required."),
            }

        if resp.status_code == 403:
            logger.warning("Token Vault 403 for user %s", user_sub)
            raise HTTPException(
                status_code=403,
                detail=f"Action forbidden: user has not authorized the '{scope}' scope.",
            )

        # ── Token Vault not configured — fall back to identity ──
        if resp.status_code == 404:
            logger.info("Token Vault 404 — falling back to user identity for %s", user_sub)
            gh_token = _get_github_token_from_identity(user_sub)
            if gh_token:
                return {"status": "approved", "access_token": gh_token}

            raise HTTPException(
                status_code=404,
                detail=(
                    "GitHub token not found. Please log in with GitHub "
                    "to link your account."
                ),
            )

        logger.error("Unexpected Token Vault error %d: %s", resp.status_code, resp.text)
        raise HTTPException(
            status_code=503,
            detail=f"Auth0 Token Vault returned unexpected status: {resp.status_code}",
        )

    except requests.RequestException as exc:
        # Network error — try identity fallback before giving up
        logger.warning("Token Vault network error, trying identity fallback: %s", exc)
        gh_token = _get_github_token_from_identity(user_sub)
        if gh_token:
            return {"status": "approved", "access_token": gh_token}

        raise HTTPException(
            status_code=503,
            detail=f"Failed to retrieve GitHub token: {exc}",
        ) from exc
