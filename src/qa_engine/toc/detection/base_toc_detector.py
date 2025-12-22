"""
Abstract base class for TOC detectors.

Provides shared functionality for all TOC detection modules.
No hardcoded data - all configuration from JSON files.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Any

from ...domain.models.issue import Issue, Severity
from ..config.config_loader import TOCConfigLoader


class BaseTOCDetector(ABC):
    """Abstract base class for TOC detection modules."""

    def __init__(self) -> None:
        """Initialize with shared config loader."""
        self._config = TOCConfigLoader()
        self._category: str = ""

    @abstractmethod
    def detect(self, entries: List[Dict[str, Any]], file_path: str) -> List[Issue]:
        """
        Detect issues in TOC entries.

        Args:
            entries: Parsed TOC entries
            file_path: Source file path

        Returns:
            List of detected issues
        """
        pass

    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        pass

    def _get_severity(self, level: str) -> Severity:
        """Convert string severity to Severity enum."""
        severity_map = {
            "CRITICAL": Severity.CRITICAL,
            "WARNING": Severity.WARNING,
            "INFO": Severity.INFO,
        }
        return severity_map.get(level, Severity.INFO)

    def _create_issue(
        self,
        rule_name: str,
        file_path: str,
        line: int,
        content: str,
        context: Dict[str, Any] = None,
    ) -> Issue:
        """Create an Issue object with fixer recommendation."""
        rules = self._config.get_rules_by_category(self._category)
        rule_def = rules.get(rule_name, {})
        fixer_info = self._config.get_fixer_for_rule(rule_name)

        fix_suggestion = self._build_fix_suggestion(fixer_info)

        return Issue(
            rule=rule_name,
            file=file_path,
            line=line,
            content=content[:80] if content else "",
            severity=self._get_severity(rule_def.get("severity", "INFO")),
            fix=fix_suggestion,
            context=context or {},
        )

    def _build_fix_suggestion(self, fixer_info: Dict[str, Any]) -> str:
        """Build fix suggestion from fixer mapping."""
        parts = []

        if fixer_info.get("skill"):
            parts.append(f"Run skill: {fixer_info['skill']}")

        if fixer_info.get("fixer"):
            parts.append(f"Use fixer: {fixer_info['fixer']}")

        if fixer_info.get("action"):
            parts.append(f"Action: {fixer_info['action']}")

        if fixer_info.get("manual"):
            parts.append("[Manual fix required]")

        return " | ".join(parts) if parts else "Review manually"

    def _get_rules_for_category(self) -> Dict[str, Any]:
        """Get rules for this detector's category."""
        return self._config.get_rules_by_category(self._category)

    def _log_detection(self, rule: str, line: int, content: str) -> None:
        """Optional logging hook for debugging."""
        pass  # Subclasses can override
