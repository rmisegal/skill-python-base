"""
Validation result models for BC validators.

Provides dataclasses for validation results following the project's
domain model patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

from ...domain.models.issue import Issue, Severity


@dataclass
class BCValidationIssue:
    """Validation issue found by BC validators."""

    rule: str
    severity: str
    message: str
    line: int
    suggestion: str
    auto_fixable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
            "suggestion": self.suggestion,
            "auto_fixable": self.auto_fixable,
        }


@dataclass
class FixAttempt:
    """Record of a fix attempt for an issue."""

    rule: str
    success: bool
    original: str
    fixed: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "rule": self.rule,
            "success": self.success,
            "original": self.original,
            "fixed": self.fixed,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ValidationResult:
    """Result of validating content with a BC validator."""

    validator_name: str
    content: str
    is_valid: bool
    issues: List[Issue] = field(default_factory=list)
    fixed_issues: List[FixAttempt] = field(default_factory=list)
    unfixable_issues: List[Issue] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_critical(self) -> bool:
        """Check if any unfixable issues are critical."""
        return any(i.severity == Severity.CRITICAL for i in self.unfixable_issues)

    @property
    def total_issues(self) -> int:
        """Total issues detected."""
        return len(self.issues)

    @property
    def auto_fixed_count(self) -> int:
        """Count of successfully auto-fixed issues."""
        return sum(1 for f in self.fixed_issues if f.success)

    @property
    def unfixable_count(self) -> int:
        """Count of issues that could not be fixed."""
        return len(self.unfixable_issues)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "validator_name": self.validator_name,
            "is_valid": self.is_valid,
            "total_issues": self.total_issues,
            "auto_fixed_count": self.auto_fixed_count,
            "unfixable_count": self.unfixable_count,
            "has_critical": self.has_critical,
            "issues": [i.to_dict() for i in self.issues],
            "fixed_issues": [f.to_dict() for f in self.fixed_issues],
            "unfixable_issues": [i.to_dict() for i in self.unfixable_issues],
            "timestamp": self.timestamp.isoformat(),
        }
