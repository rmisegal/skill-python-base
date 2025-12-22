"""
Table cell alignment fixer for Hebrew RTL LaTeX.

Fixes cell alignment issues using CLS commands like hebcell, encell, etc.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Hebrew Unicode range pattern
HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]')


@dataclass
class CellFix:
    """Represents a cell alignment fix."""
    table: int
    row: int
    col: int
    cell_id: str
    old: str
    new: str
    fix_type: str  # "hebcell", "encell", "hebheader", "enheader"


@dataclass
class AlignmentFixResult:
    """Result of table alignment fix operation."""
    cells_fixed: int = 0
    changes: List[CellFix] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.cells_fixed > 0 else "NO_CHANGES"


class TableAlignmentFixer:
    """
    Fixes cell alignment issues in Hebrew RTL tables.

    Uses CLS commands:
    - \\hebcell{} for Hebrew content
    - \\encell{} for English content
    - \\hebheader{} for Hebrew headers
    - \\enheader{} for English headers
    """

    # Commands that are already alignment-wrapped
    WRAPPED_COMMANDS = (r'\hebcell', r'\encell', r'\hebheader', r'\enheader',
                        r'\texthebrew', r'\textbf', r'\multicolumn')

    def fix_content(self, content: str, issues: List[Dict] = None) -> tuple:
        """Fix alignment issues in content."""
        result = AlignmentFixResult()
        lines = content.split('\n')
        table_num = 0
        in_table = False
        header_done = False
        row_num = 0

        for i, line in enumerate(lines):
            # Track table boundaries
            if r'\begin{tabular}' in line or r'\begin{rtltabular}' in line:
                in_table = True
                table_num += 1
                row_num = 0
                header_done = False
                continue
            if r'\end{tabular}' in line or r'\end{rtltabular}' in line:
                in_table = False
                continue
            if not in_table:
                continue

            # Skip hline-only lines but mark header as done after first data row
            if line.strip() == r'\hline':
                if row_num > 0:
                    header_done = True
                continue

            # Process table row (has cell content)
            if '&' in line or r'\\' in line:
                row_num += 1
                # First row is header, subsequent rows are data
                is_header = not header_done

                fixed_line, fixes = self._fix_row(line, table_num, row_num, is_header)
                if fixed_line != line:
                    lines[i] = fixed_line
                    result.changes.extend(fixes)
                    result.cells_fixed += len(fixes)

        return '\n'.join(lines), result

    def _fix_row(self, line: str, table_num: int, row_num: int,
                 is_header: bool) -> tuple:
        """Fix alignment in a single table row."""
        fixes = []
        # Remove trailing \\ (two backslashes) and preserve it
        row_end = ''
        stripped = line.rstrip()
        # Match \\ at end (two backslash characters)
        if len(stripped) >= 2 and stripped[-2:] == '\\\\':
            row_end = ' \\\\'
            stripped = stripped[:-2].rstrip()
        # Also handle \hline at end of row
        hline = '\\hline'
        if stripped.endswith(hline):
            stripped = stripped[:-len(hline)].rstrip()

        # Split by cell delimiter but preserve structure
        parts = re.split(r'(&)', stripped)
        col_num = 0

        for j, part in enumerate(parts):
            if part == '&':
                continue
            col_num += 1
            cell_content = part.strip()

            # Skip if empty or already wrapped
            if not cell_content or self._is_wrapped(cell_content):
                continue

            fixed, fix_type = self._fix_cell(cell_content, is_header)
            if fixed != cell_content:
                # Preserve whitespace
                leading = len(part) - len(part.lstrip())
                trailing = len(part) - len(part.rstrip())
                parts[j] = ' ' * leading + fixed + ' ' * trailing
                fixes.append(CellFix(
                    table=table_num, row=row_num, col=col_num,
                    cell_id=f"row{row_num}-col{col_num}",
                    old=cell_content, new=fixed, fix_type=fix_type
                ))

        return ''.join(parts) + row_end, fixes

    def _is_wrapped(self, content: str) -> bool:
        """Check if content is already wrapped with alignment command."""
        return any(cmd in content for cmd in self.WRAPPED_COMMANDS)

    def _fix_cell(self, content: str, is_header: bool) -> tuple:
        """Fix a single cell's alignment."""
        has_hebrew = bool(HEBREW_PATTERN.search(content))
        has_english = bool(re.search(r'[a-zA-Z]', content))

        if is_header:
            if has_hebrew:
                return f'\\hebheader{{{content}}}', 'hebheader'
            elif has_english:
                return f'\\enheader{{{content}}}', 'enheader'
        else:
            if has_hebrew and has_english:
                # Mixed: wrap English parts with \en{}
                fixed = self._wrap_mixed(content)
                return f'\\hebcell{{{fixed}}}', 'hebcell'
            elif has_hebrew:
                return f'\\hebcell{{{content}}}', 'hebcell'
            elif has_english:
                return f'\\encell{{{content}}}', 'encell'

        return content, ''

    def _wrap_mixed(self, content: str) -> str:
        """Wrap English parts in mixed Hebrew/English content."""
        # Find English words and wrap them with \en{}
        def replace_english(match):
            word = match.group(0)
            return f'\\en{{{word}}}'

        # Match English words (sequences of ASCII letters)
        return re.sub(r'[a-zA-Z]+(?:\s+[a-zA-Z]+)*', replace_english, content)

    def to_dict(self, result: AlignmentFixResult) -> Dict:
        """Convert result to dictionary matching skill output format."""
        return {
            "skill": "qa-table-fix-alignment",
            "status": result.status,
            "cells_fixed": result.cells_fixed,
            "changes": [
                {"table": c.table, "cell": c.cell_id, "old": c.old,
                 "new": c.new, "fix_type": c.fix_type}
                for c in result.changes
            ]
        }
