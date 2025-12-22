"""TikZ overflow fixer - fixes TikZ diagrams that overflow text width."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue
from .tikz_overflow_patterns import (
    TIKZ_OVERFLOW_PATTERNS, FIX_STRATEGY, TikzOverflowFix, TikzOverflowFixResult
)


class TikzOverflowFixer(FixerInterface):
    """Fixes TikZ diagrams that overflow text width with deterministic patterns."""

    def __init__(self, strategy: str = "resizebox") -> None:
        self._patterns = TIKZ_OVERFLOW_PATTERNS
        self._strategy = strategy

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        for issue in issues:
            if "tikz" in issue.rule.lower():
                content = self._apply_fix(content, issue)
        return content

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        return {name: {"find": p["find"], "replace": p["replace"],
                       "description": p["description"]} for name, p in self._patterns.items()}

    def fix_content(self, content: str, file_path: str = "",
                    issue_type: str = "no_width_constraint") -> tuple[str, TikzOverflowFixResult]:
        """Fix TikZ overflow issues in content."""
        result = TikzOverflowFixResult()
        strategies = FIX_STRATEGY.get(issue_type, ["wrap-resizebox"])
        pattern_id = self._select_pattern(strategies)
        content, applied = self._apply_pattern(content, pattern_id, file_path)
        if applied:
            result.fixes_applied += 1
            result.fixes.append(applied)
        return content, result

    def fix_with_resizebox(self, content: str, file_path: str = "") -> tuple[str, TikzOverflowFixResult]:
        """Fix using resizebox wrapper (preferred method)."""
        result = TikzOverflowFixResult()
        pattern = r"([ \t]*)(\\begin\{tikzpicture\}(?:\[[^\]]*\])?)"

        for match in re.finditer(pattern, content):
            prefix = content[max(0, match.start() - 50):match.start()]
            if "\\resizebox" in prefix or "\\begin{adjustbox}" in prefix:
                continue
            end_pos = self._find_tikz_end_pos(content, match.end())
            if end_pos < 0:
                continue

            indent, tikz_start = match.group(1), match.group(2)
            new_start = f"{indent}\\resizebox{{\\textwidth}}{{!}}{{%\n{indent}{tikz_start}"
            end_line = content[end_pos:].split('\n')[0]
            new_end = f"{indent}\\end{{tikzpicture}}%\n{indent}}}"

            content = content[:end_pos] + new_end + content[end_pos + len(end_line):]
            content = content[:match.start()] + new_start + content[match.end():]

            result.fixes_applied += 1
            result.fixes.append(TikzOverflowFix(
                file=file_path, line=content[:match.start()].count('\n') + 1,
                pattern_id="wrap-resizebox", description="Wrapped tikzpicture in resizebox"))
            break
        return content, result

    def fix_with_scale(self, content: str, scale: float = 0.8) -> tuple[str, TikzOverflowFixResult]:
        """Fix by adding scale option."""
        result = TikzOverflowFixResult()
        pat1, rep1 = r"\\begin\{tikzpicture\}(?!\[)", f"\\\\begin{{tikzpicture}}[scale={scale}]"
        pat2 = r"\\begin\{tikzpicture\}\[([^\]]*)\]"

        if re.search(pat1, content):
            content = re.sub(pat1, rep1, content, count=1)
            result.fixes_applied += 1
            result.fixes.append(TikzOverflowFix(
                file="", line=0, pattern_id="add-scale", description=f"Added scale={scale} option"))
        elif (m := re.search(pat2, content)) and "scale" not in m.group(1):
            rep2 = f"\\\\begin{{tikzpicture}}[{m.group(1)}, scale={scale}]"
            content = re.sub(pat2, rep2, content, count=1)
            result.fixes_applied += 1
            result.fixes.append(TikzOverflowFix(
                file="", line=0, pattern_id="add-scale-options",
                description=f"Added scale={scale} to existing options"))
        return content, result

    def _apply_fix(self, content: str, issue: Issue) -> str:
        """Apply fix based on issue and strategy."""
        if self._strategy == "scale":
            return self.fix_with_scale(content)[0]
        return self.fix_with_resizebox(content, issue.file)[0]

    def _select_pattern(self, strategies: List[str]) -> str:
        """Select pattern based on strategy preference."""
        if self._strategy == "resizebox" and "wrap-resizebox" in strategies:
            return "wrap-resizebox"
        if self._strategy == "scale" and "add-scale" in strategies:
            return "add-scale"
        return strategies[0] if strategies else "wrap-resizebox"

    def _apply_pattern(self, content: str, pattern_id: str,
                       file_path: str) -> tuple[str, Optional[TikzOverflowFix]]:
        """Apply a specific pattern."""
        if pattern_id in ("wrap-resizebox", "wrap-resizebox-options"):
            fixed, res = self.fix_with_resizebox(content, file_path)
            return fixed, res.fixes[0] if res.fixes else None
        if pattern_id in ("add-scale", "add-scale-options"):
            fixed, res = self.fix_with_scale(content)
            return fixed, res.fixes[0] if res.fixes else None
        return content, None

    def _find_tikz_end_pos(self, content: str, start_pos: int) -> int:
        """Find position of matching \\end{tikzpicture}. Returns -1 if not found."""
        depth, pos = 1, start_pos
        while pos < len(content) and depth > 0:
            begin = re.search(r"\\begin\{tikzpicture\}", content[pos:])
            end = re.search(r"\\end\{tikzpicture\}", content[pos:])
            if not end:
                return -1
            if begin and begin.start() < end.start():
                depth += 1
                pos += begin.end()
            else:
                depth -= 1
                if depth == 0:
                    # Find start of line containing \end{tikzpicture}
                    end_abs = pos + end.start()
                    line_start = content.rfind('\n', 0, end_abs) + 1
                    return line_start
                pos += end.end()
        return -1
