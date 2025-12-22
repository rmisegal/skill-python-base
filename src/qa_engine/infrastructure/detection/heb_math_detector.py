"""Hebrew math detector for LaTeX documents."""
from __future__ import annotations
import re
from typing import Dict, List
from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .heb_math_rules import HEB_MATH_RULES, HEBREW_RANGE


class HebMathDetector(DetectorInterface):
    """Detects Hebrew text in math mode rendering incorrectly."""

    def __init__(self) -> None:
        self._rules = HEB_MATH_RULES

    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        """Detect Hebrew-in-math issues."""
        issues: List[Issue] = []
        lines = content.split("\n")
        in_math, in_cases = False, False
        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("%"):
                continue
            in_math, in_cases = self._update_context(line, in_math, in_cases)
            for rule_name, rule_def in self._rules.items():
                if rule_def.get("math_context"):
                    if not in_math and not self._has_inline_math(line):
                        continue
                if rule_def.get("cases_context") and not in_cases:
                    continue
                if rule_name == "heb-math-definition":
                    issues.extend(self._check_definition(line, line_num, file_path, offset))
                    continue
                pattern = re.compile(rule_def["pattern"])
                for match in pattern.finditer(line):
                    if rule_def.get("math_context") and not self._is_in_math_at(line, match.start()):
                        continue
                    matched = match.group(1) if match.lastindex else match.group(0)
                    issues.append(Issue(
                        rule=rule_name, file=file_path, line=line_num + offset,
                        content=matched, severity=rule_def["severity"],
                        fix=self._suggest_fix(rule_name, matched),
                        context={"in_math": in_math, "in_cases": in_cases},
                    ))
        return issues

    def _has_inline_math(self, line: str) -> bool:
        """Check if line contains inline math $...$."""
        return "$" in line and line.count("$") >= 2

    def _is_in_math_at(self, line: str, pos: int) -> bool:
        """Check if position is inside math mode."""
        in_math = False
        for i, char in enumerate(line):
            if char == "$" and (i == 0 or line[i - 1] != "\\"):
                in_math = not in_math
            if i == pos:
                return in_math
        return in_math

    def _update_context(self, line: str, in_math: bool, in_cases: bool) -> tuple:
        """Update math/cases context based on line content."""
        if r"\begin{cases}" in line or r"\begin{dcases}" in line:
            in_cases = True
        if r"\end{cases}" in line or r"\end{dcases}" in line:
            in_cases = False
        if r"\begin{equation" in line or r"\begin{align" in line or r"\[" in line:
            in_math = True
        if r"\end{equation" in line or r"\end{align" in line or r"\]" in line:
            in_math = False
        dollar_count = line.count("$") - line.count(r"\$")
        if dollar_count % 2 == 1:
            in_math = not in_math
        return in_math, in_cases

    def _check_definition(self, line: str, line_num: int, file_path: str, offset: int) -> List[Issue]:
        """Check for incorrect \\hebmath definition."""
        issues = []
        pattern = re.compile(r"\\newcommand\{\\hebmath\}")
        if pattern.search(line):
            if "textdir" not in line or "TRT" not in line:
                issues.append(Issue(
                    rule="heb-math-definition", file=file_path, line=line_num + offset,
                    content=line.strip()[:80], severity=self._rules["heb-math-definition"]["severity"],
                    fix="Add \\textdir TRT: \\newcommand{\\hebmath}[1]{\\text{\\begingroup\\selectlanguage{hebrew}\\textdir TRT #1\\endgroup}}",
                    context={"missing": "textdir TRT"},
                ))
        return issues

    def _suggest_fix(self, rule: str, content: str) -> str:
        """Suggest fix for detected issue."""
        template = self._rules.get(rule, {}).get("fix_template", "")
        if "{}" in template:
            return template.format(content, content)
        return template

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
