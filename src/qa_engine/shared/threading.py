"""
Threading and resource management module.

Provides thread-safe resource locking and management as per FR-201.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, Optional, Set


class LockError(Exception):
    """Raised when lock acquisition fails."""


class ResourceManager:
    """
    Thread-safe singleton for resource locking.

    Implements mutex-style locks for coordinating access to shared
    resources (files, skills, etc.) as per FR-201.
    """

    _instance: Optional[ResourceManager] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> ResourceManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._locks: Dict[str, threading.Lock] = {}
        self._owners: Dict[str, str] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._manager_lock = threading.Lock()
        self._initialized = True

    def acquire(
        self,
        resource: str,
        agent_id: str,
        timeout: float = 60.0,
    ) -> bool:
        """
        Acquire exclusive lock on resource.

        Args:
            resource: Resource identifier
            agent_id: Agent requesting the lock
            timeout: Maximum wait time in seconds

        Returns:
            True if lock acquired, False if timeout
        """
        with self._manager_lock:
            if resource not in self._locks:
                self._locks[resource] = threading.Lock()

        lock = self._locks[resource]
        acquired = lock.acquire(timeout=timeout)

        if acquired:
            with self._manager_lock:
                self._owners[resource] = agent_id
                self._timestamps[resource] = datetime.now()

        return acquired

    def release(self, resource: str, agent_id: str) -> None:
        """
        Release lock on resource.

        Args:
            resource: Resource identifier
            agent_id: Agent releasing the lock

        Raises:
            LockError: If agent doesn't own the lock
        """
        with self._manager_lock:
            if resource not in self._owners:
                raise LockError(f"Resource not locked: {resource}")
            if self._owners[resource] != agent_id:
                raise LockError(
                    f"Agent {agent_id} doesn't own lock on {resource}"
                )

            del self._owners[resource]
            del self._timestamps[resource]

        self._locks[resource].release()

    def is_locked(self, resource: str) -> bool:
        """Check if resource is currently locked."""
        with self._manager_lock:
            return resource in self._owners

    def get_owner(self, resource: str) -> Optional[str]:
        """Get agent ID that owns the lock on resource."""
        with self._manager_lock:
            return self._owners.get(resource)

    def get_stale_locks(self, timeout_seconds: int = 120) -> Set[str]:
        """Get resources with locks older than or equal to timeout."""
        threshold = datetime.now() - timedelta(seconds=timeout_seconds)
        with self._manager_lock:
            return {
                r
                for r, t in self._timestamps.items()
                if t <= threshold
            }

    @contextmanager
    def locked(
        self,
        resource: str,
        agent_id: str,
        timeout: float = 60.0,
    ) -> Generator[None, None, None]:
        """Context manager for acquiring and releasing locks."""
        if not self.acquire(resource, agent_id, timeout):
            raise LockError(
                f"Timeout acquiring lock on {resource} for {agent_id}"
            )
        try:
            yield
        finally:
            self.release(resource, agent_id)

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
