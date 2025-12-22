"""
Subfiles detector for LaTeX documents.

Detects issues related to subfiles package usage for modular documents.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .subfiles_rules import SUBFILES_RULES


class SubfilesDetector(DetectorInterface):
    """
    Detects subfiles-related issues in LaTeX documents.

    Checks for proper subfiles setup for modular document compilation.
    """

    def __init__(self) -> None:
        self._rules = SUBFILES_RULES

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """Detect subfiles issues in content."""
        issues: List[Issue] = []
        lines = content.split("\n")
        filename = Path(file_path).stem.lower()

        for rule_name, rule_def in self._rules.items():
            pattern = re.compile(rule_def["pattern"])
            file_pattern = rule_def.get("file_pattern")
            negative_pattern = rule_def.get("negative_pattern")

            # File pattern check - only apply to matching files
            if file_pattern and not re.search(file_pattern, filename):
                continue

            # Negative pattern check
            if negative_pattern and re.search(negative_pattern, content):
                continue

            for line_num, line in enumerate(lines, start=1):
                if line.strip().startswith("%"):
                    continue

                for match in pattern.finditer(line):
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

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
