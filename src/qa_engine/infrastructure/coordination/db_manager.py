"""
Database manager for coordination SQLite operations.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Generator


class DBManager:
    """Manages SQLite database connections and schema."""

    SCHEMA = """
        CREATE TABLE IF NOT EXISTS qa_locks (
            resource TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            acquired_at TEXT NOT NULL,
            expires_at TEXT
        );
        CREATE TABLE IF NOT EXISTS qa_status (
            skill_name TEXT PRIMARY KEY,
            state TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            issues_found INTEGER DEFAULT 0,
            agent_id TEXT,
            error_message TEXT
        );
        CREATE TABLE IF NOT EXISTS qa_heartbeat (
            agent_id TEXT PRIMARY KEY,
            last_seen TEXT NOT NULL,
            current_task TEXT
        );
    """

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._lock = Lock()
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self.connection() as conn:
            conn.executescript(self.SCHEMA)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get thread-safe database connection."""
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()

    def cleanup(self) -> None:
        """Remove database file."""
        if self._db_path.exists():
            self._db_path.unlink()
