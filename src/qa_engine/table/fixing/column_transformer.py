"""
Column transformer for RTL tables.

Handles column spec conversion and order reversal.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from .table_parser import ParsedTable, TableRow, TableCell


class ColumnTransformer:
    """Transforms table columns for RTL layout."""

    # Default column widths
    HEBREW_WIDTH = "3.5cm"
    ENGLISH_WIDTH = "2.5cm"
    DEFAULT_WIDTH = "2.5cm"

    def convert_column_spec(self, spec: str, table: ParsedTable) -> str:
        """Convert c/l/r columns to p{width} columns."""
        # Extract column types
        columns = self._extract_columns(spec)
        num_cols = len(columns)

        # Analyze content to determine widths
        widths = self._estimate_widths(table, num_cols)

        # Build new spec with p{} columns
        new_cols = []
        for i, (col_type, _) in enumerate(columns):
            if col_type == "p":
                # Keep existing p{} width
                new_cols.append(f"p{{{widths[i]}}}")
            else:
                new_cols.append(f"p{{{widths[i]}}}")

        # Preserve | separators
        has_left_border = spec.startswith("|")
        has_right_border = spec.endswith("|")
        has_inner_borders = "||" in spec or ("|" in spec[1:-1] if len(spec) > 2 else False)

        if has_inner_borders or (has_left_border and has_right_border):
            return "|" + "|".join(new_cols) + "|"
        return "".join(new_cols)

    def _extract_columns(self, spec: str) -> List[Tuple[str, str]]:
        """Extract column definitions from spec."""
        columns = []
        # Match c, l, r, or p{...}
        pattern = r"([clrCLR])|(p)\{([^}]+)\}"
        for match in re.finditer(pattern, spec):
            if match.group(1):
                columns.append((match.group(1).lower(), ""))
            else:
                columns.append(("p", match.group(3)))
        return columns

    def _estimate_widths(self, table: ParsedTable, num_cols: int) -> List[str]:
        """Estimate column widths based on content."""
        widths = [self.DEFAULT_WIDTH] * num_cols

        if not table.rows:
            return widths

        # Analyze each column
        for col_idx in range(num_cols):
            has_hebrew = False
            max_len = 0

            for row in table.rows:
                if col_idx < len(row.cells):
                    cell = row.cells[col_idx]
                    if cell.is_hebrew:
                        has_hebrew = True
                    max_len = max(max_len, len(cell.content))

            # Set width based on content
            if has_hebrew:
                widths[col_idx] = self.HEBREW_WIDTH
            elif max_len > 15:
                widths[col_idx] = "3cm"
            else:
                widths[col_idx] = self.ENGLISH_WIDTH

        return widths

    def reverse_row(self, row: TableRow) -> TableRow:
        """Reverse column order in a row for RTL."""
        new_row = TableRow(
            cells=list(reversed(row.cells)),
            is_header=row.is_header,
            has_hline_before=row.has_hline_before,
            has_hline_after=row.has_hline_after,
            raw_line=row.raw_line,
        )
        return new_row

    def format_cell(self, cell: TableCell, force_header: bool = False) -> str:
        """Format cell with appropriate command."""
        content = cell.content.strip()

        # Skip if already wrapped
        if r"\hebcell" in cell.original or r"\encell" in cell.original:
            return cell.original
        if r"\hebheader" in cell.original or r"\enheader" in cell.original:
            return cell.original

        # Determine if this is a header cell
        is_header = force_header or cell.is_header

        # Wrap content
        if is_header:
            if cell.is_hebrew:
                return f"\\textbf{{\\hebheader{{{content}}}}}"
            return f"\\textbf{{\\enheader{{{content}}}}}"
        else:
            if cell.is_hebrew:
                return f"\\hebcell{{{content}}}"
            return f"\\encell{{{content}}}"

    def format_row(self, row: TableRow, add_header_style: bool = False) -> str:
        """Format a complete row."""
        parts = []

        # Add rowcolor for header row
        if add_header_style:
            parts.append("\\rowcolor{blue!15}")

        # Format cells (treat as header if add_header_style is True)
        cell_parts = [self.format_cell(cell, force_header=add_header_style) for cell in row.cells]
        parts.append(" & ".join(cell_parts) + r" \\")

        return "\n".join(parts)
