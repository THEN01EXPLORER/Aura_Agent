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


def request_scoped_token(user_sub: str, scope: str) -> dict:
    """
    Request a GitHub access token for the given user using Auth0 Token Vault.

    This uses the Tokensproxy API to retrieve a scoped, short-lived token.
    If the action requires human approval or step-up authentication, the
    API returns 202 (Accepted) with an approval_reference.

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
        - ``{"status": "approval_required", "approval_reference": "...",
             "message": "..."}``

    Raises
    ------
    HTTPException
        403 if the user hasn't authorized the connection or the scope.
        503 on Auth0 communication failure.
    """
    mgmt_token = _get_management_token()
    
    # Token Vault Connection Proxy endpoint
    connection_name = settings.auth0_token_vault_connection
    url = f"https://{settings.auth0_domain}/api/v2/tokensproxy/connections/{connection_name}/token"
    
    params = {
        "user_id": user_sub,
        "scope": scope
    }
    
    headers = {
        "Authorization": f"Bearer {mgmt_token}",
        "Content-Type": "application/json"
    }

    try:
        logger.info("Requesting scoped token for %s from Token Vault (scope: %s)", user_sub, scope)
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        
        # ── 1. Success — Token received directly ────────────────
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "approved",
                "access_token": data["access_token"]
            }

        # ── 2. Approval Required — Step-up or consent needed ──
        if resp.status_code == 202:
            data = resp.json()
            return {
                "status": "approval_required",
                "approval_reference": data.get("approval_reference"),
                "message": data.get("message", "Human approval or step-up authentication is required.")
            }

        # ── 3. Forbidden — Missing delegation or restricted scope ─
        if resp.status_code == 403:
            logger.warning("Auth0 Token Vault returned 403 Forbidden for user %s", user_sub)
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Action forbidden: The user has not authorized the '{scope}' scope, "
                    "or the application is not authorized to act on behalf of the user."
                )
            )

        # ── 4. Not Found — Connection or User doesn't exist ─────
        if resp.status_code == 404:
            logger.warning("Auth0 Token Vault or user not found: %s", user_sub)
            raise HTTPException(
                status_code=404,
                detail=f"Token Vault connection '{connection_name}' or user not found."
            )

        # ── 5. Unexpected errors ────────────────────────────────
        logger.error("Unexpected Token Vault error %d: %s", resp.status_code, resp.text)
        raise HTTPException(
            status_code=503,
            detail=f"Auth0 Token Vault returned an unexpected status code: {resp.status_code}"
        )

    except requests.RequestException as exc:
        logger.error("Auth0 Token Vault communication failure: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Failed to communicate with Auth0 Token Vault: {exc}"
        )
