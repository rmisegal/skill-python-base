"""
Base manager providing CRUD operations for all entities.

Abstract base class that defines the interface for all managers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar

from ..domain.models.base import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseManager(ABC, Generic[T]):
    """Abstract base manager with CRUD operations."""

    def __init__(self, storage_path: Path):
        """Initialize manager with storage path."""
        self._storage_path = storage_path
        self._cache: Dict[str, T] = {}
        self._loaded = False

    @property
    def storage_path(self) -> Path:
        """Get storage path."""
        return self._storage_path

    # CRUD Operations

    def create(self, entity: T) -> T:
        """Create a new entity."""
        if entity.id in self._cache:
            raise ValueError(f"Entity already exists: {entity.id}")
        errors = entity.validate()
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        self._cache[entity.id] = entity
        self._persist(entity)
        return entity

    def read(self, entity_id: str) -> Optional[T]:
        """Read an entity by ID."""
        self._ensure_loaded()
        return self._cache.get(entity_id)

    def update(self, entity_id: str, updates: Dict[str, Any]) -> T:
        """Update an entity with given values."""
        entity = self.read(entity_id)
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")

        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.touch()
        errors = entity.validate()
        if errors:
            raise ValueError(f"Validation errors: {errors}")

        self._persist(entity)
        return entity

    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID."""
        entity = self.read(entity_id)
        if not entity:
            return False
        del self._cache[entity_id]
        self._remove_persisted(entity)
        return True

    # Bulk Operations

    def list_all(self) -> List[T]:
        """List all entities."""
        self._ensure_loaded()
        return list(self._cache.values())

    def find(self, **criteria: Any) -> List[T]:
        """Find entities matching criteria."""
        self._ensure_loaded()
        results: List[T] = []
        for entity in self._cache.values():
            if self._matches_criteria(entity, criteria):
                results.append(entity)
        return results

    def _matches_criteria(self, entity: T, criteria: Dict[str, Any]) -> bool:
        """Check if entity matches all criteria."""
        for key, value in criteria.items():
            entity_value = getattr(entity, key, None)
            if entity_value != value:
                return False
        return True

    # State Management

    def enable(self, entity_id: str) -> bool:
        """Enable an entity."""
        entity = self.read(entity_id)
        if not entity:
            return False
        entity.enable()
        self._persist(entity)
        return True

    def disable(self, entity_id: str) -> bool:
        """Disable an entity."""
        entity = self.read(entity_id)
        if not entity:
            return False
        entity.disable()
        self._persist(entity)
        return True

    def duplicate(self, entity_id: str, new_id: str) -> T:
        """Duplicate an entity with a new ID."""
        entity = self.read(entity_id)
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")
        if new_id in self._cache:
            raise ValueError(f"Entity already exists: {new_id}")

        data = entity.to_dict()
        data["id"] = new_id
        data["name"] = new_id
        new_entity = self._from_dict(data)
        return self.create(new_entity)

    # Persistence

    def load_all(self) -> None:
        """Load all entities from storage."""
        self._cache.clear()
        for entity in self._load_from_storage():
            self._cache[entity.id] = entity
        self._loaded = True

    def save_all(self) -> None:
        """Save all entities to storage."""
        for entity in self._cache.values():
            self._persist(entity)

    def refresh(self, entity_id: str) -> Optional[T]:
        """Reload entity from storage."""
        entity = self._load_single(entity_id)
        if entity:
            self._cache[entity_id] = entity
        return entity

    def _ensure_loaded(self) -> None:
        """Ensure entities are loaded."""
        if not self._loaded:
            self.load_all()

    # Abstract methods for subclasses

    @abstractmethod
    def _load_from_storage(self) -> List[T]:
        """Load all entities from storage."""
        pass

    @abstractmethod
    def _load_single(self, entity_id: str) -> Optional[T]:
        """Load a single entity from storage."""
        pass

    @abstractmethod
    def _persist(self, entity: T) -> None:
        """Persist entity to storage."""
        pass

    @abstractmethod
    def _remove_persisted(self, entity: T) -> None:
        """Remove entity from storage."""
        pass

    @abstractmethod
    def _from_dict(self, data: Dict[str, Any]) -> T:
        """Create entity from dictionary."""
        pass
