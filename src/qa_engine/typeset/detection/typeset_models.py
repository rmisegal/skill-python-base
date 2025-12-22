"""
Data models for typeset detection.

Contains dataclasses used by LogWarningDetector matching qa-typeset-detect skill.md v1.5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class WarningSeverity(Enum):
    """Severity levels matching skill.md."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class HboxWarning:
    """Overfull/Underfull hbox warning."""
    type: str  # "overfull" or "underfull"
    amount_pt: Optional[float] = None  # For overfull
    badness: Optional[int] = None  # For underfull
    lines: List[int] = field(default_factory=list)
    context: str = ""
    severity: str = "WARNING"


@dataclass
class VboxWarning:
    """Overfull/Underfull vbox warning."""
    type: str  # "overfull" or "underfull"
    amount_pt: Optional[float] = None  # For overfull
    badness: Optional[int] = None  # For underfull
    context: str = ""
    severity: str = "WARNING"


@dataclass
class UndefinedReference:
    """Undefined reference warning."""
    reference: str
    page: int
    input_line: int
    severity: str = "CRITICAL"


@dataclass
class UndefinedCitation:
    """Undefined citation warning."""
    citation: str
    page: int
    input_line: int
    severity: str = "CRITICAL"


@dataclass
class FloatTooLarge:
    """Float too large warning."""
    overflow_pt: float
    input_line: int
    severity: str = "CRITICAL"


@dataclass
class KnownIssue:
    """Known issue that doesn't affect output."""
    type: str
    message: str
    cause: str
    severity: str = "INFO"
    affects_output: bool = False


@dataclass
class TikzOverflowRisk:
    """TikZ picture that may overflow text width."""
    file: str
    line: int
    content: str
    issue: str  # "no_width_constraint" or "large_coordinates"
    severity: str = "WARNING"
    fix: str = ""


@dataclass
class LatexError:
    """LaTeX error from log."""
    message: str
    line: Optional[int] = None
    severity: str = "CRITICAL"


@dataclass
class PackageError:
    """Package error from log."""
    package: str
    message: str
    severity: str = "WARNING"


@dataclass
class ItemsepIssue:
    """Itemize/enumerate without noitemsep in flushbottom context."""
    file: str
    line: int
    env_type: str  # "itemize" or "enumerate"
    severity: str = "WARNING"


@dataclass
class TypesetDetectResult:
    """Result matching skill.md output format."""
    log_file: str = ""
    overfull_hbox: List[HboxWarning] = field(default_factory=list)
    underfull_hbox: List[HboxWarning] = field(default_factory=list)
    overfull_vbox: List[VboxWarning] = field(default_factory=list)
    underfull_vbox: List[VboxWarning] = field(default_factory=list)
    undefined_references: List[UndefinedReference] = field(default_factory=list)
    undefined_citations: List[UndefinedCitation] = field(default_factory=list)
    float_too_large: List[FloatTooLarge] = field(default_factory=list)
    known_issues: List[KnownIssue] = field(default_factory=list)
    tikz_overflow_risk: List[TikzOverflowRisk] = field(default_factory=list)
    latex_errors: List[LatexError] = field(default_factory=list)
    package_errors: List[PackageError] = field(default_factory=list)
    itemsep_issues: List[ItemsepIssue] = field(default_factory=list)
    has_raggedbottom: bool = False
    underfull_vbox_count: int = 0

    @property
    def verdict(self) -> str:
        """FAIL if any CRITICAL, WARNING if only WARNING, else PASS."""
        all_severities = (
            [w.severity for w in self.overfull_hbox] +
            [w.severity for w in self.underfull_hbox] +
            [w.severity for w in self.overfull_vbox] +
            [w.severity for w in self.underfull_vbox] +
            [r.severity for r in self.undefined_references] +
            [c.severity for c in self.undefined_citations] +
            [f.severity for f in self.float_too_large] +
            [t.severity for t in self.tikz_overflow_risk] +
            [e.severity for e in self.latex_errors] +
            [p.severity for p in self.package_errors]
        )
        if "CRITICAL" in all_severities:
            return "FAIL"
        if "WARNING" in all_severities:
            return "WARNING"
        return "PASS"

    @property
    def triggers(self) -> List[str]:
        """Return triggered fix skills."""
        t = []
        if self.overfull_hbox or self.underfull_hbox:
            t.append("qa-typeset-fix-hbox")
        if self.undefined_references or self.undefined_citations:
            t.append("qa-typeset-fix-refs")
        if self.float_too_large:
            t.append("qa-typeset-fix-float")
        if self.tikz_overflow_risk:
            t.append("qa-typeset-fix-tikz")
        if self.overfull_vbox or self.underfull_vbox:
            t.append("qa-typeset-fix-vbox")
        return t
