"""Code block detector. Implements FR-402 from PRD."""

from __future__ import annotations
import re
from typing import Dict, List
from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .code_rules import CODE_RULES, CODE_ENV_PATTERN, HEBREW_WRAPPERS, FIX_SUGGESTIONS


class CodeDetector(DetectorInterface):
    """Detects code block issues in LaTeX documents."""

    def __init__(self) -> None:
        self._rules = CODE_RULES

    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        """Detect code block issues."""
        issues: List[Issue] = []
        lines = content.split("\n")
        in_code, in_english, code_env = False, False, ""

        for line_num, line in enumerate(lines, start=1):
            in_english = self._track_english(line, in_english)
            in_code, code_env = self._track_code(line, in_code, code_env)

            for rule_name, rule_def in self._rules.items():
                if not self._should_check(rule_name, rule_def, line, in_code, in_english):
                    continue

                for match in re.finditer(rule_def["pattern"], line):
                    if rule_name == "code-direction-hebrew":
                        if self._is_wrapped(line, match.start()):
                            continue
                    issues.append(self._create_issue(
                        rule_name, rule_def, file_path, line_num + offset,
                        match.group(0)[:50], in_code, code_env
                    ))
        return issues

    def _track_english(self, line: str, in_english: bool) -> bool:
        if "\\begin{english}" in line:
            return True
        if "\\end{english}" in line:
            return False
        return in_english

    def _track_code(self, line: str, in_code: bool, code_env: str) -> tuple:
        begin = re.search(r"\\begin\{" + CODE_ENV_PATTERN + r"\}", line)
        if begin:
            return True, begin.group(1)
        if re.search(r"\\end\{" + CODE_ENV_PATTERN + r"\}", line):
            return False, ""
        return in_code, code_env

    def _should_check(self, rule: str, rule_def: dict, line: str,
                      in_code: bool, in_english: bool) -> bool:
        if rule_def.get("in_code_block") and not in_code:
            return False
        if rule_def.get("outside_code_block") and in_code:
            return False
        if rule == "code-background-overflow" and in_english:
            return False
        if rule == "code-direction-hebrew":
            if "\\begin{" in line:
                return False
            if any(w in line for w in HEBREW_WRAPPERS) and re.search(r"[א-ת]", line):
                return False
        return True

    def _is_wrapped(self, line: str, pos: int) -> bool:
        before = line[:pos]
        for wrapper in HEBREW_WRAPPERS:
            wp = before.rfind("\\" + wrapper)
            if wp != -1:
                after = before[wp:]
                if after.count("{") > after.count("}"):
                    return True
        return False

    def _create_issue(self, rule: str, rule_def: dict, file: str,
                      line: int, content: str, in_code: bool, env: str) -> Issue:
        return Issue(
            rule=rule, file=file, line=line, content=content,
            severity=rule_def["severity"], fix=FIX_SUGGESTIONS.get(rule, ""),
            context={"in_code_block": in_code, "code_env": env or "pythonbox"}
        )

    def get_rules(self) -> Dict[str, str]:
        return {n: r["description"] for n, r in self._rules.items()}
