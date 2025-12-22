"""
Issue model for QA detection results.

Represents a single issue detected in a LaTeX document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Severity(Enum):
    """Issue severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Issue:
    """
    Standard issue representation returned by detectors.

    Attributes:
        rule: Detection rule that triggered this issue
        file: Path to the file containing the issue
        line: Line number where issue was found (1-indexed)
        content: The problematic content/line
        severity: Issue severity level
        fix: Optional suggested fix
        context: Additional context data
    """

    rule: str
    file: str
    line: int
    content: str
    severity: Severity
    fix: Optional[str] = None
    context: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary for JSON serialization."""
        return {
            "rule": self.rule,
            "file": self.file,
            "line": self.line,
            "content": self.content,
            "severity": self.severity.value,
            "fix": self.fix,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Issue:
        """Create Issue from dictionary."""
        return cls(
            rule=data["rule"],
            file=data["file"],
            line=data["line"],
            content=data["content"],
            severity=Severity(data["severity"]),
            fix=data.get("fix"),
            context=data.get("context", {}),
        )

    def with_offset(self, offset: int) -> Issue:
        """Return a new Issue with adjusted line number."""
        return Issue(
            rule=self.rule,
            file=self.file,
            line=self.line + offset,
            content=self.content,
            severity=self.severity,
            fix=self.fix,
            context=self.context,
        )
