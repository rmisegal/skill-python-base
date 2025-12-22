"""
Table layout detector for RTL Hebrew documents.

Aligns with qa-table-detect skill.md output format.
Provides source-level detection that complements PDF visual analysis.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from .table_models import TableIssue, TableDetectResult


class TableLayoutDetector:
    """
    Detects table layout issues in Hebrew RTL documents.

    Aligns with qa-table-detect skill.md phases:
    - Phase 1: Table Discovery
    - Phase 2: Caption Alignment Analysis
    - Phase 3: Column Order Inspection
    - Phase 4: Cell Content Analysis
    """

    TABLE_ENV = r"\\begin\{(table|tabular|rtltabular)\}"
    TABLE_END = r"\\end\{(table|tabular|rtltabular)\}"
    CAPTION_PATTERN = r"\\caption\{([^}]*)\}"
    CAPTION_LEFT = r"\\begin\{flushleft\}[^}]*\\caption"
    LTR_TABULAR = r"\\begin\{tabular\}"
    HEBREW_IN_CELL = r"&\s*([א-ת][^&\\]*)\s*(?:&|\\\\)"

    RULES = {
        "column-order-ltr": "Table using LTR tabular in Hebrew document",
        "caption-left-aligned": "Caption left-aligned (should be center/right)",
        "cell-hebrew-unwrapped": "Hebrew text in cell without RTL wrapper",
        "table-no-rtl-env": "Table environment without RTL support",
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize detector with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def detect_in_file(self, file_path: Path) -> TableDetectResult:
        """Detect table issues in a LaTeX file."""
        if not file_path.exists():
            return TableDetectResult()
        content = file_path.read_text(encoding="utf-8")
        rel_path = str(file_path.relative_to(self.project_root)) if self.project_root else str(file_path)
        return self.detect_content(content, rel_path)

    def detect_content(self, content: str, file_path: str) -> TableDetectResult:
        """Detect table issues in content string."""
        result = TableDetectResult()
        tables = self._discover_tables(content)
        result.tables_found = len(tables)

        for table_num, table_info in enumerate(tables, 1):
            issues = self._analyze_table(table_info, content, result)
            if issues:
                result.details.append(TableIssue(
                    table_num=table_num, page=0, caption=table_info.get("caption", ""),
                    issue_type=", ".join(issues), severity="WARNING",
                    line=table_info.get("line", 0), context=file_path,
                ))

        result.issues_found = len(result.details)
        return result

    def _analyze_table(self, table_info: Dict, content: str, result: TableDetectResult) -> List[str]:
        """Analyze single table for all issue types."""
        issues = []
        if self._check_caption_alignment(table_info, content):
            issues.append("caption_alignment")
            result.caption_alignment_issues += 1
        if self._check_column_order(table_info, content):
            issues.append("column_order")
            result.column_order_issues += 1
        cell_count = self._check_cell_alignment(table_info, content)
        if cell_count:
            issues.append("cell_alignment")
            result.cell_alignment_issues += cell_count
        return issues

    def _discover_tables(self, content: str) -> List[Dict]:
        """Phase 1: Discover all tables in content."""
        tables, lines = [], content.split("\n")
        for line_num, line in enumerate(lines, 1):
            if re.search(self.TABLE_ENV, line):
                caption = ""
                for i in range(max(0, line_num - 3), min(len(lines), line_num + 10)):
                    cap_match = re.search(self.CAPTION_PATTERN, lines[i])
                    if cap_match:
                        caption = cap_match.group(1)
                        break
                tables.append({"line": line_num, "caption": caption, "env_line": line})
        return tables

    def _check_caption_alignment(self, table_info: Dict, content: str) -> bool:
        """Phase 2: Check caption alignment (left is wrong for Hebrew)."""
        ctx_start = max(0, content.find(table_info.get("env_line", "")) - 200)
        return bool(re.search(self.CAPTION_LEFT, content[ctx_start:ctx_start + 500]))

    def _check_column_order(self, table_info: Dict, content: str) -> bool:
        """Phase 3: Check if table uses LTR tabular in Hebrew context."""
        if re.search(self.LTR_TABULAR, table_info.get("env_line", "")):
            return bool(re.search(r"[א-ת]", content))
        return False

    def _check_cell_alignment(self, table_info: Dict, content: str) -> int:
        """Phase 4: Check cell content alignment issues."""
        lines = content.split("\n")
        line_num, issues = table_info.get("line", 0), 0
        for i in range(line_num, min(line_num + 30, len(lines))):
            if re.search(self.TABLE_END, lines[i]):
                break
            if re.search(self.HEBREW_IN_CELL, lines[i]):
                issues += 1
        return issues

    def to_dict(self, result: TableDetectResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-table-detect", "status": "DONE",
            "tables_found": result.tables_found, "issues_found": result.issues_found,
            "categories": {
                "column_order": result.column_order_issues,
                "caption_alignment": result.caption_alignment_issues,
                "cell_alignment": result.cell_alignment_issues,
            },
            "details": [
                {"table": d.table_num, "page": d.page, "caption": d.caption,
                 "issues": d.issue_type.split(", "), "line": d.line}
                for d in result.details
            ],
            "triggers": result.triggers,
        }

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return self.RULES.copy()
