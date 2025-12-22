"""
TOC BiDi detector.

Validates bidirectional text direction in TOC entries.
All patterns loaded from JSON configuration.

Version: 2.0.0 - Added naked English detection (will render RTL)
"""

from __future__ import annotations

import re
from typing import Dict, List

from ...domain.models.issue import Issue
from .base_toc_detector import BaseTOCDetector
from .toc_entry_parser import TOCEntry
from .bidi_helpers import BiDiHelpers


class TOCBiDiDetector(BaseTOCDetector):
    """Detects BiDi issues in TOC entries."""

    def __init__(self) -> None:
        """Initialize detector with patterns."""
        super().__init__()
        self._category = "bidi_number"
        self._helpers = BiDiHelpers(self._config)

    def detect(self, entries: List[TOCEntry], file_path: str) -> List[Issue]:
        """Detect BiDi issues in TOC entries."""
        issues: List[Issue] = []

        for entry in entries:
            issues.extend(self._check_number_direction(entry, file_path))
            issues.extend(self._check_text_direction(entry, file_path))
            issues.extend(self._check_parentheticals(entry, file_path))
            issues.extend(self._check_mixed_patterns(entry, file_path))
            issues.extend(self._check_naked_english(entry, file_path))

        return issues

    def _check_number_direction(
        self, entry: TOCEntry, file_path: str
    ) -> List[Issue]:
        """Check all numbers are wrapped in LTR."""
        issues: List[Issue] = []

        if not self._helpers.has_ltr_wrapper(entry.title) and entry.number:
            rule = f"toc-{entry.entry_type}-number-not-ltr"
            issues.append(self._create_issue(
                rule, file_path, entry.line_number,
                f"Number {entry.number} not in LTR wrapper",
            ))

        if self._helpers.has_unwrapped_percentage(entry.title):
            issues.append(self._create_issue(
                "toc-percentage-not-ltr", file_path, entry.line_number,
                "Percentage not wrapped in LTR",
            ))

        return issues

    def _check_text_direction(
        self, entry: TOCEntry, file_path: str
    ) -> List[Issue]:
        """Check English and Hebrew text direction."""
        issues: List[Issue] = []

        for word, pos in self._helpers.find_unwrapped_english(entry.title):
            issues.append(self._create_issue(
                "toc-english-text-not-ltr", file_path, entry.line_number,
                f"English '{word}' not wrapped",
                {"word": word, "position": pos},
            ))

        for acronym in self._helpers.find_unwrapped_acronyms(entry.title):
            issues.append(self._create_issue(
                "toc-acronym-not-ltr", file_path, entry.line_number,
                f"Acronym '{acronym}' not wrapped",
            ))

        return issues

    def _check_parentheticals(
        self, entry: TOCEntry, file_path: str
    ) -> List[Issue]:
        """Check parenthetical direction in Hebrew context."""
        issues: List[Issue] = []

        if not self._helpers.has_hebrew(entry.title):
            return issues

        for paren_type, is_valid in self._helpers.check_parentheticals(entry.title):
            if not is_valid:
                rule = f"toc-{paren_type}-reversed"
                issues.append(self._create_issue(
                    rule, file_path, entry.line_number,
                    f"Parenthetical '{paren_type}' may be reversed",
                ))

        if self._helpers.has_nested_parens(entry.title):
            issues.append(self._create_issue(
                "toc-nested-parens-bidi", file_path, entry.line_number,
                "Nested parentheses in mixed text",
            ))

        return issues

    def _check_mixed_patterns(
        self, entry: TOCEntry, file_path: str
    ) -> List[Issue]:
        """Check complex mixed Hebrew/English patterns."""
        issues: List[Issue] = []

        if self._helpers.has_heb_eng_heb_pattern(entry.title):
            issues.append(self._create_issue(
                "toc-mixed-heb-eng-heb", file_path, entry.line_number,
                "Hebrew→English→Hebrew pattern detected",
            ))

        if self._helpers.has_eng_heb_eng_pattern(entry.title):
            issues.append(self._create_issue(
                "toc-mixed-eng-heb-eng", file_path, entry.line_number,
                "English→Hebrew→English pattern detected",
            ))

        return issues

    def _check_naked_english(
        self, entry: TOCEntry, file_path: str
    ) -> List[Issue]:
        """
        Check for naked English text that will render RTL (v2.0).

        Naked English = English text not wrapped in LTR command.
        In RTL document, this renders backwards:
          "English References" → "secnerefeR hsilgnE"
        """
        issues: List[Issue] = []

        # Find naked English in this entry
        naked_items = self._helpers.find_naked_english(
            entry.raw_content,
            entry.title
        )

        if not naked_items:
            return issues

        # Get severity based on amount of naked English
        severity = self._helpers.get_naked_english_severity(naked_items)

        # Extract the naked words for reporting
        naked_words = [word for word, _ in naked_items]
        words_str = ", ".join(naked_words[:5])  # Limit to 5 words
        if len(naked_words) > 5:
            words_str += f" (+{len(naked_words) - 5} more)"

        # Create single issue per entry (not per word)
        issues.append(self._create_issue(
            "toc-english-text-naked",
            file_path,
            entry.line_number,
            f"English will render RTL: [{words_str}]",
            severity=severity,
            context={
                "naked_words": naked_words,
                "entry_type": entry.entry_type,
                "fix": "Wrap English text in \\textenglish{} or \\en{}",
                "example_bad": f"{entry.title[:50]}",
                "example_good": f"\\textenglish{{{naked_words[0]}}}",
            },
        ))

        return issues

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        rules = {}
        for cat in ["bidi_number", "parenthetical", "bidi_text", "alignment"]:
            self._category = cat
            cat_rules = self._get_rules_for_category()
            rules.update({n: r.get("description", "") for n, r in cat_rules.items()})

        # Add new v2.0 naked English rule
        rules["toc-english-text-naked"] = (
            "English text without LTR wrapper will render RTL (backwards)"
        )

        return rules
