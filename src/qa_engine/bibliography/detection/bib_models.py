"""
Data models for bibliography detection.

Contains dataclasses used by BibDetector matching qa-bib-detect skill.md v1.1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BibIssueType(Enum):
    """Types of bibliography issues."""
    MISSING_ENTRY = "missing_entry"
    MISSING_PRINTBIB = "missing_printbib"
    NOT_IN_TOC = "not_in_toc"
    EMPTY_BIBLIOGRAPHY = "empty_bibliography"
    UNUSED_ENTRY = "unused_entry"
    NOT_IN_ENGLISH = "not_in_english"
    SPACING_TOO_LARGE = "spacing_too_large"


class BibSeverity(Enum):
    """Severity levels for bibliography issues."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CitationLocation:
    """Location of a citation in source files."""
    key: str
    file: str
    line: int


@dataclass
class BibIssue:
    """Represents a bibliography issue."""
    type: BibIssueType
    severity: BibSeverity
    key: Optional[str] = None
    cited_in: Optional[str] = None
    line: Optional[int] = None
    message: str = ""


@dataclass
class BibDetectResult:
    """Result of bibliography detection matching qa-bib-detect skill.md."""
    citations_total: int = 0
    citations_unique: List[str] = field(default_factory=list)
    citation_locations: List[CitationLocation] = field(default_factory=list)
    bib_file: str = ""
    bib_entries: List[str] = field(default_factory=list)
    issues: List[BibIssue] = field(default_factory=list)
    has_printbib: bool = False
    bib_in_toc: bool = False
    bib_rendered: bool = True
    bib_in_english: bool = True
    has_bibitemsep: bool = False

    @property
    def missing_entries(self) -> List[str]:
        """Get list of missing bibliography entries."""
        return [i.key for i in self.issues
                if i.type == BibIssueType.MISSING_ENTRY and i.key]

    @property
    def unused_entries(self) -> List[str]:
        """Get list of unused bibliography entries."""
        return [i.key for i in self.issues
                if i.type == BibIssueType.UNUSED_ENTRY and i.key]

    @property
    def unique_keys(self) -> List[str]:
        """Get list of unique citation keys."""
        return self.citations_unique

    @property
    def verdict(self) -> str:
        """Determine verdict based on issues."""
        severities = [i.severity for i in self.issues]
        if BibSeverity.CRITICAL in severities:
            return "FAIL"
        if BibSeverity.WARNING in severities:
            return "WARNING"
        return "PASS"

    @property
    def triggers(self) -> List[str]:
        """Return triggered fix skills."""
        critical_types = [BibIssueType.MISSING_ENTRY, BibIssueType.MISSING_PRINTBIB,
                         BibIssueType.EMPTY_BIBLIOGRAPHY, BibIssueType.NOT_IN_ENGLISH]
        if any(i.type in critical_types for i in self.issues):
            return ["qa-bib-fix-missing"]
        if any(i.type == BibIssueType.NOT_IN_TOC for i in self.issues):
            return ["qa-bib-fix-missing"]
        return []


@dataclass
class BibFixResult:
    """Result of bibliography fix operation."""
    fixes_applied: List[Dict[str, Any]] = field(default_factory=list)
    manual_actions: List[str] = field(default_factory=list)
    recompile_needed: bool = False
    passes_required: int = 3

    @property
    def status(self) -> str:
        if self.fixes_applied:
            return "DONE"
        return "MANUAL_REVIEW" if self.manual_actions else "NO_CHANGES"


@dataclass
class BibOrchestratorResult:
    """Result of bibliography orchestrator (Level 1)."""
    detect_result: Optional[BibDetectResult] = None
    fix_result: Optional[BibFixResult] = None

    @property
    def verdict(self) -> str:
        if self.detect_result:
            return self.detect_result.verdict
        return "PASS"

    @property
    def status(self) -> str:
        return "DONE"
