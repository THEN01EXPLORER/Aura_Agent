"""
Aura — GitHub Execution Service.

Provides thin, typed wrappers around the GitHub REST API for the
three supported actions:
  • read_repos  — GET /user/repos
  • archive_repo — PATCH /repos/{owner}/{repo}  (archived=true)
  • delete_repo  — DELETE /repos/{owner}/{repo}

All calls use Bearer-token auth and structured error handling.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from fastapi import HTTPException

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_GITHUB_API = settings.github_api_base


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _parse_repo(repo_full_name: str) -> tuple[str, str]:
    """Split ``owner/repo`` into (owner, repo); raise on bad format."""
    parts = repo_full_name.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid repo format '{repo_full_name}'. "
                f"Expected 'owner/repo'."
            ),
        )
    return parts[0], parts[1]


# ─── Public API ───────────────────────────────────────────


def read_repos(token: str) -> list[dict[str, Any]]:
    """
    Fetch the authenticated user's repositories.

    Returns a list of repo summary dicts (name, full_name, private,
    html_url, description).
    """
    url = f"{_GITHUB_API}/user/repos"
    params = {"per_page": 100, "sort": "updated"}

    try:
        resp = requests.get(url, headers=_headers(token), params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("GitHub read_repos failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error while listing repos: {exc}",
        ) from exc

    repos_raw: list[dict[str, Any]] = resp.json()
    return [
        {
            "name": r.get("name"),
            "full_name": r.get("full_name"),
            "private": r.get("private"),
            "html_url": r.get("html_url"),
            "description": r.get("description"),
            "archived": r.get("archived"),
        }
        for r in repos_raw
    ]


def archive_repo(token: str, repo_full_name: str) -> dict[str, Any]:
    """
    Archive a repository by setting ``archived = true``.

    Returns a summary dict of the updated repo.
    """
    owner, repo = _parse_repo(repo_full_name)
    url = f"{_GITHUB_API}/repos/{owner}/{repo}"

    try:
        resp = requests.patch(
            url,
            headers=_headers(token),
            json={"archived": True},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("GitHub archive_repo failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error while archiving repo: {exc}",
        ) from exc

    data = resp.json()
    return {
        "full_name": data.get("full_name"),
        "archived": data.get("archived"),
        "html_url": data.get("html_url"),
    }


def delete_repo(token: str, repo_full_name: str) -> dict[str, Any]:
    """
    Permanently delete a repository.

    Returns a confirmation dict.
    """
    owner, repo = _parse_repo(repo_full_name)
    url = f"{_GITHUB_API}/repos/{owner}/{repo}"

    try:
        resp = requests.delete(url, headers=_headers(token), timeout=15)
        # 204 No Content = success for DELETE
        if resp.status_code == 204:
            return {
                "full_name": repo_full_name,
                "deleted": True,
                "message": f"Repository '{repo_full_name}' deleted successfully.",
            }
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("GitHub delete_repo failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error while deleting repo: {exc}",
        ) from exc

    # Should not reach here, but handle defensively
    return {
        "full_name": repo_full_name,
        "deleted": False,
        "message": f"Unexpected status {resp.status_code}.",
    }
def create_repo(token: str, name: str, private: bool = False) -> dict[str, Any]:
    """
    Create a new repository for the authenticated user.

    Returns a summary dict of the created repo.
    """
    url = f"{_GITHUB_API}/user/repos"
    payload = {
        "name": name,
        "private": private,
        "auto_init": True,
    }

    try:
        resp = requests.post(
            url,
            headers=_headers(token),
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("GitHub create_repo failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error while creating repo: {exc}",
        ) from exc

    data = resp.json()
    return {
        "full_name": data.get("full_name"),
        "visibility": "private" if data.get("private") else "public",
        "html_url": data.get("html_url"),
        "created_at": data.get("created_at"),
        "node_id": data.get("node_id"),
    }
