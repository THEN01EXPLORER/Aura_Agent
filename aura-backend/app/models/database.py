"""
Aura — SQLAlchemy models and database engine bootstrap.

Defines:
  • audit_logs table (append-only, immutable)
  • engine / SessionLocal / Base
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # required for SQLite
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ─── Audit Log Table ─────────────────────────────────────


class AuditLog(Base):  # type: ignore[misc]
    """
    Immutable, append-only audit trail.
    NO UPDATE / DELETE operations are permitted.
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(
        String,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )
    event_type = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_repo = Column(String, nullable=True)
    decision = Column(String, nullable=False)
    actor = Column(String, nullable=False, default="system")
    metadata_json = Column(Text, nullable=True)


# ─── Immutability Guard ──────────────────────────────────
# Reject UPDATE and DELETE at the ORM event level.


def _block_update(mapper: object, connection: object, target: AuditLog) -> None:
    raise RuntimeError(
        "AuditLog records are immutable. UPDATE is not permitted."
    )


def _block_delete(mapper: object, connection: object, target: AuditLog) -> None:
    raise RuntimeError(
        "AuditLog records are immutable. DELETE is not permitted."
    )


event.listen(AuditLog, "before_update", _block_update)
event.listen(AuditLog, "before_delete", _block_delete)


# ─── Helpers ─────────────────────────────────────────────


def create_tables() -> None:
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
