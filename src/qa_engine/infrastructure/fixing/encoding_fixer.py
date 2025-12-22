"""
Encoding fixer for code blocks.

Fixes character encoding issues that cause missing character warnings.
Aligned with qa-code-fix-encoding skill.md patterns.
"""
from __future__ import annotations
import re
from typing import Dict, List, Tuple
from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue
from .encoding_patterns import TEXT_PATTERNS, CODE_PATTERNS


class EncodingFixer(FixerInterface):
    """Fixes character encoding issues in LaTeX documents."""

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes based on issues (interface compliance)."""
        fixed, _ = self.fix_content(content, "auto")
        return fixed

    def fix_content(self, content: str, context: str = "auto") -> Tuple[str, List[Dict]]:
        """Fix encoding issues in content."""
        changes: List[Dict] = []
        if context == "auto":
            return self._fix_auto_context(content)
        patterns = CODE_PATTERNS if context == "code" else TEXT_PATTERNS
        for name, pattern_def in patterns.items():
            regex = re.compile(pattern_def["pattern"])
            matches = list(regex.finditer(content))
            replacement = pattern_def["replace"]
            for match in matches:
                changes.append({
                    "pattern": name,
                    "original": match.group(0),
                    "replacement": replacement,
                    "position": match.start(),
                })
            # Use lambda to prevent backslash interpretation in replacement
            content = regex.sub(lambda m: replacement, content)
        return content, changes

    def _fix_auto_context(self, content: str) -> Tuple[str, List[Dict]]:
        """Fix with automatic context detection."""
        changes: List[Dict] = []
        lines = content.split("\n")
        in_code = False
        result_lines = []
        for line in lines:
            if re.search(r"\\begin\{(lstlisting|minted|verbatim)", line):
                in_code = True
            if re.search(r"\\end\{(lstlisting|minted|verbatim)", line):
                in_code = False
            patterns = CODE_PATTERNS if in_code else TEXT_PATTERNS
            fixed_line = line
            for name, pattern_def in patterns.items():
                regex = re.compile(pattern_def["pattern"])
                if regex.search(fixed_line):
                    replacement = pattern_def["replace"]
                    changes.append({"pattern": name, "context": "code" if in_code else "text"})
                    fixed_line = regex.sub(lambda m, r=replacement: r, fixed_line)
            result_lines.append(fixed_line)
        return "\n".join(result_lines), changes

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return all available patterns."""
        return {"text": TEXT_PATTERNS, "code": CODE_PATTERNS}
