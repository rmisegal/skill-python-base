"""Resource class hierarchy for QA system."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseEntity
from .definitions import PatternDefinition, RuleDefinition


class ResourceType(Enum):
    """Types of resources."""
    CONFIG = "config"        # JSON/YAML configuration
    TEMPLATE = "template"    # Markdown/LaTeX templates
    RULES = "rules"          # Rule definition files
    PATTERNS = "patterns"    # Pattern definition files


class FileFormat(Enum):
    """Supported file formats."""

    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "md"
    PYTHON = "py"
    LATEX = "tex"


@dataclass
class Resource(BaseEntity):
    """
    Base resource class.

    Attributes:
        resource_type: Type of resource
        file_format: Format of the resource file
        content: Parsed content of the resource
        schema_path: Path to JSON schema for validation
    """

    resource_type: ResourceType = ResourceType.CONFIG
    file_format: FileFormat = FileFormat.JSON
    content: Any = None
    schema_path: Optional[Path] = None

    def validate(self) -> List[str]:
        """Validate resource configuration."""
        errors = self._base_validate()
        if self.content is None:
            errors.append("Resource content is required")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "resource_type": self.resource_type.value,
            "file_format": self.file_format.value,
            "content": self.content,
            "schema_path": str(self.schema_path) if self.schema_path else None,
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resource":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {}),
            path=Path(data["path"]) if data.get("path") else None,
            resource_type=ResourceType(data.get("resource_type", "config")),
            file_format=FileFormat(data.get("file_format", "json")),
            content=data.get("content"),
            schema_path=Path(data["schema_path"]) if data.get("schema_path") else None,
        )


@dataclass
class ConfigResource(Resource):
    """
    Configuration resource (JSON/YAML).

    Attributes:
        schema: JSON schema for validation
        defaults: Default values
    """

    schema: Dict[str, Any] = field(default_factory=dict)
    defaults: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.resource_type = ResourceType.CONFIG

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key."""
        if not self.content:
            return default
        keys = key.split(".")
        value = self.content
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


@dataclass
class RulesResource(Resource):
    """
    Detection rules resource.

    Attributes:
        rules: Dictionary of rule definitions
    """

    rules: Dict[str, RuleDefinition] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.resource_type = ResourceType.RULES
        self.file_format = FileFormat.PYTHON

    def get_rule(self, rule_id: str) -> Optional[RuleDefinition]:
        """Get rule by ID."""
        return self.rules.get(rule_id)

    def add_rule(self, rule: RuleDefinition) -> None:
        """Add a rule definition."""
        self.rules[rule.id] = rule
        self.touch()

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.touch()
            return True
        return False


@dataclass
class PatternsResource(Resource):
    """
    Fix patterns resource.

    Attributes:
        patterns: Dictionary of pattern definitions
    """

    patterns: Dict[str, PatternDefinition] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.resource_type = ResourceType.PATTERNS
        self.file_format = FileFormat.PYTHON

    def get_pattern(self, pattern_id: str) -> Optional[PatternDefinition]:
        """Get pattern by ID."""
        return self.patterns.get(pattern_id)

    def add_pattern(self, pattern: PatternDefinition) -> None:
        """Add a pattern definition."""
        self.patterns[pattern.id] = pattern
        self.touch()

    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern by ID."""
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            self.touch()
            return True
        return False
