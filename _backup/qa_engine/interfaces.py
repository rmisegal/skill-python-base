"""
Core interfaces for QA detection and fix tools.

Defines the contracts that all detectors and fixers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any


class Severity(Enum):
    """Issue severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Issue:
    """Standard issue representation returned by detectors."""
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
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
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


class DetectorInterface(ABC):
    """Interface for detection tools. MUST NOT modify content."""

    @abstractmethod
    def detect(
        self, content: str, file_path: str, offset: int = 0
    ) -> List[Issue]:
        """
        Detect issues in content.

        Args:
            content: The text content to analyze
            file_path: Path to the source file
            offset: Line number offset for chunked processing

        Returns:
            List of Issue objects found
        """
        pass

    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """
        Return dict of rule_name -> description.

        Returns:
            Dictionary mapping rule names to their descriptions
        """
        pass


class FixerInterface(ABC):
    """Interface for fix tools. MUST NOT detect new issues."""

    @abstractmethod
    def fix(self, content: str, issues: List[Issue]) -> str:
        """
        Apply fixes to content based on provided issues.

        Args:
            content: The text content to fix
            issues: List of Issue objects to fix

        Returns:
            Fixed content string
        """
        pass

    @abstractmethod
    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """
        Return dict of pattern_name -> {find, replace, description}.

        Returns:
            Dictionary mapping pattern names to their definitions
        """
        pass
