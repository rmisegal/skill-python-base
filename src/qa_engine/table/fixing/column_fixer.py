"""
Table column order fixer for Hebrew RTL LaTeX.

Reverses column order in tables for correct RTL display.
Aligned with qa-table-fix-columns skill.md.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ColumnFixChange:
    """Represents a column fix change."""
    table: int
    file: str
    line: int
    action: str = "reversed column order"


@dataclass
class ColumnFixResult:
    """Result of column order fix operation."""
    tables_fixed: int = 0
    changes: List[ColumnFixChange] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.tables_fixed > 0 else "NO_CHANGES"


class TableColumnFixer:
    """
    Fixes column order in Hebrew RTL tables.

    Reverses column order so that:
    - LaTeX Column 1 appears RIGHTMOST in RTL display
    - LaTeX Column N appears LEFTMOST in RTL display

    Does NOT change:
    - Environment (tabular/rtltabular)
    - Column spec (|c|c|c|)
    - Styling or cell commands
    """

    # Pattern to match table environments
    TABLE_BEGIN = re.compile(r'\\begin\{(tabular|rtltabular)\}\{([^}]+)\}')
    TABLE_END = re.compile(r'\\end\{(tabular|rtltabular)\}')

    def fix_content(self, content: str, file_path: str = "") -> tuple:
        """Fix column order in all tables in content."""
        result = ColumnFixResult()
        lines = content.split('\n')
        table_num = 0
        in_table = False
        table_start = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Detect table start
            if self.TABLE_BEGIN.search(line):
                in_table = True
                table_start = i
                table_num += 1
                i += 1
                continue

            # Detect table end
            if in_table and self.TABLE_END.search(line):
                in_table = False
                result.changes.append(ColumnFixChange(
                    table=table_num, file=file_path, line=table_start + 1
                ))
                result.tables_fixed += 1
                i += 1
                continue

            # Process table rows
            if in_table and '&' in line:
                lines[i] = self._reverse_row(line)

            i += 1

        return '\n'.join(lines), result

    def _reverse_row(self, line: str) -> str:
        """Reverse column order in a single row."""
        # Preserve leading whitespace
        leading = len(line) - len(line.lstrip())
        prefix = line[:leading]

        # Handle row ending (\\)
        row_end = ''
        stripped = line.rstrip()
        if stripped.endswith('\\\\'):
            row_end = ' \\\\'
            stripped = stripped[:-2].rstrip()

        # Handle \hline at end
        hline_suffix = ''
        if stripped.endswith('\\hline'):
            hline_suffix = ' \\hline'
            stripped = stripped[:-6].rstrip()

        # Split by & and reverse
        parts = stripped[leading:].split('&')
        reversed_parts = list(reversed(parts))

        # Rebuild row preserving spacing
        rebuilt = ' & '.join(p.strip() for p in reversed_parts)
        return prefix + rebuilt + row_end + hline_suffix

    def fix_file(self, file_path: Path) -> ColumnFixResult:
        """Fix column order in a file."""
        if not file_path.exists():
            return ColumnFixResult()

        content = file_path.read_text(encoding='utf-8')
        fixed_content, result = self.fix_content(content, str(file_path))

        if result.tables_fixed > 0:
            file_path.write_text(fixed_content, encoding='utf-8')

        return result

    def to_dict(self, result: ColumnFixResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-table-fix-columns",
            "status": result.status,
            "tables_fixed": result.tables_fixed,
            "changes": [
                {"table": c.table, "file": c.file, "line": c.line, "action": c.action}
                for c in result.changes
            ]
        }
