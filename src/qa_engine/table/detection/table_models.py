"""
Data models for table detection.

Contains dataclasses used by TableLayoutDetector and FancyTableDetector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class TableIssue:
    """Represents a table-related issue."""
    table_num: int
    page: int
    caption: str
    issue_type: str
    severity: str
    line: int
    context: str


@dataclass
class TableDetectResult:
    """Result of table detection matching skill.md format."""
    tables_found: int = 0
    issues_found: int = 0
    column_order_issues: int = 0
    caption_alignment_issues: int = 0
    cell_alignment_issues: int = 0
    details: List[TableIssue] = field(default_factory=list)

    @property
    def triggers(self) -> List[str]:
        """Return list of triggered fix skills."""
        triggers = []
        if self.column_order_issues > 0:
            triggers.append("qa-table-fix-columns")
        if self.caption_alignment_issues > 0:
            triggers.append("qa-table-fix-captions")
        if self.cell_alignment_issues > 0:
            triggers.append("qa-table-fix-alignment")
        return triggers


@dataclass
class TableProblem:
    """Represents a problem found in a table."""
    code: str
    description: str
    severity: str


@dataclass
class TableAnalysis:
    """Analysis result for a single table."""
    file: str
    line: int
    table_label: str
    classification: str  # PLAIN, PARTIAL, FANCY
    problems: List[str] = field(default_factory=list)
    severity: str = "INFO"


@dataclass
class FancyDetectResult:
    """Result of fancy table detection."""
    tables_scanned: int = 0
    plain_tables_found: int = 0
    partial_tables_found: int = 0
    fancy_tables_found: int = 0
    issues: List[TableAnalysis] = field(default_factory=list)

    @property
    def triggers(self) -> List[str]:
        """Return list of triggered fix skills."""
        if self.plain_tables_found > 0 or self.partial_tables_found > 0:
            return ["qa-table-fancy-fix"]
        return []


@dataclass
class TableOverflowIssue:
    """Represents a table overflow issue."""
    file: str
    line: int
    table_type: str  # tabular, rtltabular, tabularx, longtable
    columns: int
    has_resizebox: bool
    severity: str  # CRITICAL, WARNING, SAFE
    fix: str = ""


@dataclass
class OverflowDetectResult:
    """Result of table overflow detection."""
    tables: List[TableOverflowIssue] = field(default_factory=list)
    total_tables: int = 0
    unsafe: int = 0
    safe: int = 0

    @property
    def verdict(self) -> str:
        """Overall verdict based on findings."""
        if any(t.severity == "CRITICAL" for t in self.tables):
            return "FAIL"
        if any(t.severity == "WARNING" for t in self.tables):
            return "WARNING"
        return "PASS"

    @property
    def triggers(self) -> List[str]:
        """Triggers based on findings."""
        return ["qa-table-overflow-fix"] if self.unsafe > 0 else []
