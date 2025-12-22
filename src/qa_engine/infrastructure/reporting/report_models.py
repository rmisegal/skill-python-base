"""
Report data models for QA Super.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ...domain.models.issue import Issue


@dataclass
class CLSCheckResult:
    """Result of CLS version check."""
    status: str  # CURRENT, FIXED, FAILED
    version: str = ""
    action_taken: str = ""


@dataclass
class FamilyResult:
    """Result of a single family execution."""
    family: str
    verdict: str  # PASS, FAIL, WARNING
    issues_found: int = 0
    issues_fixed: int = 0
    detection_verified: bool = False


@dataclass
class QASuperReport:
    """Complete QA Super report data."""
    document_name: str
    cls_check: Optional[CLSCheckResult] = None
    families: List[FamilyResult] = field(default_factory=list)
    critical_issues: List[Issue] = field(default_factory=list)
    warnings: List[Issue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
