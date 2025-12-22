"""
Coverpage detector for source-level validation.

Implements FR-405 from PRD - detects cover page metadata issues.
PDF-level validation requires LLM (qa-coverpage skill).
"""

from __future__ import annotations

import re
from typing import Dict, List

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .coverpage_rules import COVERPAGE_RULES


class CoverpageDetector(DetectorInterface):
    """
    Detects cover page issues at source level.

    Source-level detection (Python):
    - Hebrew metadata BiDi issues
    - Unwrapped English/numbers in Hebrew commands
    - Date format validation
    - Acronym detection

    PDF-level validation (LLM only):
    - Rendered text direction
    - Visual layout
    - Image positioning
    """

    def __init__(self) -> None:
        self._rules = COVERPAGE_RULES

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """
        Detect cover page issues in source.

        Args:
            content: LaTeX content to analyze
            file_path: Source file path
            offset: Line number offset

        Returns:
            List of detected issues
        """
        issues: List[Issue] = []
        lines = content.split("\n")

        # Only scan preamble and first 100 lines (cover page area)
        scan_lines = lines[:100]

        for line_num, line in enumerate(scan_lines, start=1):
            if line.strip().startswith("%"):
                continue

            for rule_name, rule_def in self._rules.items():
                pattern = re.compile(rule_def["pattern"])
                matches = pattern.finditer(line)

                for match in matches:
                    # Check exclude pattern
                    if self._should_exclude(line, match, rule_def):
                        continue

                    # Check context pattern
                    if not self._has_context(line, rule_def):
                        continue

                    # Validate format if required
                    if not self._validate_format(match, rule_def):
                        issues.append(self._create_issue(
                            rule_name, rule_def, match, file_path,
                            line_num + offset
                        ))
                        continue

                    # Check content for BiDi issues
                    if rule_def.get("check_content"):
                        if self._has_bidi_issue(match):
                            issues.append(self._create_issue(
                                rule_name, rule_def, match, file_path,
                                line_num + offset
                            ))

        return issues

    def _should_exclude(
        self, line: str, match: re.Match, rule_def: Dict
    ) -> bool:
        """Check if match should be excluded."""
        exclude = rule_def.get("exclude_pattern")
        if not exclude:
            return False
        # Check if excluded wrapper exists around match
        before = line[:match.start()]
        return bool(re.search(exclude, before))

    def _has_context(self, line: str, rule_def: Dict) -> bool:
        """Check if required context exists."""
        context = rule_def.get("context_pattern")
        if not context:
            return True
        return bool(re.search(context, line, re.IGNORECASE))

    def _validate_format(self, match: re.Match, rule_def: Dict) -> bool:
        """Validate content format if required."""
        format_pattern = rule_def.get("validate_format")
        if not format_pattern:
            return True
        content = match.group(1) if match.lastindex else match.group(0)
        return bool(re.fullmatch(format_pattern, content.strip()))

    def _has_bidi_issue(self, match: re.Match) -> bool:
        """Check if matched content has BiDi issues."""
        content = match.group(1) if match.lastindex else match.group(0)
        # Check for unwrapped English (3+ chars)
        if re.search(r"(?<!\\en\{)[a-zA-Z]{3,}", content):
            return True
        # Check for unwrapped numbers
        if re.search(r"(?<!\\en\{)(?<!\\num\{)\d+[.,]?\d*", content):
            return True
        return False

    def _create_issue(
        self,
        rule_name: str,
        rule_def: Dict,
        match: re.Match,
        file_path: str,
        line_num: int,
    ) -> Issue:
        """Create issue from match."""
        content = match.group(1) if match.lastindex else match.group(0)
        return Issue(
            rule=rule_name,
            file=file_path,
            line=line_num,
            content=content[:50],
            severity=rule_def["severity"],
            fix=self._suggest_fix(rule_name, content),
            context={"full_match": match.group(0)[:80]},
        )

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
