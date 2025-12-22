"""
Heartbeat monitoring for agent health tracking.

Implements FR-202 (Heartbeat Monitoring) and FR-303 (Watchdog Monitor).
"""

from __future__ import annotations

import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional


class HeartbeatMonitor:
    """
    Monitors agent health via heartbeat mechanism.

    Tracks agent heartbeats and detects stale agents
    as per FR-202 and FR-303 requirements.
    """

    def __init__(
        self,
        db_path: str | Path,
        stale_timeout: int = 120,
        check_interval: int = 30,
    ) -> None:
        """
        Initialize heartbeat monitor.

        Args:
            db_path: Path to SQLite database
            stale_timeout: Seconds without heartbeat to consider stale
            check_interval: Seconds between stale checks
        """
        self._db_path = Path(db_path)
        self._stale_timeout = stale_timeout
        self._check_interval = check_interval
        self._lock = threading.Lock()
        self._watchdog_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._on_stale_callback: Optional[Callable[[Dict], None]] = None

    def update_heartbeat(self, agent_id: str, current_task: str) -> None:
        """
        Update heartbeat for an agent.

        Args:
            agent_id: Agent identifier
            current_task: Current task description
        """
        now = datetime.now().isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO qa_heartbeat
                       (agent_id, last_seen, current_task)
                       VALUES (?, ?, ?)""",
                    (agent_id, now, current_task),
                )
                conn.commit()
            finally:
                conn.close()

    def check_stale_agents(self) -> List[Dict[str, str]]:
        """
        Check for stale agents.

        Returns:
            List of stale agent info dicts
        """
        threshold = datetime.now() - timedelta(seconds=self._stale_timeout)

        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute(
                    "SELECT agent_id, last_seen, current_task FROM qa_heartbeat"
                ).fetchall()

                stale = []
                for row in rows:
                    last_seen = datetime.fromisoformat(row["last_seen"])
                    if last_seen < threshold:
                        stale.append({
                            "agent_id": row["agent_id"],
                            "last_seen": row["last_seen"],
                            "current_task": row["current_task"],
                        })
                return stale
            finally:
                conn.close()

    def remove_agent(self, agent_id: str) -> None:
        """Remove agent from heartbeat tracking."""
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            try:
                conn.execute(
                    "DELETE FROM qa_heartbeat WHERE agent_id = ?",
                    (agent_id,),
                )
                conn.commit()
            finally:
                conn.close()

    def start_watchdog(
        self,
        on_stale: Optional[Callable[[Dict], None]] = None,
    ) -> None:
        """
        Start background watchdog thread.

        Args:
            on_stale: Callback for stale agent detection
        """
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            return

        self._on_stale_callback = on_stale
        self._stop_event.clear()
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
        )
        self._watchdog_thread.start()

    def stop_watchdog(self) -> None:
        """Stop watchdog thread."""
        self._stop_event.set()
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=5)

    def _watchdog_loop(self) -> None:
        """Background loop checking for stale agents."""
        while not self._stop_event.is_set():
            stale_agents = self.check_stale_agents()
            if stale_agents and self._on_stale_callback:
                for agent in stale_agents:
                    self._on_stale_callback(agent)
            time.sleep(self._check_interval)

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, str]]:
        """Get status of a specific agent."""
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute(
                    "SELECT * FROM qa_heartbeat WHERE agent_id = ?",
                    (agent_id,),
                ).fetchone()
                return dict(row) if row else None
            finally:
                conn.close()
