"""
TOC configuration detector.

Detects TOC-related BiDi issues in CLS files.
Detection is Python-backed; fixing remains LLM-only.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .toc_rules import TOC_COUNTER_RULES, L_AT_BLOCK_RULES


class TOCDetector(DetectorInterface):
    """Detects TOC configuration issues in CLS files."""

    def __init__(self) -> None:
        self._counter_rules = TOC_COUNTER_RULES
        self._block_rules = L_AT_BLOCK_RULES

    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        """Detect TOC configuration issues in CLS content."""
        if not file_path.endswith(".cls"):
            return []
        issues = self._detect_counter_issues(content, file_path, offset)
        issues.extend(self._detect_l_at_issues(content, file_path, offset))
        return issues

    def _detect_counter_issues(
        self, content: str, file_path: str, offset: int
    ) -> List[Issue]:
        """Detect counter-related issues (file-wide patterns)."""
        issues: List[Issue] = []
        lines = content.split("\n")

        for rule_name, rule_def in self._counter_rules.items():
            if not re.search(rule_def["pattern"], content):
                continue
            neg = rule_def.get("negative_pattern")
            if neg and re.search(neg, content):
                continue
            for ln, line in enumerate(lines, start=1):
                if re.search(rule_def["pattern"], line):
                    issues.append(self._make_issue(rule_name, file_path, ln + offset,
                                                   line.strip()[:60], rule_def))
                    if neg:  # Only one issue per negative-pattern rule
                        break
        return issues

    def _detect_l_at_issues(
        self, content: str, file_path: str, offset: int
    ) -> List[Issue]:
        """Detect l@ command issues (block-aware detection)."""
        issues: List[Issue] = []
        lines = content.split("\n")

        for rule_name, rule_def in self._block_rules.items():
            for ln, line in enumerate(lines, start=1):
                if not re.search(rule_def["start_pattern"], line):
                    continue
                block = self._extract_block(lines, ln - 1)
                if not re.search(rule_def["rtl_check"], block):
                    issues.append(self._make_issue(
                        rule_name, file_path, ln + offset,
                        f"\\{rule_def['command']} without RTL", rule_def))
        return issues

    def _extract_block(self, lines: List[str], start_idx: int) -> str:
        """Extract command block from start line to balanced braces."""
        block, brace_count, started = [], 0, False
        for i in range(start_idx, min(start_idx + 25, len(lines))):
            block.append(lines[i])
            for c in lines[i]:
                if c == "{":
                    brace_count += 1
                    started = True
                elif c == "}":
                    brace_count -= 1
            if started and brace_count <= 0:
                break
        return "\n".join(block)

    def _make_issue(self, rule: str, fp: str, ln: int, ct: str, rd: dict) -> Issue:
        """Create an Issue object."""
        return Issue(rule=rule, file=fp, line=ln, content=ct,
                     severity=rd["severity"], fix=rd.get("fix_template", ""))

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        r = {n: d["description"] for n, d in self._counter_rules.items()}
        r.update({n: d["description"] for n, d in self._block_rules.items()})
        return r

    def detect_in_cls_file(self, cls_path: str) -> List[Issue]:
        """Convenience method to detect issues in a CLS file."""
        path = Path(cls_path)
        if not path.exists():
            return []
        return self.detect(path.read_text(encoding="utf-8", errors="replace"), str(path))
