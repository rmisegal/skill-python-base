"""
Table overflow detector for LaTeX documents.

Detects wide tables without resizebox wrapper that may cause overfull hbox.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from .table_models import TableOverflowIssue, OverflowDetectResult


class TableOverflowDetector:
    """
    Detects tables that may overflow text width.

    Aligned with qa-table-overflow-detect skill.md:
    - Step 1: Find table environments
    - Step 2: Check for resizebox wrapper
    - Step 3: Count columns
    """

    # Table environment patterns - handle nested braces in column spec (e.g., p{2cm})
    # Pattern: {(?:[^{}]|{[^{}]*})*} matches column specs with one level of nesting
    COL_SPEC = r"\{((?:[^{}]|\{[^{}]*\})*)\}"
    TABLE_ENVS = [
        (r"\\begin\{rtltabular\}" + COL_SPEC, "rtltabular"),
        (r"\\begin\{tabular\}" + COL_SPEC, "tabular"),
        (r"\\begin\{tabularx\}" + COL_SPEC + COL_SPEC, "tabularx"),
        (r"\\begin\{longtable\}" + COL_SPEC, "longtable"),
    ]

    # Resizebox check pattern
    RESIZEBOX_PATTERN = r"\\resizebox\{[^}]*\}\{[^}]*\}\s*\{"

    # Column type characters
    COLUMN_CHARS = r"[clrCLRpmXb]"

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize detector."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def detect_in_file(self, file_path: Path) -> OverflowDetectResult:
        """Detect overflow issues in a LaTeX file."""
        if not file_path.exists():
            return OverflowDetectResult()

        content = file_path.read_text(encoding="utf-8")
        rel_path = str(file_path.relative_to(self.project_root))
        return self.detect_content(content, rel_path)

    def detect_content(self, content: str, file_path: str) -> OverflowDetectResult:
        """Detect overflow issues in content."""
        result = OverflowDetectResult()
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern, env_type in self.TABLE_ENVS:
                match = re.search(pattern, line)
                if match:
                    result.total_tables += 1

                    # Extract column spec
                    if env_type == "tabularx":
                        col_spec = match.group(2)  # Second group is column spec
                        width_spec = match.group(1)
                    else:
                        col_spec = match.group(1)
                        width_spec = ""

                    # Count columns
                    num_cols = self._count_columns(col_spec)

                    # Check for resizebox wrapper
                    has_resizebox = self._has_resizebox(content, line_num, lines)

                    # Check for tabularx with textwidth (safe)
                    is_tabularx_safe = (env_type == "tabularx" and
                                        r"\textwidth" in width_spec)

                    # Determine severity
                    severity = self._determine_severity(
                        num_cols, has_resizebox, is_tabularx_safe
                    )

                    issue = TableOverflowIssue(
                        file=file_path,
                        line=line_num,
                        table_type=env_type,
                        columns=num_cols,
                        has_resizebox=has_resizebox or is_tabularx_safe,
                        severity=severity,
                        fix=self._get_fix_suggestion(severity),
                    )
                    result.tables.append(issue)

                    if severity in ("CRITICAL", "WARNING"):
                        result.unsafe += 1
                    else:
                        result.safe += 1

        return result

    def _count_columns(self, col_spec: str) -> int:
        """Count number of columns in column specification."""
        clean = col_spec.replace("|", "")
        # Count p{}, m{}, b{} columns, then remaining single-char types
        count = len(re.findall(r"[pmb]\{[^}]*\}", clean))
        clean = re.sub(r"[pmb]\{[^}]*\}", "", clean)
        count += len(re.findall(self.COLUMN_CHARS, clean))
        return max(count, 1)

    def _has_resizebox(self, content: str, line_num: int, lines: List[str]) -> bool:
        """Check if table is wrapped in resizebox."""
        prefix = "\n".join(lines[max(0, line_num - 6):line_num - 1])
        current = lines[line_num - 1] if line_num <= len(lines) else ""
        return bool(re.search(self.RESIZEBOX_PATTERN, prefix) or
                    re.search(r"\\resizebox\{", current))

    def _determine_severity(self, num_cols: int, has_box: bool, tabularx_safe: bool) -> str:
        """Determine severity based on detection rules."""
        if has_box or tabularx_safe:
            return "SAFE"
        return "CRITICAL" if num_cols >= 5 else ("WARNING" if num_cols >= 4 else "SAFE")

    def _get_fix_suggestion(self, severity: str) -> str:
        """Get fix suggestion based on severity."""
        return r"Wrap with \resizebox{\textwidth}{!}{...}" if severity != "SAFE" else ""

    def to_dict(self, result: OverflowDetectResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-table-overflow-detect", "status": "DONE", "verdict": result.verdict,
            "tables": [{"file": t.file, "line": t.line, "type": t.table_type,
                        "columns": t.columns, "has_resizebox": t.has_resizebox,
                        "severity": t.severity, "fix": t.fix} for t in result.tables],
            "summary": {"total_tables": result.total_tables,
                        "unsafe": result.unsafe, "safe": result.safe},
            "triggers": result.triggers}

    def get_rules(self) -> Dict[str, str]:
        """Return detection rules."""
        return {"5+_columns_no_resizebox": "CRITICAL - 5+ columns without resizebox",
                "4_columns_no_resizebox": "WARNING - 4 columns without resizebox",
                "any_with_resizebox": "SAFE - Table wrapped in resizebox",
                "tabularx_textwidth": r"SAFE - tabularx with \textwidth auto-adjusts"}
