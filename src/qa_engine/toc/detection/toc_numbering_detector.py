"""
TOC numbering detector.

Validates numbering continuity and format in TOC entries.
Detects unnumbered entries and classifies them.
All rules loaded from JSON configuration.

Version: 2.0.0 - Added unnumbered entry detection
"""

from __future__ import annotations

import re
from typing import Dict, List, Any

from ...domain.models.issue import Issue
from .base_toc_detector import BaseTOCDetector
from .toc_entry_parser import TOCEntry


# Patterns for expected unnumbered entries (bibliography, appendix, etc.)
EXPECTED_UNNUMBERED_PATTERNS = [
    r"מקורות",           # Hebrew bibliography
    r"bibliography",     # English bibliography
    r"references",       # References
    r"נספח",             # Hebrew appendix
    r"appendix",         # English appendix
    r"תוכן עניינים",    # Table of contents
    r"רשימת",            # List of (figures/tables)
    r"מפתח",             # Index
    r"index",            # English index
    r"הקדמה",            # Introduction/preface
    r"preface",          # English preface
]


class TOCNumberingDetector(BaseTOCDetector):
    """Detects numbering issues in TOC entries."""

    def __init__(self) -> None:
        """Initialize detector."""
        super().__init__()
        self._category = "numbering"

    def detect(self, entries: List[TOCEntry], file_path: str) -> List[Issue]:
        """Detect numbering issues in TOC entries."""
        issues: List[Issue] = []

        issues.extend(self._check_chapter_continuity(entries, file_path))
        issues.extend(self._check_section_continuity(entries, file_path))
        issues.extend(self._check_number_format(entries, file_path))
        issues.extend(self._check_sources_numbering(entries, file_path))
        issues.extend(self._check_unnumbered_entries(entries, file_path))

        return issues

    def _check_chapter_continuity(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check chapter numbers are continuous."""
        issues: List[Issue] = []
        chapters = [e for e in entries if e.entry_type == "chapter" and e.number]

        expected = 1
        for chapter in chapters:
            try:
                num = int(chapter.number)
                if num != expected:
                    issues.append(self._create_issue(
                        "toc-chapter-gap",
                        file_path,
                        chapter.line_number,
                        f"Expected chapter {expected}, found {num}",
                        {"expected": expected, "found": num},
                    ))
                expected = num + 1
            except ValueError:
                continue

        return issues

    def _check_section_continuity(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check section numbers are continuous within chapters."""
        issues: List[Issue] = []
        current_chapter = None
        expected_section = 1

        for entry in entries:
            if entry.entry_type == "chapter":
                current_chapter = entry.number
                expected_section = 1
            elif entry.entry_type == "section" and entry.number:
                parts = entry.number.split(".")
                if len(parts) >= 2:
                    try:
                        section_num = int(parts[1])
                        if section_num != expected_section:
                            issues.append(self._create_issue(
                                "toc-numbering-discontinuous",
                                file_path,
                                entry.line_number,
                                f"Expected {current_chapter}.{expected_section}, found {entry.number}",
                            ))
                        expected_section = section_num + 1
                    except ValueError:
                        continue

        return issues

    def _check_number_format(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check numbering follows X.Y.Z pattern."""
        issues: List[Issue] = []
        format_patterns = {
            "section": r"^\d+\.\d+$",
            "subsection": r"^\d+\.\d+\.\d+$",
            "subsubsection": r"^\d+\.\d+\.\d+\.\d+$",
        }

        for entry in entries:
            if entry.entry_type in format_patterns and entry.number:
                pattern = format_patterns[entry.entry_type]
                if not re.match(pattern, entry.number):
                    issues.append(self._create_issue(
                        "toc-numbering-format-invalid",
                        file_path,
                        entry.line_number,
                        f"Invalid format: {entry.number} for {entry.entry_type}",
                    ))

        return issues

    def _check_sources_numbering(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check if sources section has sequential number."""
        issues: List[Issue] = []
        bib_pattern = self._config.get_raw_pattern("bibliography_patterns", "hebrew")

        for entry in entries:
            if bib_pattern and re.search(bib_pattern, entry.title):
                if not entry.number:
                    issues.append(self._create_issue(
                        "toc-sources-no-number",
                        file_path,
                        entry.line_number,
                        "Sources section without sequential number",
                        severity="INFO",  # Expected behavior
                    ))

        return issues

    def _check_unnumbered_entries(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """
        Detect and classify unnumbered TOC entries (v2.0).

        Checks for presence of \\numberline{} in raw content.
        Classifies as:
        - EXPECTED: Bibliography, appendix, front matter
        - STARRED: Entries with *.N hyperref pattern
        - UNEXPECTED: Regular entries missing numbers
        """
        issues: List[Issue] = []

        for entry in entries:
            # Check if entry has \numberline{} in raw content
            has_numberline = r"\numberline" in entry.raw_content

            if has_numberline:
                continue  # Entry is properly numbered

            # Entry is unnumbered - classify it
            is_starred = "*." in entry.hyperref
            is_expected = self._is_expected_unnumbered(entry.title)

            if is_expected:
                # Expected unnumbered (bibliography, appendix, etc.)
                issues.append(self._create_issue(
                    "toc-unnumbered-entry-expected",
                    file_path,
                    entry.line_number,
                    f"Expected unnumbered {entry.entry_type}: {entry.title[:40]}",
                    severity="INFO",
                    context={"classification": "EXPECTED", "type": entry.entry_type},
                ))
            elif is_starred:
                # Starred entry (e.g., chapter*, section*)
                issues.append(self._create_issue(
                    "toc-unnumbered-entry-starred",
                    file_path,
                    entry.line_number,
                    f"Starred {entry.entry_type}: {entry.title[:40]}",
                    severity="INFO",
                    context={"classification": "STARRED", "type": entry.entry_type},
                ))
            else:
                # UNEXPECTED - should have number!
                rule_name = f"toc-{entry.entry_type}-no-numberline"
                issues.append(self._create_issue(
                    rule_name,
                    file_path,
                    entry.line_number,
                    f"Missing \\numberline{{}} in {entry.entry_type}: {entry.title[:40]}",
                    severity="WARNING",
                    context={
                        "classification": "UNEXPECTED",
                        "type": entry.entry_type,
                        "fix": "Check source .tex file for missing counter",
                    },
                ))

        return issues

    def _is_expected_unnumbered(self, title: str) -> bool:
        """Check if title matches expected unnumbered patterns."""
        for pattern in EXPECTED_UNNUMBERED_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return True
        return False

    def get_unnumbered_entries(
        self, entries: List[TOCEntry]
    ) -> List[Dict[str, Any]]:
        """
        Get all unnumbered entries with classification.

        Returns list of dicts with entry info and classification.
        """
        result = []

        for entry in entries:
            has_numberline = r"\numberline" in entry.raw_content

            if not has_numberline:
                is_starred = "*." in entry.hyperref
                is_expected = self._is_expected_unnumbered(entry.title)

                classification = "EXPECTED" if is_expected else (
                    "STARRED" if is_starred else "UNEXPECTED"
                )

                result.append({
                    "entry_type": entry.entry_type,
                    "title": entry.title,
                    "line": entry.line_number,
                    "classification": classification,
                    "hyperref": entry.hyperref,
                })

        return result

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        rules = self._get_rules_for_category()
        # Add new v2.0 rules
        rules.update({
            "toc-chapter-no-numberline": "Chapter entry missing \\numberline{}",
            "toc-section-no-numberline": "Section entry missing \\numberline{}",
            "toc-subsection-no-numberline": "Subsection entry missing \\numberline{}",
            "toc-subsubsection-no-numberline": "Subsubsection missing \\numberline{}",
            "toc-unnumbered-entry-expected": "Expected unnumbered (bib, appendix)",
            "toc-unnumbered-entry-starred": "Starred entry without number",
            "toc-unnumbered-chapter-unexpected": "Unexpected unnumbered chapter",
            "toc-unnumbered-section-unexpected": "Unexpected unnumbered section",
        })
        return {name: desc for name, desc in rules.items()}
