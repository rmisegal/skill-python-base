"""
Table detector for RTL Hebrew-English LaTeX documents.

Implements detection of table-related issues in RTL context.
"""

from __future__ import annotations

import re
from typing import Dict, List

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .table_rules import TABLE_RULES


class TableDetector(DetectorInterface):
    """
    Detects table layout issues in Hebrew-English LaTeX.

    Implements rules for RTL table detection - all regex-based.
    """

    def __init__(self) -> None:
        self._rules = TABLE_RULES

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """Detect table issues in content."""
        issues: List[Issue] = []
        lines = content.split("\n")

        for rule_name, rule_def in self._rules.items():
            pattern = re.compile(rule_def["pattern"])
            context_pattern = rule_def.get("context_pattern")
            document_context = rule_def.get("document_context", False)
            exclude_pattern = rule_def.get("exclude_pattern")

            # Document context check
            if document_context and context_pattern:
                if not re.search(context_pattern, content):
                    continue

            for line_num, line in enumerate(lines, start=1):
                if line.strip().startswith("%"):
                    continue

                # Line context check (non-document)
                if context_pattern and not document_context:
                    if not re.search(context_pattern, line):
                        continue

                for match in pattern.finditer(line):
                    # Check exclude pattern
                    if exclude_pattern:
                        prefix = content[:content.find(line) + match.start()]
                        if self._check_exclude(prefix, exclude_pattern):
                            continue

                    matched = match.group(1) if match.lastindex else match.group(0)
                    issues.append(
                        Issue(
                            rule=rule_name,
                            file=file_path,
                            line=line_num + offset,
                            content=matched,
                            severity=rule_def["severity"],
                            fix=rule_def.get("fix_template", ""),
                            context={"match_start": match.start()},
                        )
                    )

        return issues

    def _check_exclude(self, prefix: str, exclude_pattern: str) -> bool:
        """Check if exclude pattern exists in prefix."""
        # For resizebox check - look for unclosed resizebox
        if "resizebox" in exclude_pattern:
            opens = len(re.findall(r"\\resizebox", prefix))
            closes = prefix.count("}")
            # Simplified check - if resizebox appears before, skip
            return opens > 0
        return re.search(exclude_pattern, prefix) is not None

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
