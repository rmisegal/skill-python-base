"""
TikZ fixer for RTL LaTeX documents.

Wraps TikZ environments in english wrapper for correct rendering.
"""

from __future__ import annotations

import re
from typing import Dict, List

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue


class TikzFixer(FixerInterface):
    """
    Fixes TikZ issues in RTL LaTeX documents.

    Wraps tikzpicture environments in english environment.
    """

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        lines = content.split("\n")

        # Process issues in reverse order to preserve line numbers
        tikz_lines = sorted(
            [i.line for i in issues if i.rule == "bidi-tikz-rtl"],
            reverse=True,
        )

        for line_num in tikz_lines:
            if 1 <= line_num <= len(lines):
                lines = self._wrap_tikz(lines, line_num)

        return "\n".join(lines)

    def _wrap_tikz(self, lines: List[str], line_num: int) -> List[str]:
        """Wrap tikzpicture in english environment."""
        start_idx = line_num - 1

        # Check if already wrapped
        if start_idx > 0:
            prev_line = lines[start_idx - 1].strip()
            if "\\begin{english}" in prev_line:
                return lines

        # Find tikzpicture end
        end_idx = None
        depth = 0
        for i in range(start_idx, len(lines)):
            if "\\begin{tikzpicture}" in lines[i]:
                depth += 1
            if "\\end{tikzpicture}" in lines[i]:
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break

        if end_idx is not None:
            # Insert wrappers
            indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
            prefix = " " * indent
            lines.insert(end_idx + 1, f"{prefix}\\end{{english}}")
            lines.insert(start_idx, f"{prefix}\\begin{{english}}")

        return lines

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return fix patterns."""
        return {
            "tikz-wrap": {
                "find": r"\\begin{tikzpicture}",
                "replace": r"\\begin{english}\n\\begin{tikzpicture}",
                "description": "Wrap TikZ in english environment",
            },
        }
