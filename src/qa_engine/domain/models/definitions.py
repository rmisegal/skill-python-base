"""Rule and pattern definitions for detection and fixing."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class RuleDefinition:
    """
    Definition of a detection rule.

    Attributes:
        id: Unique rule identifier (e.g., 'bidi-numbers')
        description: Human-readable description
        pattern: Regex pattern for detection
        severity: Issue severity level
        context_pattern: Optional context validation regex
        exclude_pattern: Pattern to exclude from detection
        negative_pattern: Pattern that must NOT exist
        fix_template: Suggested fix template
        skip_math_mode: Skip detection inside math mode
        skip_cite_context: Skip detection inside cite commands
        document_context: Check entire document, not just line
        enabled: Whether rule is active
    """

    id: str
    description: str
    pattern: str
    severity: Severity = Severity.WARNING
    context_pattern: Optional[str] = None
    exclude_pattern: Optional[str] = None
    negative_pattern: Optional[str] = None
    fix_template: Optional[str] = None
    skip_math_mode: bool = False
    skip_cite_context: bool = False
    document_context: bool = False
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "pattern": self.pattern,
            "severity": self.severity.value,
            "context_pattern": self.context_pattern,
            "exclude_pattern": self.exclude_pattern,
            "negative_pattern": self.negative_pattern,
            "fix_template": self.fix_template,
            "skip_math_mode": self.skip_math_mode,
            "skip_cite_context": self.skip_cite_context,
            "document_context": self.document_context,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleDefinition":
        """Create from dictionary."""
        severity = data.get("severity", "warning")
        if isinstance(severity, str):
            severity = Severity(severity)
        return cls(
            id=data["id"],
            description=data.get("description", ""),
            pattern=data["pattern"],
            severity=severity,
            context_pattern=data.get("context_pattern"),
            exclude_pattern=data.get("exclude_pattern"),
            negative_pattern=data.get("negative_pattern"),
            fix_template=data.get("fix_template"),
            skip_math_mode=data.get("skip_math_mode", False),
            skip_cite_context=data.get("skip_cite_context", False),
            document_context=data.get("document_context", False),
            enabled=data.get("enabled", True),
        )


@dataclass
class PatternDefinition:
    """
    Definition of a fix pattern.

    Attributes:
        id: Unique pattern identifier
        description: Human-readable description
        find: Regex pattern to find
        replace: Replacement string (with backreferences)
        condition: Optional condition for applying
        enabled: Whether pattern is active
    """

    id: str
    description: str
    find: str
    replace: str
    condition: Optional[str] = None
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "find": self.find,
            "replace": self.replace,
            "condition": self.condition,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatternDefinition":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            description=data.get("description", ""),
            find=data["find"],
            replace=data["replace"],
            condition=data.get("condition"),
            enabled=data.get("enabled", True),
        )


@dataclass
class RuleConfig:
    """
    Runtime configuration for a rule.

    Attributes:
        rule_id: Reference to RuleDefinition
        enabled: Override for rule enabled state
        auto_fix: Whether to auto-fix issues from this rule
        custom_severity: Override severity level
    """

    rule_id: str
    enabled: bool = True
    auto_fix: bool = False
    custom_severity: Optional[Severity] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = {"enabled": self.enabled, "auto_fix": self.auto_fix}
        if self.custom_severity:
            result["severity"] = self.custom_severity.value
        return result

    @classmethod
    def from_dict(cls, rule_id: str, data: Dict[str, Any]) -> "RuleConfig":
        """Create from dictionary."""
        severity = data.get("severity")
        if severity and isinstance(severity, str):
            severity = Severity(severity)
        return cls(
            rule_id=rule_id,
            enabled=data.get("enabled", True),
            auto_fix=data.get("auto_fix", False),
            custom_severity=severity,
        )
