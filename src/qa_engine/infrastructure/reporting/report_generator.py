"""
Report generator for QA results.

Implements FR-103 from PRD - generates QA reports in various formats.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from ...domain.models.issue import Issue
from ...domain.models.status import QAStatus
from .formatters import format_json, format_markdown, format_summary


class ReportFormat(Enum):
    """Supported report formats."""

    JSON = "json"
    MARKDOWN = "markdown"
    SUMMARY = "summary"


class ReportGenerator:
    """Generates QA reports in various formats."""

    def generate(
        self,
        issues: List[Issue],
        status: Optional[QAStatus] = None,
        format: ReportFormat = ReportFormat.MARKDOWN,
    ) -> str:
        """Generate report in specified format."""
        by_severity = self._count_by_severity(issues)
        by_rule = self._count_by_rule(issues)
        by_file = self._group_by_file(issues)

        if format == ReportFormat.JSON:
            return format_json(issues, status, by_severity, by_rule)
        elif format == ReportFormat.MARKDOWN:
            return format_markdown(issues, status, by_severity, by_file)
        else:
            return format_summary(issues, status, by_severity, by_rule)

    def _count_by_severity(self, issues: List[Issue]) -> Dict[str, int]:
        """Count issues by severity."""
        counts: Dict[str, int] = {}
        for issue in issues:
            sev = issue.severity.value
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def _count_by_rule(self, issues: List[Issue]) -> Dict[str, int]:
        """Count issues by rule."""
        counts: Dict[str, int] = {}
        for issue in issues:
            counts[issue.rule] = counts.get(issue.rule, 0) + 1
        return counts

    def _group_by_file(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """Group issues by file path."""
        groups: Dict[str, List[Issue]] = {}
        for issue in issues:
            if issue.file not in groups:
                groups[issue.file] = []
            groups[issue.file].append(issue)
        return groups

    def save(
        self,
        issues: List[Issue],
        output_path: Path,
        format: ReportFormat = ReportFormat.MARKDOWN,
        status: Optional[QAStatus] = None,
    ) -> None:
        """Save report to file."""
        content = self.generate(issues, status, format)
        output_path.write_text(content, encoding="utf-8")
