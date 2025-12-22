"""
Table parser for LaTeX tables.

Parses table structure for transformation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class TableCell:
    """Represents a single table cell."""
    content: str
    is_hebrew: bool = False
    is_header: bool = False
    original: str = ""


@dataclass
class TableRow:
    """Represents a table row."""
    cells: List[TableCell] = field(default_factory=list)
    is_header: bool = False
    has_hline_before: bool = False
    has_hline_after: bool = False
    raw_line: str = ""


@dataclass
class ParsedTable:
    """Parsed table structure."""
    environment: str = "tabular"
    column_spec: str = ""
    rows: List[TableRow] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    raw_content: str = ""


HEBREW_PATTERN = re.compile(r"[א-ת]")
CELL_CMD_PATTERN = re.compile(r"\\(hebcell|hebheader|encell|enheader)\{([^}]*)\}")


class TableParser:
    """Parses LaTeX tables into structured format."""

    def parse(self, content: str, start_line: int = 0) -> Optional[ParsedTable]:
        """Parse table content into structured format."""
        lines = content.split("\n")
        table = ParsedTable(start_line=start_line, raw_content=content)

        # Find environment and column spec
        env_match = re.search(
            r"\\begin\{(tabular|rtltabular)\}\{([^}]+)\}", content
        )
        if not env_match:
            return None

        table.environment = env_match.group(1)
        table.column_spec = env_match.group(2)

        # Parse rows
        in_table = False
        current_row_lines: List[str] = []
        hline_before = False
        first_row_parsed = False  # Track if we've seen the first data row

        for i, line in enumerate(lines):
            if r"\begin{" in line and ("tabular" in line or "rtltabular" in line):
                in_table = True
                continue
            if r"\end{" in line and ("tabular" in line or "rtltabular" in line):
                table.end_line = start_line + i
                break
            if not in_table:
                continue

            stripped = line.strip()
            if stripped == r"\hline":
                if current_row_lines:
                    is_header = hline_before and not first_row_parsed
                    row = self._parse_row("\n".join(current_row_lines), is_header)
                    row.has_hline_after = True
                    table.rows.append(row)
                    current_row_lines = []
                    first_row_parsed = True
                hline_before = True
                continue

            if stripped:
                current_row_lines.append(line)
                if r"\\" in line:
                    is_header = hline_before and not first_row_parsed
                    row = self._parse_row("\n".join(current_row_lines), is_header)
                    table.rows.append(row)
                    current_row_lines = []
                    hline_before = False
                    first_row_parsed = True

        return table

    def _parse_row(self, line: str, hline_before: bool) -> TableRow:
        """Parse a single row into cells."""
        row = TableRow(raw_line=line, has_hline_before=hline_before)

        # Remove trailing \\ and split by &
        clean_line = re.sub(r"\\\\.*$", "", line).strip()
        # Handle rowcolor
        clean_line = re.sub(r"\\rowcolor\{[^}]+\}\s*", "", clean_line)

        parts = clean_line.split("&")
        is_first_row = hline_before  # First row after hline is likely header

        for part in parts:
            cell = self._parse_cell(part.strip(), is_first_row)
            row.cells.append(cell)

        # Check if this is a header row (has hebheader/enheader or is bold)
        if r"\hebheader" in line or r"\enheader" in line or r"\textbf" in line:
            row.is_header = True
            for cell in row.cells:
                cell.is_header = True

        return row

    def _parse_cell(self, content: str, is_header: bool) -> TableCell:
        """Parse cell content."""
        cell = TableCell(content=content, original=content, is_header=is_header)

        # Check for Hebrew
        cell.is_hebrew = bool(HEBREW_PATTERN.search(content))

        # Extract actual content from cell commands
        cmd_match = CELL_CMD_PATTERN.search(content)
        if cmd_match:
            cell.content = cmd_match.group(2)
            cell.is_hebrew = cmd_match.group(1) in ("hebcell", "hebheader")

        return cell

    def count_columns(self, column_spec: str) -> int:
        """Count number of columns from spec."""
        # Remove | and count column types
        clean = column_spec.replace("|", "")
        # Count c, l, r, or p{...}
        count = len(re.findall(r"[clrCLR]|p\{[^}]+\}", clean))
        return count if count > 0 else 1
