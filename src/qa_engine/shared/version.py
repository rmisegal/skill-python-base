"""
Version management module.

Provides singleton VersionManager for tracking and comparing versions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from threading import Lock
from typing import Optional, Tuple


@dataclass(frozen=True)
class SemanticVersion:
    """Immutable semantic version representation."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version_str: str) -> SemanticVersion:
        """Parse version string like '1.2.3' into SemanticVersion."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str.strip())
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: SemanticVersion) -> bool:
        return self.as_tuple() < other.as_tuple()

    def __le__(self, other: SemanticVersion) -> bool:
        return self.as_tuple() <= other.as_tuple()

    def __gt__(self, other: SemanticVersion) -> bool:
        return self.as_tuple() > other.as_tuple()

    def __ge__(self, other: SemanticVersion) -> bool:
        return self.as_tuple() >= other.as_tuple()

    def as_tuple(self) -> Tuple[int, int, int]:
        """Return version as comparable tuple."""
        return (self.major, self.minor, self.patch)


class VersionManager:
    """
    Thread-safe singleton for version management.

    Tracks application version and provides comparison utilities.
    """

    _instance: Optional[VersionManager] = None
    _lock: Lock = Lock()

    def __new__(cls) -> VersionManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._version = SemanticVersion(1, 0, 0)
        self._initialized = True

    @property
    def version(self) -> SemanticVersion:
        """Get current version."""
        return self._version

    @property
    def version_string(self) -> str:
        """Get version as string."""
        return str(self._version)

    def set_version(self, version_str: str) -> None:
        """Set version from string."""
        self._version = SemanticVersion.parse(version_str)

    def is_compatible(self, min_version: str) -> bool:
        """Check if current version meets minimum requirement."""
        required = SemanticVersion.parse(min_version)
        return self._version >= required

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
