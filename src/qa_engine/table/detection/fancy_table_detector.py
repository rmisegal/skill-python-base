"""
Fancy table detector for Hebrew RTL LaTeX documents.

Detects plain/broken tables without proper RTL styling.
Aligned with qa-table-fancy-detect skill.md patterns.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from .table_models import TableAnalysis, FancyDetectResult


class FancyTableDetector:
    """Detects plain/broken tables without proper RTL styling."""

    TABULAR_START, RTLTABULAR_START = r"\\begin\{tabular\}", r"\\begin\{rtltabular\}"
    TABLE_ENV_START, HEBREWTABLE_ENV_START = r"\\begin\{table\}", r"\\begin\{hebrewtable\}"
    TABLE_LABEL = r"\\label\{([^}]+)\}"
    COLUMN_SPEC_SIMPLE = r"\\begin\{(?:tabular|rtltabular)\}\{[|lcrLCR]+\}"
    COLUMN_SPEC_P = r"\\begin\{(?:tabular|rtltabular)\}\{[^}]*p\{[^}]+\}[^}]*\}"
    HEBCELL, HEBHEADER = r"\\hebcell\{", r"\\hebheader\{"
    ROWCOLOR_DATA, HEBREW_TEXT = r"\\rowcolor\{gray!\d+\}", r"[א-ת]+"
    ROWCOLOR_HEADER = r"\\rowcolor\{blue!15\}"  # Header row should have blue background

    PROBLEM_CODES = {
        "uses_tabular_not_rtltabular": "Uses tabular instead of rtltabular",
        "uses_table_not_hebrewtable": "Uses table instead of hebrewtable in Hebrew doc",
        "uses_c_columns_not_p": "Uses c/l/r columns instead of p{width}",
        "missing_hebcell_commands": "Hebrew without hebcell/hebheader",
        "missing_header_color": "Header row missing rowcolor{blue!15}",
        "ltr_column_order": "Hebrew column last (should be first for RTL)",
        "gray_rowcolor_on_data": "Uses rowcolor{gray} on data rows",
        "tabular_in_hebrewtable": "Uses tabular inside hebrewtable",
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def detect_in_file(self, file_path: Path) -> FancyDetectResult:
        if not file_path.exists():
            return FancyDetectResult()
        return self.detect_content(file_path.read_text(encoding="utf-8"),
                                   str(file_path.relative_to(self.project_root)))

    def detect_content(self, content: str, file_path: str) -> FancyDetectResult:
        result, tables = FancyDetectResult(), self._find_tables(content)
        result.tables_scanned = len(tables)
        for table in tables:
            analysis = self._analyze_table(table, content, file_path)
            if analysis.classification == "PLAIN":
                result.plain_tables_found += 1
                result.issues.append(analysis)
            elif analysis.classification == "PARTIAL":
                result.partial_tables_found += 1
                result.issues.append(analysis)
            else:
                result.fancy_tables_found += 1
        return result

    def _find_tables(self, content: str) -> List[Dict]:
        tables, lines = [], content.split("\n")
        for line_num, line in enumerate(lines, 1):
            if re.search(self.TABULAR_START, line) or re.search(self.RTLTABULAR_START, line):
                tc = self._extract_table_content(lines, line_num - 1)
                lbl = (m := re.search(self.TABLE_LABEL, tc)) and m.group(1) or ""
                in_hebrewtable = self._in_hebrewtable(line_num, content)
                in_table = self._in_table_env(line_num, content)
                in_english = self._in_english_env(line_num, content)
                tables.append({"line": line_num, "content": tc, "label": lbl,
                               "is_rtltabular": bool(re.search(self.RTLTABULAR_START, line)),
                               "in_hebrewtable": in_hebrewtable, "in_table": in_table,
                               "in_english": in_english})
        return tables

    def _extract_table_content(self, lines: List[str], start_idx: int) -> str:
        result = []
        for i in range(start_idx, min(start_idx + 50, len(lines))):
            result.append(lines[i])
            if r"\end{tabular}" in lines[i] or r"\end{rtltabular}" in lines[i]:
                break
        return "\n".join(result)

    def _analyze_table(self, table: Dict, full_content: str, file_path: str) -> TableAnalysis:
        """Analyze a single table for issues."""
        problems = self._find_problems(table, full_content)
        return TableAnalysis(file=file_path, line=table["line"], table_label=table["label"],
                             classification=self._classify(problems), problems=problems,
                             severity=self._determine_severity(problems))

    def _find_problems(self, table: Dict, full_content: str) -> List[str]:
        """Find all problems in a table."""
        problems, content, is_rtl = [], table["content"], table["is_rtltabular"]
        in_hebrewtable = table.get("in_hebrewtable", False)
        in_table = table.get("in_table", False)
        in_english = table.get("in_english", False)

        # Skip RTL-related checks for tables inside english environment
        if not in_english:
            # Check for wrong tabular environment
            if not is_rtl:
                problems.append("uses_tabular_not_rtltabular")
            # Check for wrong table environment (table instead of hebrewtable in Hebrew doc)
            if in_table and not in_hebrewtable and self._is_hebrew_document(full_content):
                problems.append("uses_table_not_hebrewtable")
            if re.search(self.COLUMN_SPEC_SIMPLE, content) and not re.search(self.COLUMN_SPEC_P, content):
                problems.append("uses_c_columns_not_p")
            if re.search(self.HEBREW_TEXT, content) and not (re.search(self.HEBCELL, content) or re.search(self.HEBHEADER, content)):
                problems.append("missing_hebcell_commands")
            if not is_rtl and self._check_ltr_order(content):
                problems.append("ltr_column_order")
            if in_hebrewtable and not is_rtl:
                problems.append("tabular_in_hebrewtable")

        # These checks apply to all tables (including English)
        if not self._has_header_color(content):
            problems.append("missing_header_color")
        if re.search(self.ROWCOLOR_DATA, content):
            problems.append("gray_rowcolor_on_data")
        return problems

    def _check_ltr_order(self, content: str) -> bool:
        """Check if Hebrew appears last (wrong for RTL)."""
        for line in content.split("\n"):
            if "&" in line and r"\\" in line:
                parts = line.split("&")
                if len(parts) >= 2 and re.search(self.HEBREW_TEXT, parts[-1]) and not re.search(self.HEBREW_TEXT, parts[0]):
                    return True
                break
        return False

    def _in_hebrewtable(self, line_num: int, content: str) -> bool:
        """Check if inside hebrewtable environment."""
        lines = content.split("\n")
        for i in range(line_num - 1, max(0, line_num - 20), -1):
            if r"\begin{hebrewtable}" in lines[i]:
                return True
            if r"\end{hebrewtable}" in lines[i]:
                return False
        return False

    def _in_table_env(self, line_num: int, content: str) -> bool:
        """Check if inside table environment (not hebrewtable)."""
        lines = content.split("\n")
        for i in range(line_num - 1, max(0, line_num - 20), -1):
            if r"\begin{table}" in lines[i]:
                return True
            if r"\end{table}" in lines[i]:
                return False
        return False

    def _in_english_env(self, line_num: int, content: str) -> bool:
        """Check if inside english environment."""
        lines = content.split("\n")
        for i in range(line_num - 1, max(0, line_num - 30), -1):
            if r"\begin{english}" in lines[i]:
                return True
            if r"\end{english}" in lines[i]:
                return False
        return False

    def _has_header_color(self, content: str) -> bool:
        """Check if table has header row with blue background color."""
        return bool(re.search(self.ROWCOLOR_HEADER, content))

    def _is_hebrew_document(self, content: str) -> bool:
        """Check if document contains Hebrew text (making it RTL context)."""
        return bool(re.search(self.HEBREW_TEXT, content))

    CRITICAL_PROBLEMS = ["uses_tabular_not_rtltabular", "uses_table_not_hebrewtable",
                         "missing_header_color", "ltr_column_order", "tabular_in_hebrewtable"]

    def _classify(self, problems: List[str]) -> str:
        """Classify table as PLAIN, PARTIAL, or FANCY."""
        if any(p in self.CRITICAL_PROBLEMS for p in problems):
            return "PLAIN"
        return "PARTIAL" if problems else "FANCY"

    def _determine_severity(self, problems: List[str]) -> str:
        """Determine overall severity based on problems."""
        if any(p in self.CRITICAL_PROBLEMS for p in problems):
            return "CRITICAL"
        return "WARNING" if problems else "INFO"

    def to_dict(self, result: FancyDetectResult) -> Dict:
        """Convert result to skill.md output format."""
        return {"skill": "qa-table-fancy-detect", "status": "DONE",
                "tables_scanned": result.tables_scanned, "plain_tables_found": result.plain_tables_found,
                "partial_tables_found": result.partial_tables_found, "fancy_tables_found": result.fancy_tables_found,
                "issues": [{"file": a.file, "line": a.line, "table_label": a.table_label,
                            "classification": a.classification, "problems": a.problems, "severity": a.severity}
                           for a in result.issues], "triggers": result.triggers}

    def get_rules(self) -> Dict[str, str]:
        return self.PROBLEM_CODES.copy()
