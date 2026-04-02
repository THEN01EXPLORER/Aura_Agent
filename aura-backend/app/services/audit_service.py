"""
Aura — Audit Service.

Provides append-only logging to the audit_logs table and read-only
query access.  No audit record may ever be updated or deleted.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.database import AuditLog
from app.models.schemas import AuditEntry

logger = logging.getLogger(__name__)


def log_event(
    db: Session,
    event_type: str,
    action: str,
    target_repo: Optional[str],
    decision: str,
    actor: str = "system",
    metadata: Optional[dict[str, Any]] = None,
) -> AuditLog:
    """
    Insert a single immutable audit event into the database.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy session.
    event_type : str
        One of the EventType enum values.
    action : str
        The action being audited (e.g. ``"read_repos"``).
    target_repo : str | None
        Repository targeted by the action, if any.
    decision : str
        Policy decision or outcome (e.g. ``"allow"``, ``"blocked"``).
    actor : str
        Identity of the actor (default ``"system"``).
    metadata : dict | None
        Arbitrary JSON-serializable metadata to attach.

    Returns
    -------
    AuditLog
        The newly created audit record (with ``id`` populated).
    """
    metadata_json: Optional[str] = None
    if metadata is not None:
        try:
            metadata_json = json.dumps(metadata, default=str)
        except (TypeError, ValueError) as exc:
            logger.warning("Failed to serialize audit metadata: %s", exc)
            metadata_json = json.dumps({"_serialization_error": str(exc)})

    record = AuditLog(
        event_type=event_type,
        action=action,
        target_repo=target_repo,
        decision=decision,
        actor=actor,
        metadata_json=metadata_json,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info(
        "Audit [%s] action=%s target=%s decision=%s actor=%s",
        event_type,
        action,
        target_repo,
        decision,
        actor,
    )

    return record


def get_audit_logs(
    db: Session,
    actor: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditEntry]:
    """
    Retrieve audit log entries ordered by most recent first.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy session.
    limit : int
        Maximum number of entries to return.
    offset : int
        Number of entries to skip (for pagination).

    Returns
    -------
    list[AuditEntry]
        List of audit entries as Pydantic models.
    """
    query = db.query(AuditLog)
    if actor:
        query = query.filter(AuditLog.actor == actor)

    rows = (
        query.order_by(AuditLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        AuditEntry(
            id=row.id,
            timestamp=row.timestamp,
            event_type=row.event_type,
            action=row.action,
            target_repo=row.target_repo,
            decision=row.decision,
            actor=row.actor,
            metadata_json=row.metadata_json,
        )
        for row in rows
    ]
