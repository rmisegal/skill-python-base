"""
Tool class hierarchy for QA system.

Defines Python tool implementations:
- DetectorTool: Detection tools with rules
- FixerTool: Fixer tools with patterns
- UtilityTool: General utility tools
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseEntity
from .definitions import PatternDefinition, RuleDefinition


class ToolType(Enum):
    """Types of Python tools."""

    DETECTOR = "detector"
    FIXER = "fixer"
    UTILITY = "utility"


@dataclass
class Tool(BaseEntity):
    """
    Base tool class for Python implementations.

    Attributes:
        tool_type: Type of tool (detector, fixer, utility)
        module_path: Python module path
        entry_function: Main function name to call
        input_schema: JSON schema for input
        output_schema: JSON schema for output
        imports: Required import statements
        requires: List of other tool IDs this depends on
    """

    tool_type: ToolType = ToolType.UTILITY
    module_path: str = ""
    entry_function: str = "run"
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """Validate tool configuration."""
        errors = self._base_validate()
        if not self.module_path:
            errors.append("Module path is required")
        if not self.entry_function:
            errors.append("Entry function is required")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "tool_type": self.tool_type.value,
            "module_path": self.module_path,
            "entry_function": self.entry_function,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "imports": self.imports,
            "requires": self.requires,
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tool":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {}),
            path=Path(data["path"]) if data.get("path") else None,
            tool_type=ToolType(data.get("tool_type", "utility")),
            module_path=data.get("module_path", ""),
            entry_function=data.get("entry_function", "run"),
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            imports=data.get("imports", []),
            requires=data.get("requires", []),
        )


@dataclass
class DetectorTool(Tool):
    """
    Detection tool implementation.

    Attributes:
        rules: Dictionary of rule definitions
        detector_class: Name of detector class in module
    """

    rules: Dict[str, RuleDefinition] = field(default_factory=dict)
    detector_class: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.tool_type = ToolType.DETECTOR
        self.entry_function = "run_detection"

    def get_rules(self) -> Dict[str, str]:
        """Return rule ID to description mapping."""
        return {rule_id: rule.description for rule_id, rule in self.rules.items()}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base["rules"] = {k: v.to_dict() for k, v in self.rules.items()}
        base["detector_class"] = self.detector_class
        return base


@dataclass
class FixerTool(Tool):
    """
    Fixer tool implementation.

    Attributes:
        patterns: Dictionary of pattern definitions
        fixer_class: Name of fixer class in module
    """

    patterns: Dict[str, PatternDefinition] = field(default_factory=dict)
    fixer_class: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.tool_type = ToolType.FIXER
        self.entry_function = "fix"

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return pattern configurations."""
        return {
            pat_id: {"find": pat.find, "replace": pat.replace, "desc": pat.description}
            for pat_id, pat in self.patterns.items()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base["patterns"] = {k: v.to_dict() for k, v in self.patterns.items()}
        base["fixer_class"] = self.fixer_class
        return base
