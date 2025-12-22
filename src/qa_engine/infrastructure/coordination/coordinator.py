"""
Coordinator for multi-agent resource management.

Implements FR-201 (Resource Locking), FR-203 (Shared Status Database).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .db_manager import DBManager


class CoordinatorError(Exception):
    """Raised when coordination operation fails."""


class Coordinator:
    """Coordinates multi-agent access to shared resources using SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        self._db = DBManager(db_path)

    def acquire_resource(self, resource: str, agent_id: str, timeout: int = 60) -> bool:
        """Acquire exclusive lock on resource. Returns True if acquired."""
        now = datetime.now()
        expires_at = now + timedelta(seconds=timeout)

        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT agent_id, expires_at FROM qa_locks WHERE resource = ?",
                (resource,),
            ).fetchone()

            if row:
                existing_expires = datetime.fromisoformat(row["expires_at"])
                if existing_expires > now:
                    return False
                conn.execute("DELETE FROM qa_locks WHERE resource = ?", (resource,))

            conn.execute(
                "INSERT INTO qa_locks (resource, agent_id, acquired_at, expires_at) VALUES (?, ?, ?, ?)",
                (resource, agent_id, now.isoformat(), expires_at.isoformat()),
            )
            return True

    def release_resource(self, resource: str, agent_id: str) -> None:
        """Release lock on resource."""
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT agent_id FROM qa_locks WHERE resource = ?", (resource,),
            ).fetchone()

            if not row:
                raise CoordinatorError(f"Resource not locked: {resource}")
            if row["agent_id"] != agent_id:
                raise CoordinatorError(f"Agent {agent_id} doesn't own lock on {resource}")

            conn.execute("DELETE FROM qa_locks WHERE resource = ?", (resource,))

    def get_resource_owner(self, resource: str) -> Optional[str]:
        """Get agent ID that owns lock on resource."""
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT agent_id, expires_at FROM qa_locks WHERE resource = ?",
                (resource,),
            ).fetchone()

            if row and datetime.fromisoformat(row["expires_at"]) > datetime.now():
                return row["agent_id"]
            return None

    def update_status(
        self, skill_name: str, state: str, agent_id: str,
        issues_found: int = 0, error_message: Optional[str] = None,
    ) -> None:
        """Update skill execution status."""
        now = datetime.now().isoformat()
        completed = now if state in ("completed", "failed") else None

        with self._db.connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO qa_status
                   (skill_name, state, started_at, completed_at, issues_found, agent_id, error_message)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (skill_name, state, now, completed, issues_found, agent_id, error_message),
            )

    def get_status(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get status for a skill."""
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM qa_status WHERE skill_name = ?", (skill_name,),
            ).fetchone()
            return dict(row) if row else None

    def get_all_status(self) -> List[Dict[str, Any]]:
        """Get all skill statuses."""
        with self._db.connection() as conn:
            rows = conn.execute("SELECT * FROM qa_status").fetchall()
            return [dict(row) for row in rows]

    def cleanup(self) -> None:
        """Remove database file."""
        self._db.cleanup()
