"""
Table overflow fixer for LaTeX documents.

Wraps wide tables with resizebox to prevent overfull hbox.
Aligned with qa-table-overflow-fix skill.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class OverflowFix:
    """Record of a single overflow fix."""
    table: int
    file: str
    line: int
    action: str


@dataclass
class OverflowFixResult:
    """Result of overflow fixing."""
    tables_fixed: int = 0
    changes: List[OverflowFix] = field(default_factory=list)
    status: str = "NO_CHANGES"


class TableOverflowFixer:
    """
    Fixes wide tables by wrapping with resizebox.

    Aligned with qa-table-overflow-fix skill.md:
    - Add \\resizebox{\\textwidth}{!}{% BEFORE table
    - Add % after \\end{...} and closing }
    """

    TABLE_BEGIN = re.compile(
        r'(\\begin\{(rtltabular|tabular|longtable)\}\{[^}]+\})'
    )
    TABLE_END = re.compile(r'(\\end\{(rtltabular|tabular|longtable)\})')
    RESIZEBOX_CHECK = re.compile(r'\\resizebox\{')

    def fix_file(self, file_path: Path) -> OverflowFixResult:
        """Fix overflow issues in a file."""
        if not file_path.exists():
            return OverflowFixResult()

        content = file_path.read_text(encoding="utf-8")
        fixed, result = self.fix_content(content, str(file_path))

        if result.tables_fixed > 0:
            file_path.write_text(fixed, encoding="utf-8")

        return result

    def fix_content(
        self, content: str, file_path: str = "",
        issues: Optional[List[Dict]] = None
    ) -> Tuple[str, OverflowFixResult]:
        """Fix overflow issues in content."""
        result = OverflowFixResult()
        lines = content.split("\n")

        # Find tables needing fixes
        tables_to_fix = self._find_tables_to_fix(lines, issues)

        if not tables_to_fix:
            return content, result

        # Apply fixes from bottom to top to preserve line numbers
        for table_info in reversed(tables_to_fix):
            lines = self._wrap_table(lines, table_info, result, file_path)

        result.status = "DONE" if result.tables_fixed > 0 else "NO_CHANGES"
        return "\n".join(lines), result

    def _find_tables_to_fix(
        self, lines: List[str], issues: Optional[List[Dict]]
    ) -> List[Dict]:
        """Find tables that need wrapping."""
        tables = []

        if issues:
            # Use provided issues
            for issue in issues:
                if issue.get("severity") in ("CRITICAL", "WARNING"):
                    tables.append({
                        "line": issue.get("line", 0),
                        "type": issue.get("type", "tabular")
                    })
        else:
            # Detect tables without resizebox
            for i, line in enumerate(lines):
                match = self.TABLE_BEGIN.search(line)
                if match:
                    # Check previous lines for resizebox
                    prefix = "\n".join(lines[max(0, i - 3):i + 1])
                    if not self.RESIZEBOX_CHECK.search(prefix):
                        tables.append({"line": i + 1, "type": match.group(2)})

        return tables

    def _wrap_table(
        self, lines: List[str], table_info: Dict,
        result: OverflowFixResult, file_path: str
    ) -> List[str]:
        """Wrap a single table with resizebox."""
        start_idx = table_info["line"] - 1
        table_type = table_info["type"]

        # Find table end
        end_idx = self._find_table_end(lines, start_idx, table_type)
        if end_idx is None:
            return lines

        # Get indentation
        indent = self._get_indent(lines[start_idx])

        # Insert resizebox wrapper
        lines[start_idx] = f"{indent}\\resizebox{{\\textwidth}}{{!}}{{%\n{lines[start_idx]}"

        # Add closing after table end
        end_line = lines[end_idx]
        if not end_line.rstrip().endswith("%"):
            lines[end_idx] = end_line.rstrip() + "%"
        lines[end_idx] = lines[end_idx] + f"\n{indent}}}"

        result.tables_fixed += 1
        result.changes.append(OverflowFix(
            table=result.tables_fixed,
            file=file_path,
            line=table_info["line"],
            action="wrapped with resizebox"
        ))

        return lines

    def _find_table_end(
        self, lines: List[str], start: int, table_type: str
    ) -> Optional[int]:
        """Find the end line of a table."""
        pattern = re.compile(rf'\\end\{{{table_type}\}}')
        for i in range(start, len(lines)):
            if pattern.search(lines[i]):
                return i
        return None

    def _get_indent(self, line: str) -> str:
        """Get leading whitespace from a line."""
        return line[:len(line) - len(line.lstrip())]

    def to_dict(self, result: OverflowFixResult) -> Dict:
        """Convert result to dictionary matching skill.md output."""
        return {
            "skill": "qa-table-overflow-fix",
            "status": result.status,
            "tables_fixed": result.tables_fixed,
            "changes": [
                {
                    "table": c.table,
                    "file": c.file,
                    "line": c.line,
                    "action": c.action,
                }
                for c in result.changes
            ],
        }
