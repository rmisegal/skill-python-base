"""
Resource manager for managing configuration and template resources.

Provides CRUD operations and content management for resources.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.models import (
    Resource,
    ResourceType,
    FileFormat,
    ConfigResource,
    RulesResource,
    PatternsResource,
)
from ..parsers.config_parser import ConfigParser
from ..serializers.config_serializer import ConfigSerializer
from .base_manager import BaseManager


class ResourceManager(BaseManager[Resource]):
    """Manages configuration and template resources."""

    def __init__(self, storage_path: Path):
        """Initialize resource manager."""
        super().__init__(storage_path)
        self._parser = ConfigParser()
        self._serializer = ConfigSerializer()

    # Content Operations

    def get_content(self, resource_id: str) -> Any:
        """Get resource content."""
        resource = self.read(resource_id)
        return resource.content if resource else None

    def set_content(self, resource_id: str, content: Any) -> None:
        """Set resource content."""
        self.update(resource_id, {"content": content})

    def merge_content(self, resource_id: str, partial: Dict[str, Any]) -> None:
        """Merge partial content into resource."""
        resource = self.read(resource_id)
        if not resource:
            raise ValueError(f"Resource not found: {resource_id}")
        if not isinstance(resource.content, dict):
            raise ValueError("Cannot merge into non-dict content")

        merged = self._parser.merge_configs(resource.content, partial)
        self.update(resource_id, {"content": merged})

    # Schema Validation

    def validate_content(self, resource_id: str) -> List[str]:
        """Validate resource content against schema."""
        resource = self.read(resource_id)
        if not resource:
            return [f"Resource not found: {resource_id}"]

        if isinstance(resource, ConfigResource) and resource.schema:
            return self._parser.validate_schema(resource.content, resource.schema)
        return []

    def get_schema(self, resource_id: str) -> Dict[str, Any]:
        """Get resource schema."""
        resource = self.read(resource_id)
        if isinstance(resource, ConfigResource):
            return resource.schema
        return {}

    # Resource Queries

    def get_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """Get all resources of a specific type."""
        return self.find(resource_type=resource_type)

    def get_configs(self) -> List[ConfigResource]:
        """Get all configuration resources."""
        return [r for r in self.list_all() if isinstance(r, ConfigResource)]

    def get_rules_resources(self) -> List[RulesResource]:
        """Get all rules resources."""
        return [r for r in self.list_all() if isinstance(r, RulesResource)]

    def get_patterns_resources(self) -> List[PatternsResource]:
        """Get all patterns resources."""
        return [r for r in self.list_all() if isinstance(r, PatternsResource)]

    # Implementation of abstract methods

    def _load_from_storage(self) -> List[Resource]:
        """Load all resources from storage."""
        resources: List[Resource] = []
        if not self._storage_path.exists():
            return resources

        for file_path in self._storage_path.glob("**/*.json"):
            resource = self._load_resource_file(file_path)
            if resource:
                resources.append(resource)

        for file_path in self._storage_path.glob("**/*.yaml"):
            resource = self._load_resource_file(file_path)
            if resource:
                resources.append(resource)

        return resources

    def _load_resource_file(self, file_path: Path) -> Optional[Resource]:
        """Load a single resource file."""
        content = self._parser.parse(file_path)
        resource_type = self._determine_resource_type(file_path, content)
        return self._create_resource(file_path, content, resource_type)

    def _determine_resource_type(
        self, file_path: Path, content: Dict[str, Any]
    ) -> ResourceType:
        """Determine resource type from path or content."""
        name = file_path.stem.lower()
        if "rules" in name:
            return ResourceType.RULES
        if "patterns" in name:
            return ResourceType.PATTERNS
        if "template" in name:
            return ResourceType.TEMPLATE
        return ResourceType.CONFIG

    def _create_resource(
        self, path: Path, content: Any, resource_type: ResourceType
    ) -> Resource:
        """Create appropriate Resource subclass."""
        file_format = FileFormat.JSON if path.suffix == ".json" else FileFormat.YAML
        base = {
            "id": path.stem,
            "name": path.stem,
            "description": "",
            "path": path,
            "resource_type": resource_type,
            "file_format": file_format,
            "content": content,
        }

        if resource_type == ResourceType.RULES:
            return RulesResource(**base)
        elif resource_type == ResourceType.PATTERNS:
            return PatternsResource(**base)
        elif resource_type == ResourceType.CONFIG:
            return ConfigResource(**base)
        return Resource(**base)

    def _load_single(self, entity_id: str) -> Optional[Resource]:
        """Load a single resource from storage."""
        for ext in (".json", ".yaml"):
            file_path = self._storage_path / f"{entity_id}{ext}"
            if file_path.exists():
                return self._load_resource_file(file_path)
        return None

    def _persist(self, entity: Resource) -> None:
        """Persist resource to storage."""
        ext = ".json" if entity.file_format == FileFormat.JSON else ".yaml"
        file_path = self._storage_path / f"{entity.id}{ext}"
        self._serializer.write(entity.content, file_path)

    def _remove_persisted(self, entity: Resource) -> None:
        """Remove resource file from storage."""
        if entity.path and entity.path.exists():
            entity.path.unlink()

    def _from_dict(self, data: Dict[str, Any]) -> Resource:
        """Create resource from dictionary."""
        return Resource.from_dict(data)
