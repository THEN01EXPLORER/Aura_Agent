"""
Aura — Planner Service.

Sends a user prompt to the OpenAI Chat Completions API and returns
a validated structured intent conforming to PlannerOutput.

Uses raw OpenAI SDK only — no LangChain, no agent frameworks.
"""

from __future__ import annotations

import json
import logging

from fastapi import HTTPException
from openai import OpenAI, OpenAIError

from app.config import get_settings
from app.models.schemas import PlannerOutput

logger = logging.getLogger(__name__)

settings = get_settings()

_client = OpenAI(api_key=settings.openai_api_key)

_SYSTEM_PROMPT = """\
You are Aura's intent planner.  Your ONLY job is to classify a user's
natural-language instruction about GitHub repositories into EXACTLY one
of the following actions:

  • read_repos   — list the user's repositories
  • create_repo   — create a new repository
  • archive_repo — archive a specific repository
  • delete_repo  — permanently delete a specific repository

You MUST respond with a JSON object containing EXACTLY these fields
and NO others:

{
  "action":      one of "read_repos", "create_repo", "archive_repo", "delete_repo",
  "target_repo": "owner/repo" string or null (MUST be null for read_repos),
  "reason":      a short human-readable justification,
  "confidence":  a number between 0 and 1 indicating your certainty
}

Rules:
- If the user's request does not clearly map to one of the four actions,
  choose the closest match and set confidence below 0.5.
- Never invent additional fields.
- Never return markdown, commentary, or anything outside the JSON object.
- target_repo MUST be null when action is read_repos.
- For create_repo, target_repo MUST be the simple name of the new repository.
- For archive_repo or delete_repo, target_repo MUST be a non-empty string in
  "owner/repo" format. If the user only provides a repo name without an owner,
  use the placeholder owner "user" (e.g. "user/repo-name").
"""


def generate_intent(prompt: str) -> PlannerOutput:
    """
    Call the OpenAI Chat Completions API to classify a user prompt
    into a structured intent.

    Returns
    -------
    PlannerOutput
        Validated structured intent.

    Raises
    ------
    HTTPException
        • 502 if the OpenAI API call fails
        • 422 if the LLM returns JSON that fails validation
    """
    try:
        response = _client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
    except OpenAIError as exc:
        logger.error("OpenAI API call failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Planner LLM call failed: {exc}",
        ) from exc

    raw_content = response.choices[0].message.content
    if not raw_content:
        raise HTTPException(
            status_code=502,
            detail="Planner LLM returned an empty response.",
        )

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned invalid JSON: %s", raw_content)
        raise HTTPException(
            status_code=502,
            detail=f"Planner LLM returned invalid JSON: {exc}",
        ) from exc

    try:
        intent = PlannerOutput(**parsed)
    except Exception as exc:
        logger.error("LLM JSON failed schema validation: %s", exc)
        raise HTTPException(
            status_code=422,
            detail=f"Planner output failed validation: {exc}",
        ) from exc

    return intent
