"""
Typeset issue detector.

Implements FR-403 from PRD - parses LaTeX logs for typeset warnings.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue, Severity


class TypesetDetector(DetectorInterface):
    """
    Detects typeset issues from LaTeX log files.

    Parses .log files for warnings about:
    - Overfull/Underfull hbox
    - Overfull/Underfull vbox
    - Undefined references
    - Undefined citations
    - Float too large
    """

    def __init__(self) -> None:
        self._rules = self._build_rules()

    def _build_rules(self) -> Dict[str, Dict]:
        """Build rule definitions for log parsing."""
        return {
            "typeset-overfull-hbox": {
                "description": "Overfull horizontal box",
                "pattern": r"Overfull \\hbox \((\d+\.?\d*)pt too wide\)",
                "severity": Severity.WARNING,
            },
            "typeset-underfull-hbox": {
                "description": "Underfull horizontal box",
                "pattern": r"Underfull \\hbox \(badness (\d+)\)",
                "severity": Severity.INFO,
            },
            "typeset-overfull-vbox": {
                "description": "Overfull vertical box",
                "pattern": r"Overfull \\vbox \((\d+\.?\d*)pt too high\)",
                "severity": Severity.WARNING,
            },
            "typeset-underfull-vbox": {
                "description": "Underfull vertical box",
                "pattern": r"Underfull \\vbox \(badness (\d+)\)",
                "severity": Severity.INFO,
            },
            "typeset-undefined-ref": {
                "description": "Undefined reference",
                "pattern": r"Reference `([^']+)' on page \d+ undefined",
                "severity": Severity.CRITICAL,
            },
            "typeset-undefined-citation": {
                "description": "Undefined citation",
                "pattern": r"Citation `([^']+)' on page \d+ undefined",
                "severity": Severity.CRITICAL,
            },
            "typeset-float-too-large": {
                "description": "Float too large for page",
                "pattern": r"Float too large for page(?: by (\d+\.?\d*)pt)?",
                "severity": Severity.WARNING,
            },
        }

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """
        Detect typeset issues in log content.

        Args:
            content: Log file content to analyze
            file_path: Source file path (log file)
            offset: Line number offset

        Returns:
            List of detected issues
        """
        issues: List[Issue] = []
        lines = content.split("\n")
        current_file = file_path

        for line_num, line in enumerate(lines, start=1):
            # Track file context from log output
            file_match = re.search(r"\(([^()]+\.tex)", line)
            if file_match:
                current_file = file_match.group(1)

            for rule_name, rule_def in self._rules.items():
                pattern = re.compile(rule_def["pattern"])
                match = pattern.search(line)

                if match:
                    ctx = {"log_line": line_num}
                    if rule_name == "typeset-float-too-large" and match.groups():
                        overflow = match.group(1)
                        if overflow:
                            ctx["overflow_pt"] = float(overflow)
                    issues.append(
                        Issue(
                            rule=rule_name,
                            file=current_file,
                            line=self._extract_line_number(line, line_num + offset),
                            content=match.group(0),
                            severity=rule_def["severity"],
                            fix=self._suggest_fix(rule_name, match),
                            context=ctx,
                        )
                    )

        return issues

    def _extract_line_number(self, line: str, default: int) -> int:
        """Extract line number from log message if available."""
        match = re.search(r"line (\d+)", line)
        if match:
            return int(match.group(1))
        match = re.search(r"on input line (\d+)", line)
        if match:
            return int(match.group(1))
        return default

    def _suggest_fix(self, rule: str, match: re.Match) -> str:
        """Suggest fix based on rule and match."""
        if rule == "typeset-overfull-hbox":
            return "Reduce content width or use \\resizebox"
        elif rule == "typeset-underfull-hbox":
            return "Add content or use \\hfill"
        elif rule == "typeset-undefined-ref":
            ref = match.group(1) if match.groups() else ""
            return f"Define label '{ref}' or fix reference"
        elif rule == "typeset-undefined-citation":
            cite = match.group(1) if match.groups() else ""
            return f"Add citation '{cite}' to bibliography"
        elif rule == "typeset-float-too-large":
            overflow = float(match.group(1)) if match.groups() and match.group(1) else 0
            if overflow > 100:
                return "Split content or use smaller font (large overflow)"
            elif overflow > 50:
                return "Use smaller font or add breakable option"
            return "Use [p] placement or scale content"
        return ""

    def detect_from_log(self, log_path: str | Path) -> List[Issue]:
        """
        Convenience method to detect from log file path.

        Args:
            log_path: Path to .log file

        Returns:
            List of detected issues
        """
        path = Path(log_path)
        if not path.exists():
            return []

        content = path.read_text(encoding="utf-8", errors="ignore")
        return self.detect(content, str(log_path))

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
