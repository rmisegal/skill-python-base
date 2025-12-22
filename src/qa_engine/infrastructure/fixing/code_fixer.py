"""
Code block fixer.

Implements FR-502 from PRD - fixes code block issues.
"""

from __future__ import annotations

import re
from typing import Dict, List

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue


class CodeFixer(FixerInterface):
    """
    Fixes code block issues in LaTeX documents.

    Applies fixes for:
    - Background overflow (adds english wrapper)
    - Emoji characters (removes or replaces)
    """

    def __init__(self) -> None:
        self._patterns = self._build_patterns()

    def _build_patterns(self) -> Dict[str, Dict[str, str]]:
        """Build fix patterns."""
        return {
            "english-wrapper": {
                "find": r"(\\begin\{pythonbox\})",
                "replace": r"\\begin{english}\n\1",
                "description": "Wrap code block in english environment",
            },
            "english-wrapper-end": {
                "find": r"(\\end\{pythonbox\})",
                "replace": r"\1\n\\end{english}",
                "description": "Close english environment after code block",
            },
        }

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        lines = content.split("\n")
        needs_wrap: Dict[int, str] = {}
        hebrew_lines: set = set()

        for issue in issues:
            if issue.rule in ("code-background-overflow", "code-direction-hebrew"):
                line_num = issue.line
                if 1 <= line_num <= len(lines):
                    code_env = issue.context.get("code_env", "pythonbox")
                    start_line = self._find_env_start(lines, line_num - 1, code_env)
                    if start_line is not None:
                        needs_wrap[start_line + 1] = code_env
            elif issue.rule == "code-hebrew-content":
                hebrew_lines.add(issue.line)

        # Fix Hebrew content in code (replace with placeholders)
        for line_num in hebrew_lines:
            if 1 <= line_num <= len(lines):
                lines[line_num - 1] = self._fix_hebrew_in_code(lines[line_num - 1])

        # Apply wrapping fixes (process in reverse)
        for line_num in sorted(needs_wrap.keys(), reverse=True):
            env_name = needs_wrap[line_num]
            end_line = self._find_env_end(lines, line_num - 1, env_name)
            if end_line:
                lines.insert(end_line, "\\end{english}")
                lines.insert(line_num - 1, "\\begin{english}")

        return "\n".join(lines)

    def _fix_hebrew_in_code(self, line: str) -> str:
        """Replace Hebrew text in code line with English placeholder."""
        hebrew = re.compile(r'[\u0590-\u05FF]+')
        # Handle comments
        if '#' in line:
            parts = line.split('#', 1)
            if hebrew.search(parts[1]):
                return parts[0] + '# [TODO: translate Hebrew comment]'
        # Handle strings with Hebrew
        if hebrew.search(line):
            line = hebrew.sub('[HEB]', line)
        return line

    def _find_env_start(
        self,
        lines: List[str],
        line_idx: int,
        env_name: str,
    ) -> int | None:
        """Find the line index of environment start, searching backwards."""
        start_pattern = re.compile(rf"\\begin\{{({env_name}|lstlisting|minted|verbatim|pythonbox\*?|tcolorbox|tcblisting)\}}")
        for i in range(line_idx, -1, -1):
            if start_pattern.search(lines[i]):
                return i
        return None

    def _find_env_end(
        self,
        lines: List[str],
        start_idx: int,
        env_name: str,
    ) -> int | None:
        """Find the line index of environment end."""
        end_pattern = re.compile(rf"\\end\{{({env_name}|lstlisting|minted|verbatim|pythonbox\*?|tcolorbox|tcblisting)\}}")
        for i in range(start_idx, len(lines)):
            if end_pattern.search(lines[i]):
                return i + 1  # Return 1-indexed position after end
        return None

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        return self._patterns
