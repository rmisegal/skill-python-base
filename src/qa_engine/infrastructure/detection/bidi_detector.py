"""
BiDi (Bidirectional text) detector.

Implements FR-401 from PRD - detects BiDi issues in Hebrew-English LaTeX.
All 15 rules as specified in QA-CLAUDE-MECHANISM-ARCHITECTURE-REPORT.md.
"""

from __future__ import annotations

import re
from typing import Dict, List

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .bidi_rules import BIDI_RULES


class BiDiDetector(DetectorInterface):
    """
    Detects bidirectional text issues in Hebrew-English LaTeX.

    Implements all 15 BiDi detection rules - all regex-based, deterministic.
    """

    def __init__(self) -> None:
        self._rules = BIDI_RULES

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """
        Detect BiDi issues in content.

        Args:
            content: LaTeX content to analyze
            file_path: Source file path
            offset: Line number offset for chunked processing

        Returns:
            List of detected issues
        """
        issues: List[Issue] = []
        lines = content.split("\n")

        for rule_name, rule_def in self._rules.items():
            pattern = re.compile(rule_def["pattern"])
            context_pattern = rule_def.get("context_pattern")
            negative_pattern = rule_def.get("negative_pattern")
            exclude_pattern = rule_def.get("exclude_pattern")
            document_context = rule_def.get("document_context", False)

            # For rules with negative_pattern, check whole content first
            if negative_pattern and re.search(negative_pattern, content):
                continue

            # For document_context rules, check Hebrew exists anywhere
            if document_context and context_pattern:
                if not re.search(context_pattern, content):
                    continue

            skip_math = rule_def.get("skip_math_mode", False)
            skip_cite = rule_def.get("skip_cite_context", False)

            for line_num, line in enumerate(lines, start=1):
                if line.strip().startswith("%"):
                    continue

                # Line-level context check (skip for document_context rules)
                if context_pattern and not document_context:
                    if not re.search(context_pattern, line):
                        continue

                for match in pattern.finditer(line):
                    # Skip if inside math mode
                    if skip_math and self._is_inside_math(line, match.start()):
                        continue
                    # Skip if inside \cite{} command
                    if skip_cite and self._is_inside_cite(line, match.start()):
                        continue
                    # Check exclude_pattern - skip if match is inside a wrapper
                    if exclude_pattern:
                        # Check if match is inside a wrapper on the same line
                        if self._is_inside_wrapper(line, match.start(), exclude_pattern):
                            continue
                        # For environment wrappers, check document context
                        prefix = content[:content.find(line) + match.start()]
                        if self._has_active_wrapper(prefix, exclude_pattern):
                            continue

                    matched_text = match.group(1) if match.lastindex else match.group(0)
                    issues.append(
                        Issue(
                            rule=rule_name,
                            file=file_path,
                            line=line_num + offset,
                            content=matched_text,
                            severity=rule_def["severity"],
                            fix=self._suggest_fix(rule_name, matched_text),
                            context={"match_start": match.start()},
                        )
                    )

        return issues

    def _is_inside_cite(self, line: str, pos: int) -> bool:
        """Check if position is inside a \\cite{} command (handles nested braces)."""
        # Find all \cite commands with optional brackets
        cite_patterns = [r"\\cite\{", r"\\cite\["]
        for pattern in cite_patterns:
            for match in re.finditer(pattern, line):
                start = match.end()
                if start > pos:
                    continue
                # Count braces to find the end of the cite command
                depth = 1
                i = start
                while i < len(line) and depth > 0:
                    if line[i] == "{":
                        depth += 1
                    elif line[i] == "}":
                        depth -= 1
                    i += 1
                # If pos is between start and end, we're inside the cite
                if start <= pos < i:
                    return True
        return False

    def _is_inside_math(self, line: str, pos: int) -> bool:
        """Check if position is inside math mode ($...$, \\[...\\], etc.)."""
        # Check inline math $...$
        in_math = False
        for i, char in enumerate(line):
            if char == "$" and (i == 0 or line[i - 1] != "\\"):
                in_math = not in_math
            if i == pos:
                return in_math
        # Check display math \[...\] or equation environments
        before = line[:pos]
        if r"\[" in before and r"\]" not in before:
            return True
        return False

    def _is_inside_wrapper(self, line: str, pos: int, exclude_pattern: str) -> bool:
        """Check if position is inside a wrapper command on the same line."""
        # Split exclude_pattern by | and check each pattern
        patterns = exclude_pattern.split("|")
        for pat in patterns:
            pat = pat.strip()
            if not pat:
                continue
            # For command-style wrappers like \num{, \en{, etc.
            if pat.endswith(r"\{"):
                cmd_pattern = pat.replace(r"\{", r"\{[^}]*\}")
                for match in re.finditer(cmd_pattern, line):
                    if match.start() < pos < match.end():
                        return True
            # For math mode $...$
            elif pat.startswith(r"\$"):
                for match in re.finditer(r"\$[^$]+\$", line):
                    if match.start() < pos < match.end():
                        return True
        return False

    def _has_active_wrapper(self, prefix: str, exclude_pattern: str) -> bool:
        """Check if there's an unclosed wrapper before match position."""
        # For environment wrappers like \begin{english}
        if "begin" in exclude_pattern:
            env_name = re.search(r"begin\\{(\w+)\\}", exclude_pattern)
            if env_name:
                env = env_name.group(1)
                opens = len(re.findall(rf"\\begin\{{{env}\}}", prefix))
                closes = len(re.findall(rf"\\end\{{{env}\}}", prefix))
                return opens > closes
        return False

    def _suggest_fix(self, rule: str, content: str) -> str:
        """Suggest fix for detected issue."""
        rule_def = self._rules.get(rule, {})
        template = rule_def.get("fix_template", "")

        if "{}" in template:
            return template.format(content)
        return template

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
