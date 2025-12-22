"""
TOC comprehensive detector - Main orchestrator.

Coordinates all TOC detection modules for complete validation.
Generates unified reports with fix recommendations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any, Optional

from ...domain.models.issue import Issue
from ..config.config_loader import TOCConfigLoader
from .toc_entry_parser import TOCEntryParser, TOCEntry
from .toc_numbering_detector import TOCNumberingDetector
from .toc_bidi_detector import TOCBiDiDetector
from .toc_structure_detector import TOCStructureDetector


class TOCComprehensiveDetector:
    """
    Orchestrates all TOC detection modules.

    Provides unified detection across:
    - Numbering validation
    - BiDi direction validation
    - Structure validation
    """

    def __init__(self, expected_chapters: Optional[int] = None) -> None:
        """Initialize all detection modules."""
        self._config = TOCConfigLoader()
        self._parser = TOCEntryParser()
        self._numbering = TOCNumberingDetector()
        self._bidi = TOCBiDiDetector()
        self._structure = TOCStructureDetector(expected_chapters)

    def detect_in_file(self, toc_path: str) -> List[Issue]:
        """Run all detectors on a .toc file."""
        entries = self._parser.parse_file(toc_path)
        return self._run_all_detectors(entries, toc_path)

    def detect_in_content(self, content: str, file_path: str = "") -> List[Issue]:
        """Run all detectors on TOC content string."""
        entries = self._parser.parse_content(content, file_path)
        return self._run_all_detectors(entries, file_path)

    def _run_all_detectors(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Run all detection modules and combine results."""
        all_issues: List[Issue] = []

        all_issues.extend(self._numbering.detect(entries, file_path))
        all_issues.extend(self._bidi.detect(entries, file_path))
        all_issues.extend(self._structure.detect(entries, file_path))

        return self._deduplicate_issues(all_issues)

    def _deduplicate_issues(self, issues: List[Issue]) -> List[Issue]:
        """Remove duplicate issues based on rule+line+content."""
        seen = set()
        unique = []

        for issue in issues:
            key = (issue.rule, issue.line, issue.content[:50])
            if key not in seen:
                seen.add(key)
                unique.append(issue)

        return unique

    def detect_project(self, project_path: str) -> Dict[str, List[Issue]]:
        """Detect issues in all .toc files in a project."""
        results: Dict[str, List[Issue]] = {}
        project = Path(project_path)

        for toc_file in project.rglob("*.toc"):
            issues = self.detect_in_file(str(toc_file))
            if issues:
                results[str(toc_file)] = issues

        return results

    def generate_report(self, issues: List[Issue]) -> Dict[str, Any]:
        """Generate a structured report from issues."""
        report = {
            "summary": {
                "total_issues": len(issues),
                "critical": 0,
                "warning": 0,
                "info": 0,
            },
            "by_category": {},
            "by_rule": {},
            "issues": [],
        }

        for issue in issues:
            sev = issue.severity.value
            report["summary"][sev.lower()] = report["summary"].get(sev.lower(), 0) + 1

            category = issue.rule.split("-")[1] if "-" in issue.rule else "other"
            if category not in report["by_category"]:
                report["by_category"][category] = []
            report["by_category"][category].append(issue.to_dict())

            if issue.rule not in report["by_rule"]:
                report["by_rule"][issue.rule] = []
            report["by_rule"][issue.rule].append(issue.line)

            report["issues"].append(issue.to_dict())

        return report

    def get_all_rules(self) -> Dict[str, str]:
        """Get all rules from all detectors."""
        rules = {}
        rules.update(self._numbering.get_rules())
        rules.update(self._bidi.get_rules())
        rules.update(self._structure.get_rules())
        return rules

    def set_expected_chapters(self, count: int) -> None:
        """Set expected chapter count for structure validation."""
        self._structure.set_expected_chapters(count)

    @property
    def total_rules(self) -> int:
        """Get total number of detection rules."""
        return self._config.total_rules

    def get_entries(self, toc_path: str) -> List[TOCEntry]:
        """Get parsed entries for external analysis."""
        return self._parser.parse_file(toc_path)

    def get_unnumbered_entries(self, toc_path: str) -> List[Dict[str, Any]]:
        """
        Get all unnumbered entries with classification (v2.0).

        Returns list of dicts with:
        - entry_type: chapter/section/subsection/subsubsection
        - title: Entry title text
        - line: Line number in .toc file
        - classification: EXPECTED/STARRED/UNEXPECTED
        - hyperref: Hyperref anchor pattern
        """
        entries = self._parser.parse_file(toc_path)
        return self._numbering.get_unnumbered_entries(entries)
