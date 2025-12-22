"""
BiDi fixer for Hebrew-English LaTeX.

Implements FR-501 from PRD - fixes BiDi text issues.
Uses CLS built-in commands: \en{}, \num{}, \hebyear{}, \percent{}
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue


class BiDiFixer(FixerInterface):
    """
    Fixes bidirectional text issues in Hebrew-English LaTeX.

    Uses CLS built-in commands:
    - \en{} for English text and acronyms
    - \num{} for numbers
    - \hebyear{} for years
    - \percent{} for percentages
    """

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        lines = content.split("\n")

        # Group issues by line for efficient processing
        issues_by_line: Dict[int, List[Issue]] = {}
        for issue in issues:
            line_num = issue.line
            if line_num not in issues_by_line:
                issues_by_line[line_num] = []
            issues_by_line[line_num].append(issue)

        # Apply fixes line by line (reverse order to preserve positions)
        for line_num in sorted(issues_by_line.keys(), reverse=True):
            if 1 <= line_num <= len(lines):
                line = lines[line_num - 1]
                fixed_line = self._fix_line(line, issues_by_line[line_num])
                lines[line_num - 1] = fixed_line

        return "\n".join(lines)

    def _fix_line(self, line: str, issues: List[Issue]) -> str:
        """Apply fixes to a single line."""
        # Sort by position (right to left to preserve positions)
        sorted_issues = sorted(
            issues,
            key=lambda i: i.context.get("match_start", 0),
            reverse=True,
        )

        for issue in sorted_issues:
            content = issue.content
            pos = issue.context.get("match_start", 0)
            if not content:
                continue

            # Skip if this specific occurrence is already wrapped
            if self._is_wrapped_at_position(line, content, pos):
                continue

            # Apply appropriate fix based on rule
            fixed = self._get_fix(issue.rule, content)
            if fixed and fixed != content:
                line = self._replace_at_position(line, content, fixed, pos)

        return line

    def _is_wrapped_at_position(self, line: str, content: str, pos: int) -> bool:
        """Check if content at specific position is already wrapped."""
        # Check if there's a wrapper command right before this position
        before = line[max(0, pos - 20):pos]
        wrappers = [r"\\en\{$", r"\\num\{$", r"\\hebyear\{$", r"\\percent\{$", r"\\textenglish\{$"]
        for wrapper in wrappers:
            if re.search(wrapper, before):
                return True
        return False

    def _get_fix(self, rule: str, content: str) -> str:
        """Get the appropriate fix for a rule."""
        if rule == "bidi-numbers":
            return self._fix_number(content)
        elif rule == "bidi-year-range":
            return self._fix_year_range(content)
        elif rule == "bidi-english":
            return f"\\en{{{content}}}"
        elif rule == "bidi-acronym":
            return f"\\en{{{content}}}"
        elif rule == "bidi-hebrew-in-english":
            # Hebrew inside English - restructure needed
            return content  # Complex fix, handle separately
        return content

    def _fix_number(self, num: str) -> str:
        """Apply appropriate fix for numbers."""
        # Check if it's a year (4 digits, 19xx or 20xx)
        if re.match(r"^(19|20)\d{2}$", num):
            return f"\\hebyear{{{num}}}"
        # Check if it has percent
        if "%" in num:
            num_only = num.replace("%", "").replace("\\%", "")
            return f"\\percent{{{num_only}}}"
        # Default to \num{}
        return f"\\num{{{num}}}"

    def _fix_year_range(self, year_range: str) -> str:
        """Apply fix for year ranges like 2025-2026."""
        # Content comes as full match, wrap entire range with \hebyear{}
        return f"\\hebyear{{{year_range}}}"

    def _replace_at_position(
        self, line: str, old: str, new: str, pos: int
    ) -> str:
        """Replace content at specific position."""
        # Try to find exactly at the given position first
        if line[pos:pos + len(old)] == old:
            return line[:pos] + new + line[pos + len(old):]
        # If not exact, search in a small window around pos
        for offset in range(0, 10):
            idx = pos + offset
            if idx + len(old) <= len(line) and line[idx:idx + len(old)] == old:
                return line[:idx] + new + line[idx + len(old):]
            idx = pos - offset
            if idx >= 0 and line[idx:idx + len(old)] == old:
                return line[:idx] + new + line[idx + len(old):]
        # Fallback to first occurrence
        idx = line.find(old)
        if idx != -1:
            return line[:idx] + new + line[idx + len(old):]
        return line

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        return {
            "number-wrap": {
                "find": r"(\d+(?:[.,]\d+)*)",
                "replace": r"\\num{\1}",
                "description": "Wrap numbers with \\num{}",
            },
            "english-wrap": {
                "find": r"\b([a-zA-Z]{2,})\b",
                "replace": r"\\en{\1}",
                "description": "Wrap English words with \\en{}",
            },
            "acronym-wrap": {
                "find": r"\b([A-Z]{2,5})\b",
                "replace": r"\\en{\1}",
                "description": "Wrap acronyms with \\en{}",
            },
        }
