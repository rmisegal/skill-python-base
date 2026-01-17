"""
Table fixer for Hebrew RTL LaTeX.

Implements fixes for table issues in RTL context.

v1.1.0: Fixed triple RTL wrapper bug - now checks for existing wrappers
        before adding new ones.
"""

from __future__ import annotations

import re
from typing import Dict, List

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue


class TableFixer(FixerInterface):
    """
    Fixes table issues in Hebrew RTL LaTeX documents.

    Applies fixes for:
    - Plain unstyled tables (convert to rtltabular)
    - Tables without RTL environment
    - Wide tables without resizebox
    """

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        lines = content.split("\n")

        # Group issues by type and line
        for issue in sorted(issues, key=lambda i: i.line, reverse=True):
            line_num = issue.line
            if not (1 <= line_num <= len(lines)):
                continue

            if issue.rule == "table-plain-unstyled":
                lines = self._fix_plain_table(lines, line_num)
            elif issue.rule == "table-no-rtl-env":
                lines = self._fix_no_rtl_env(lines, line_num)
            elif issue.rule == "table-overflow":
                lines = self._fix_overflow(lines, line_num)
            elif issue.rule == "table-cell-hebrew":
                lines[line_num - 1] = self._fix_cell_hebrew(
                    lines[line_num - 1], issue.content
                )

        return "\n".join(lines)

    def _fix_plain_table(self, lines: List[str], line_num: int) -> List[str]:
        """Convert plain tabular to rtltabular with styling."""
        line = lines[line_num - 1]
        # Replace tabular with rtltabular
        if "\\begin{tabular}" in line:
            line = line.replace("\\begin{tabular}", "\\begin{rtltabular}")
            lines[line_num - 1] = line
            # Find and fix the end
            for i in range(line_num, len(lines)):
                if "\\end{tabular}" in lines[i]:
                    lines[i] = lines[i].replace(
                        "\\end{tabular}", "\\end{rtltabular}"
                    )
                    break
        return lines

    def _fix_no_rtl_env(self, lines: List[str], line_num: int) -> List[str]:
        """Wrap table in RTL environment."""
        # Find table start
        start_idx = line_num - 1
        end_idx = None

        # Find table end
        for i in range(start_idx, len(lines)):
            if "\\end{table}" in lines[i]:
                end_idx = i
                break

        if end_idx is not None:
            # Check if already wrapped in RTL environment
            if self._is_already_rtl_wrapped(lines, start_idx, end_idx):
                return lines

            # Insert RTL wrapper
            lines.insert(end_idx + 1, "\\end{RTL}")
            lines.insert(start_idx, "\\begin{RTL}")

        return lines

    def _is_already_rtl_wrapped(
        self, lines: List[str], start_idx: int, end_idx: int
    ) -> bool:
        """Check if table region is already wrapped in RTL environment.

        Checks for:
        - \\begin{RTL} ... \\end{RTL}
        - \\begin{hebrew} ... \\end{hebrew}
        - \\begin{english} ... \\end{english} (for LTR tables in RTL doc)
        """
        rtl_envs = ["RTL", "hebrew", "english"]

        # Check lines before start_idx for unclosed RTL begin
        rtl_depth = {}
        for env in rtl_envs:
            rtl_depth[env] = 0

        # Scan from document start to table start
        for i in range(0, start_idx):
            line = lines[i]
            for env in rtl_envs:
                opens = len(re.findall(rf"\\begin\{{{env}\}}", line))
                closes = len(re.findall(rf"\\end\{{{env}\}}", line))
                rtl_depth[env] += opens - closes

        # If any RTL environment is open at table start, we're already wrapped
        for env, depth in rtl_depth.items():
            if depth > 0:
                return True

        # Also check if table is immediately preceded by RTL begin
        if start_idx > 0:
            prev_line = lines[start_idx - 1].strip()
            for env in rtl_envs:
                if f"\\begin{{{env}}}" in prev_line:
                    return True

        return False

    def _fix_overflow(self, lines: List[str], line_num: int) -> List[str]:
        """Wrap wide table in resizebox."""
        line = lines[line_num - 1]
        if "\\begin{tabular}" in line or "\\begin{rtltabular}" in line:
            # Add resizebox before
            indent = len(line) - len(line.lstrip())
            prefix = " " * indent
            lines[line_num - 1] = (
                f"{prefix}\\resizebox{{\\textwidth}}{{!}}{{\n{line}"
            )
            # Find end and close resizebox
            env = "rtltabular" if "rtltabular" in line else "tabular"
            for i in range(line_num, len(lines)):
                if f"\\end{{{env}}}" in lines[i]:
                    lines[i] = lines[i] + "\n}"
                    break
        return lines

    def _fix_cell_hebrew(self, line: str, content: str) -> str:
        """Wrap Hebrew cell content properly."""
        if content and content in line:
            # Check if not already wrapped
            if f"\\texthebrew{{{content}}}" not in line:
                line = line.replace(content, f"\\texthebrew{{{content}}}")
        return line

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return fix patterns."""
        return {
            "rtl-tabular": {
                "find": r"\\begin{tabular}",
                "replace": r"\\begin{rtltabular}",
                "description": "Convert to RTL-aware tabular",
            },
        }
