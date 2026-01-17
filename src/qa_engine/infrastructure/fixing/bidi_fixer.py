r"""
BiDi fixer for Hebrew-English LaTeX.

Implements FR-501 from PRD - fixes BiDi text issues.
Uses CLS built-in commands: \en{}, \num{}, \hebyear{}, \percent{}

v1.3.0: Added color context exclusion to prevent corrupting color syntax
        - Added _is_inside_color_context() method
        - Detects tcolorbox options (colback=, colframe=, coltitle=, etc.)
        - Detects LaTeX color commands (\textcolor{}, \color{}, etc.)
        - Fixer now skips content inside color specifications
v1.2.0: Added TikZ environment exclusion to prevent corrupting TikZ code
        - Added SKIP_ENVIRONMENTS list (tikzpicture, pgfpicture, axis, etc.)
        - Added _get_tikz_lines() to track multi-line TikZ environments
        - Fixer now skips all lines inside TikZ environments
v1.1.0: Fixed double-wrapping bug - now properly detects already-wrapped content
        - Added _is_already_wrapped() method
        - Added _is_wrapped_at_position() with two detection methods
        - Added _would_double_wrap() simulation check
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue

# Regex patterns for detecting already-wrapped content
WRAPPER_PATTERNS = [
    re.compile(r"\\en\{[^}]*\}"),
    re.compile(r"\\num\{[^}]*\}"),
    re.compile(r"\\hebyear\{[^}]*\}"),
    re.compile(r"\\percent\{[^}]*\}"),
    re.compile(r"\\textenglish\{[^}]*\}"),
]

# Environments where BiDi fixes should NOT be applied
SKIP_ENVIRONMENTS = [
    "tikzpicture",
    "pgfpicture",
    "axis",
    "semilogyaxis",
    "loglogaxis",
]


class BiDiFixer(FixerInterface):
    r"""
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

        # Build a map of which lines are inside TikZ environments
        tikz_lines = self._get_tikz_lines(lines)

        # Apply fixes line by line (reverse order to preserve positions)
        for line_num in sorted(issues_by_line.keys(), reverse=True):
            if 1 <= line_num <= len(lines):
                # Skip lines inside TikZ environments
                if line_num in tikz_lines:
                    continue
                line = lines[line_num - 1]
                fixed_line = self._fix_line(line, issues_by_line[line_num])
                lines[line_num - 1] = fixed_line

        return "\n".join(lines)

    def _get_tikz_lines(self, lines: List[str]) -> set:
        """Return set of line numbers (1-based) that are inside TikZ environments."""
        tikz_lines = set()
        depth = 0
        for line_num, line in enumerate(lines, start=1):
            # Check for environment opens/closes
            for env in SKIP_ENVIRONMENTS:
                opens = len(re.findall(rf"\\begin\{{{env}\}}", line))
                closes = len(re.findall(rf"\\end\{{{env}\}}", line))
                depth += opens - closes
            depth = max(0, depth)
            if depth > 0:
                tikz_lines.add(line_num)
        return tikz_lines

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

            # Skip if content itself is already a wrapper command
            if self._is_already_wrapped(content):
                continue

            # Skip if inside color context (colback=purple!5, \textcolor{green})
            if self._is_inside_color_context(line, pos):
                continue

            # Apply appropriate fix based on rule
            fixed = self._get_fix(issue.rule, content)
            if fixed and fixed != content:
                # Double-check: don't create double-wrapping
                if self._would_double_wrap(line, content, fixed, pos):
                    continue
                line = self._replace_at_position(line, content, fixed, pos)

        return line

    def _is_already_wrapped(self, content: str) -> bool:
        """Check if content itself starts with a wrapper command."""
        wrapper_prefixes = [r"\en{", r"\num{", r"\hebyear{", r"\percent{", r"\textenglish{"]
        for prefix in wrapper_prefixes:
            if content.startswith(prefix):
                return True
        return False

    def _is_wrapped_at_position(self, line: str, content: str, pos: int) -> bool:
        """Check if content at specific position is already wrapped."""
        # Method 1: Check if there's a wrapper command right before this position
        before = line[max(0, pos - 20):pos]
        wrappers = [r"\\en\{$", r"\\num\{$", r"\\hebyear\{$", r"\\percent\{$", r"\\textenglish\{$"]
        for wrapper in wrappers:
            if re.search(wrapper, before):
                return True

        # Method 2: Check if position falls inside any wrapper on the line
        for pattern in WRAPPER_PATTERNS:
            for match in pattern.finditer(line):
                # Check if our content position is inside this wrapper
                if match.start() < pos < match.end():
                    return True
                # Also check if content ends inside wrapper
                content_end = pos + len(content)
                if match.start() < content_end <= match.end():
                    return True

        return False

    def _would_double_wrap(self, line: str, old: str, new: str, pos: int) -> bool:
        """Check if applying this fix would create double-wrapping."""
        # If the new content is already present in the line, skip
        if new in line:
            return True

        # Check for patterns like \en{\en{...}}
        double_wrap_patterns = [
            r"\\en\{\\en\{",
            r"\\num\{\\num\{",
            r"\\hebyear\{\\hebyear\{",
        ]
        # Simulate the replacement and check
        simulated = self._replace_at_position(line, old, new, pos)
        for pattern in double_wrap_patterns:
            if re.search(pattern, simulated):
                return True
        return False

    def _is_inside_color_context(self, line: str, pos: int) -> bool:
        """Check if position is inside a color specification context.

        Detects color contexts like:
        - colback=purple!5 (tcolorbox options)
        - colframe=green!60!black
        - \\textcolor{red!50}
        - \\color{blue}
        """
        # Pattern 1: tcolorbox color options (colback=, colframe=, coltitle=, etc.)
        tcolorbox_color_opts = [
            r"colback\s*=",
            r"colframe\s*=",
            r"coltitle\s*=",
            r"colbacktitle\s*=",
            r"coltext\s*=",
        ]
        for opt_pattern in tcolorbox_color_opts:
            for match in re.finditer(opt_pattern, line):
                opt_end = match.end()
                if opt_end <= pos:
                    # Find end of color spec (next , or ] or } or end of line)
                    rest = line[opt_end:]
                    spec_end = len(rest)
                    for i, char in enumerate(rest):
                        if char in ",]}\n":
                            spec_end = i
                            break
                    if pos < opt_end + spec_end:
                        return True

        # Pattern 2: LaTeX color commands (\textcolor{...}, \color{...})
        color_commands = [
            r"\\textcolor\{",
            r"\\color\{",
            r"\\definecolor\{",
            r"\\colorlet\{",
        ]
        for cmd_pattern in color_commands:
            for match in re.finditer(cmd_pattern, line):
                cmd_start = match.start()
                if cmd_start < pos:
                    # Find matching closing brace
                    depth = 1
                    i = match.end()
                    while i < len(line) and depth > 0:
                        if line[i] == "{":
                            depth += 1
                        elif line[i] == "}":
                            depth -= 1
                        i += 1
                    if pos < i:
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
