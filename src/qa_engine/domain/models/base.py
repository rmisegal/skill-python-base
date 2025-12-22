"""
Base entity class for all manageable QA entities.

Provides common attributes and methods for Skills, Tools, and Resources.
All data is loaded from files - no hardcoded values.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class BaseEntity(ABC):
    """
    Abstract base class for all manageable entities.

    Attributes:
        id: Unique identifier (e.g., 'qa-bidi-detect')
        name: Human-readable name
        description: Brief description of the entity
        version: Semantic version string (e.g., '1.0.0')
        enabled: Whether the entity is active
        metadata: Additional key-value metadata
        path: File system path to the entity
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: str
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    path: Optional[Path] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize timestamps if not provided."""
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entity to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "path": str(self.path) if self.path else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEntity":
        """Create entity from dictionary. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement from_dict")

    @abstractmethod
    def validate(self) -> List[str]:
        """
        Validate entity configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        pass

    def _base_validate(self) -> List[str]:
        """Common validation for all entities."""
        errors = []
        if not self.id:
            errors.append("ID is required")
        if not self.name:
            errors.append("Name is required")
        if not self.description:
            errors.append("Description is required")
        if not self._is_valid_version(self.version):
            errors.append(f"Invalid version format: {self.version}")
        return errors

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version follows semantic versioning."""
        import re
        pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$"
        return bool(re.match(pattern, version))

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    def enable(self) -> None:
        """Enable the entity."""
        self.enabled = True
        self.touch()

    def disable(self) -> None:
        """Disable the entity."""
        self.enabled = False
        self.touch()
