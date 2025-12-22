"""
Fancy table fixer for Hebrew RTL LaTeX documents.

Converts plain tables to styled RTL tables using rtltabular.
Aligned with qa-table-fancy-fix skill.md patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .table_parser import TableParser, ParsedTable
from .column_transformer import ColumnTransformer


@dataclass
class FixResult:
    """Result of a single table fix."""
    file: str = ""
    line: int = 0
    changes: Dict[str, str] = field(default_factory=dict)
    original: str = ""
    fixed: str = ""


@dataclass
class FancyFixResult:
    """Result of fancy table fixing."""
    tables_fixed: int = 0
    fixes: List[FixResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class FancyTableFixer:
    """
    Converts plain tables to styled RTL tables.

    Aligned with qa-table-fancy-fix skill.md:
    - Step 1: Change environment (tabular → rtltabular)
    - Step 2: Change column spec to p{}
    - Step 3: Reverse column order for RTL
    - Step 4: Use correct cell commands
    - Step 5: Add styling (rowcolor for header)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fixer."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.parser = TableParser()
        self.transformer = ColumnTransformer()

    def fix_content(self, content: str, file_path: str = "") -> FancyFixResult:
        """Fix all plain tables in content."""
        result = FancyFixResult()
        lines = content.split("\n")

        # Find all tables
        table_starts = []
        for i, line in enumerate(lines):
            if r"\begin{tabular}" in line:
                table_starts.append(i)

        # Process each table (reverse order to preserve line numbers)
        for start_idx in reversed(table_starts):
            # Extract table content
            table_content = self._extract_table(lines, start_idx)
            if not table_content:
                continue

            # Parse and fix
            parsed = self.parser.parse(table_content, start_idx)
            if not parsed:
                result.errors.append(f"Failed to parse table at line {start_idx + 1}")
                continue

            fix = self._fix_table(parsed, file_path)
            if fix:
                # Replace in content
                end_idx = parsed.end_line - parsed.start_line + start_idx
                lines[start_idx:end_idx + 1] = fix.fixed.split("\n")
                result.fixes.append(fix)
                result.tables_fixed += 1

        return result

    def _extract_table(self, lines: List[str], start_idx: int) -> str:
        """Extract table content from lines."""
        content_lines = []
        for i in range(start_idx, min(start_idx + 50, len(lines))):
            content_lines.append(lines[i])
            if r"\end{tabular}" in lines[i] or r"\end{rtltabular}" in lines[i]:
                break
        return "\n".join(content_lines)

    def _fix_table(self, table: ParsedTable, file_path: str) -> Optional[FixResult]:
        """Apply all fixes to a parsed table."""
        fix = FixResult(file=file_path, line=table.start_line + 1)
        fix.original = table.raw_content

        # Step 1: Change environment
        fix.changes["environment"] = "tabular -> rtltabular"

        # Step 2: Convert column spec
        new_spec = self.transformer.convert_column_spec(table.column_spec, table)
        fix.changes["column_spec"] = f"{table.column_spec} -> {new_spec}"

        # Step 3 & 4 & 5: Reverse columns, format cells, add styling
        output_lines = []
        output_lines.append(f"\\begin{{rtltabular}}{{{new_spec}}}")
        output_lines.append("\\hline")

        for i, row in enumerate(table.rows):
            # Reverse column order
            reversed_row = self.transformer.reverse_row(row)

            # Format with styling (header row gets rowcolor)
            is_first_data_row = i == 0 or (i == 1 and table.rows[0].is_header)
            add_style = reversed_row.is_header or (i == 0 and not any(r.is_header for r in table.rows))

            formatted = self.transformer.format_row(reversed_row, add_header_style=add_style)
            output_lines.append(formatted)

            if reversed_row.has_hline_after or i == len(table.rows) - 1:
                output_lines.append("\\hline")

        output_lines.append("\\end{rtltabular}")

        fix.changes["column_order"] = "reversed for RTL"
        fix.changes["cell_commands"] = "hebcell/encell applied"
        fix.changes["styling"] = "header_bg added"

        fix.fixed = "\n".join(output_lines)
        return fix

    def to_dict(self, result: FancyFixResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-table-fancy-fix",
            "status": "DONE",
            "tables_fixed": result.tables_fixed,
            "changes": {
                "environment": "tabular -> rtltabular",
                "column_spec": "c/l/r -> p{width}",
                "column_order": "reversed for RTL",
                "cell_commands": "hebcell/encell applied",
                "styling": ["header_bg", "bold_headers"],
            },
            "fixes": [
                {"file": f.file, "line": f.line, "changes": f.changes}
                for f in result.fixes
            ],
            "errors": result.errors,
        }
