"""Direction fixer for Hebrew text in code blocks."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue
from .direction_patterns import (
    CODE_ENVIRONMENTS, HEBREW_PATTERN, DirectionFix, DirectionFixResult,
    WRAPPER_COMMANDS, DEFAULT_WRAPPER,
)


class DirectionFixer(FixerInterface):
    """Fixes Hebrew text direction in code blocks by wrapping with texthebrew."""

    def __init__(self, wrapper: str = DEFAULT_WRAPPER) -> None:
        self._wrapper = wrapper
        self._wrapper_cmd = WRAPPER_COMMANDS.get(wrapper, WRAPPER_COMMANDS[DEFAULT_WRAPPER])
        self._hebrew_re = re.compile(HEBREW_PATTERN)

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes based on provided issues (interface compliance)."""
        for issue in issues:
            if "direction" in issue.rule.lower() or "hebrew" in issue.rule.lower():
                content, _ = self.fix_content(content, issue.file)
        return content

    def fix_content(self, content: str, file_path: str = "") -> tuple[str, DirectionFixResult]:
        """Fix Hebrew text direction in code blocks."""
        result = DirectionFixResult()
        lines = content.split("\n")
        fixed_lines = []
        in_code = False
        code_env = ""

        for line_num, line in enumerate(lines, start=1):
            # Track code environment state
            code_env, in_code = self._update_code_state(line, code_env, in_code)

            if in_code and self._hebrew_re.search(line):
                fixed_line, fixes = self._fix_line(line, line_num, file_path)
                fixed_lines.append(fixed_line)
                result.fixes.extend(fixes)
                result.fixes_applied += len(fixes)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines), result

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        return {
            "hebrew-in-code": {
                "find": HEBREW_PATTERN,
                "replace": self._wrapper_cmd % "...",
                "description": f"Wrap Hebrew text with \\{self._wrapper}{{}}",
            }
        }

    def _update_code_state(self, line: str, env: str, in_code: bool) -> tuple[str, bool]:
        """Update code environment tracking state."""
        for code_env in CODE_ENVIRONMENTS:
            if f"\\begin{{{code_env}}}" in line or f"\\begin{{{code_env}}}[" in line:
                return code_env, True
            if f"\\end{{{code_env}}}" in line:
                return "", False
        return env, in_code

    def _fix_line(self, line: str, line_num: int, file_path: str) -> tuple[str, List[DirectionFix]]:
        """Fix Hebrew text in a single line."""
        fixes: List[DirectionFix] = []

        # Skip if already wrapped
        if "\\texthebrew{" in line or "\\he{" in line:
            return line, fixes

        def replace_hebrew(match: re.Match) -> str:
            hebrew_text = match.group(0)
            # Check if already inside a wrapper
            before = line[:match.start()]
            if before.rstrip().endswith("{") and ("\\texthebrew" in before or "\\he" in before):
                return hebrew_text

            fixes.append(DirectionFix(
                file=file_path,
                line=line_num,
                original=hebrew_text,
                replacement=self._wrapper_cmd % hebrew_text,
                pattern_id="hebrew-in-code",
            ))
            return self._wrapper_cmd % hebrew_text

        fixed_line = self._hebrew_re.sub(replace_hebrew, line)
        return fixed_line, fixes

    def fix_with_wrapper(self, content: str, wrapper: str = "texthebrew",
                         file_path: str = "") -> tuple[str, DirectionFixResult]:
        """Fix using specific wrapper command."""
        old_wrapper = self._wrapper
        old_cmd = self._wrapper_cmd
        self._wrapper = wrapper
        self._wrapper_cmd = WRAPPER_COMMANDS.get(wrapper, WRAPPER_COMMANDS[DEFAULT_WRAPPER])

        result = self.fix_content(content, file_path)

        self._wrapper = old_wrapper
        self._wrapper_cmd = old_cmd
        return result
