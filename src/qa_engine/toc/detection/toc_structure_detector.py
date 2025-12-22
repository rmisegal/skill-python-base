"""
TOC structure detector - validates chapters, hierarchy, bibliography.

Version: 2.0.0 - Added duplicate title detection
"""

from __future__ import annotations
from typing import Dict, List, Optional

from ...domain.models.issue import Issue
from .base_toc_detector import BaseTOCDetector
from .toc_entry_parser import TOCEntry
from .structure_helpers import StructureHelpers


class TOCStructureDetector(BaseTOCDetector):
    """Detects structural issues in TOC entries."""

    def __init__(self, expected_chapters: Optional[int] = None) -> None:
        """Initialize detector."""
        super().__init__()
        self._category = "structure"
        self._expected_chapters = expected_chapters
        self._helpers = StructureHelpers(self._config)

    def detect(self, entries: List[TOCEntry], file_path: str) -> List[Issue]:
        """Detect structural issues in TOC entries."""
        issues: List[Issue] = []

        issues.extend(self._check_missing_chapters(entries, file_path))
        issues.extend(self._check_bibliography(entries, file_path))
        issues.extend(self._check_duplicates(entries, file_path))
        issues.extend(self._check_duplicate_titles(entries, file_path))
        issues.extend(self._check_sequential_duplicates(entries, file_path))
        issues.extend(self._check_similar_titles(entries, file_path))
        issues.extend(self._check_page_sequence(entries, file_path))
        issues.extend(self._check_empty_titles(entries, file_path))
        issues.extend(self._check_orphan_subsections(entries, file_path))
        issues.extend(self._check_section_gaps(entries, file_path))
        issues.extend(self._check_page_jumps(entries, file_path))

        return issues

    def _check_missing_chapters(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check if expected chapters are present."""
        if not self._expected_chapters:
            return []

        found = self._helpers.get_chapter_numbers(entries)
        issues = []

        for expected in range(1, self._expected_chapters + 1):
            if expected not in found:
                issues.append(self._create_issue(
                    "toc-missing-chapter", file_path, 0,
                    f"Chapter {expected} missing from TOC",
                    {"missing_chapter": expected},
                ))

        return issues

    def _check_bibliography(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check if bibliography appears in TOC."""
        if len(entries) <= 5:
            return []

        if not self._helpers.has_bibliography(entries):
            return [self._create_issue(
                "toc-bibliography-missing", file_path, 0,
                "Bibliography section not found in TOC",
            )]

        return []

    def _check_duplicates(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check for duplicate TOC entries."""
        issues = []
        seen: Dict[str, int] = {}

        for entry in entries:
            key = self._helpers.make_entry_key(entry)
            if key in seen:
                issues.append(self._create_issue(
                    "toc-duplicate-entry", file_path, entry.line_number,
                    f"Duplicate entry: {entry.title[:40]}",
                    {"first_occurrence": seen[key]},
                ))
            else:
                seen[key] = entry.line_number

        return issues

    def _check_page_sequence(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check page numbers are sequential."""
        issues = []
        last_page = 0

        for entry in entries:
            page = self._helpers.parse_page_number(entry.page)
            if page is not None and page < last_page and last_page > 0:
                issues.append(self._create_issue(
                    "toc-page-not-sequential", file_path, entry.line_number,
                    f"Page {page} after page {last_page}",
                ))
            if page is not None:
                last_page = page

        return issues

    def _check_empty_titles(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check for empty or whitespace-only titles."""
        issues = []

        for entry in entries:
            if self._helpers.is_empty_title(entry.title):
                issues.append(self._create_issue(
                    "toc-empty-title", file_path, entry.line_number,
                    "Empty or command-only title",
                ))

        return issues

    def _check_orphan_subsections(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """Check for subsections without parent sections."""
        issues = []
        current_section = None

        for entry in entries:
            if entry.entry_type == "section":
                current_section = entry.number
            elif entry.entry_type == "chapter":
                current_section = None
            elif entry.entry_type == "subsection" and not current_section:
                issues.append(self._create_issue(
                    "toc-orphan-subsection", file_path, entry.line_number,
                    f"Subsection {entry.number} without parent section",
                ))

        return issues

    def _check_duplicate_titles(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """
        Check for duplicate titles regardless of section number (v2.0).

        Catches cases like:
        - 11.19 English References
        - 11.20 English References
        """
        issues = []
        duplicates = self._helpers.find_duplicate_titles(entries)

        for key, group in duplicates.items():
            # Extract normalized title from key
            _, normalized_title = key.split(":", 1)

            # Get entry details for message
            entries_info = [
                f"{e.number} (line {e.line_number}, page {e.page})"
                for e in group
            ]

            issues.append(self._create_issue(
                "toc-duplicate-title",
                file_path,
                group[0].line_number,
                f"Title appears {len(group)} times: '{normalized_title[:30]}...'",
                severity="WARNING",
                context={
                    "normalized_title": normalized_title,
                    "occurrences": len(group),
                    "entries": entries_info,
                    "lines": [e.line_number for e in group],
                },
            ))

        return issues

    def _check_sequential_duplicates(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """
        Check for adjacent entries with same title (v2.0).

        These are more likely to be errors (copy-paste).
        """
        issues = []
        duplicates = self._helpers.find_sequential_duplicates(entries)

        for entry1, entry2 in duplicates:
            issues.append(self._create_issue(
                "toc-sequential-duplicate",
                file_path,
                entry2.line_number,
                f"Adjacent duplicate: '{entry1.title[:30]}...' at lines {entry1.line_number} and {entry2.line_number}",
                severity="CRITICAL",
                context={
                    "first_line": entry1.line_number,
                    "second_line": entry2.line_number,
                    "first_number": entry1.number,
                    "second_number": entry2.number,
                },
            ))

        return issues

    def _check_similar_titles(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """
        Check for very similar titles (v2.0).

        Catches near-duplicates that may indicate typos.
        """
        issues = []
        similar = self._helpers.find_similar_titles(entries, threshold=0.85)

        for entry1, entry2, similarity in similar:
            issues.append(self._create_issue(
                "toc-similar-title",
                file_path,
                entry2.line_number,
                f"Similar titles ({similarity:.0%}): '{entry1.title[:20]}...' and '{entry2.title[:20]}...'",
                severity="INFO",
                context={
                    "similarity": similarity,
                    "title1": entry1.title,
                    "title2": entry2.title,
                    "line1": entry1.line_number,
                    "line2": entry2.line_number,
                },
            ))

        return issues

    def _check_section_gaps(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """
        Check for missing vertical gaps before section entries (v2.3).

        Sections following subsections should have visual gaps.
        """
        issues = []
        missing_gaps = self._helpers.find_missing_section_gaps(entries)

        for prev_entry, section_entry in missing_gaps:
            issues.append(self._create_issue(
                "toc-section-gap-missing",
                file_path,
                section_entry.line_number,
                f"Section {section_entry.number} follows {prev_entry.entry_type} without gap",
                severity="WARNING",
                context={
                    "section_number": section_entry.number,
                    "section_title": section_entry.title[:30],
                    "previous_type": prev_entry.entry_type,
                    "previous_number": prev_entry.number,
                },
            ))

        return issues

    def _check_page_jumps(
        self, entries: List[TOCEntry], file_path: str
    ) -> List[Issue]:
        """
        Check for anomalous page number jumps within sections (v2.3).

        Large jumps within subsection groups may indicate copy-paste errors.
        """
        issues = []
        jumps = self._helpers.find_page_number_jumps(entries, threshold=10)

        for entry1, entry2, jump_size in jumps:
            issues.append(self._create_issue(
                "toc-page-number-jump",
                file_path,
                entry2.line_number,
                f"Page jump of {jump_size} pages: {entry1.number} (p.{entry1.page}) → {entry2.number} (p.{entry2.page})",
                severity="WARNING",
                context={
                    "from_entry": entry1.number,
                    "from_page": entry1.page,
                    "to_entry": entry2.number,
                    "to_page": entry2.page,
                    "jump_size": jump_size,
                },
            ))

        return issues

    def set_expected_chapters(self, count: int) -> None:
        """Set the expected number of chapters."""
        self._expected_chapters = count

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        rules = self._get_rules_for_category()
        # Add new rules
        rules.update({
            "toc-duplicate-title": "Same title appears multiple times with different numbers",
            "toc-sequential-duplicate": "Adjacent entries have identical titles",
            "toc-similar-title": "Very similar titles may indicate typo or copy-paste error",
            "toc-section-gap-missing": "Missing vertical gap before section entry",
            "toc-page-number-jump": "Anomalous page number jump within section",
        })
        return rules
