"""
Header color fixer for LaTeX tables.

Adds rowcolor{blue!15} to header rows missing the styling.
Minimal-invasive fix that preserves existing table structure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class HeaderColorFix:
    """Single header color fix record."""
    file: str = ""
    line: int = 0
    original_line: str = ""
    fixed_line: str = ""


@dataclass
class HeaderColorResult:
    """Result of header color fixing."""
    fixes_applied: int = 0
    changes: List[HeaderColorFix] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied > 0 else "NO_CHANGES"


class HeaderColorFixer:
    """Adds rowcolor{blue!15} to table header rows."""

    # Pattern to find rtltabular or tabular start with optional hline
    TABLE_START = r"\\begin\{(?:rtltabular|tabular)\}\{[^}]+\}"
    HLINE = r"\\hline"
    ROWCOLOR_HEADER = r"\\rowcolor\{blue!15\}"

    def fix_content(self, content: str, file_path: str = "") -> tuple[str, HeaderColorResult]:
        """Add header color to tables missing it."""
        result = HeaderColorResult()
        lines = content.split("\n")
        modified = False

        i = 0
        while i < len(lines):
            line = lines[i]
            # Check for table start
            if re.search(self.TABLE_START, line):
                # Check if header color is already present in next few lines
                has_color = False
                header_row_idx = None
                for j in range(i + 1, min(i + 5, len(lines))):
                    if re.search(self.ROWCOLOR_HEADER, lines[j]):
                        has_color = True
                        break
                    # Find first content row (after optional \hline)
                    if header_row_idx is None and r"\\" in lines[j] and not lines[j].strip() == r"\hline":
                        header_row_idx = j

                if not has_color and header_row_idx is not None:
                    # Add rowcolor to beginning of header row
                    original = lines[header_row_idx]
                    lines[header_row_idx] = r"\rowcolor{blue!15}" + lines[header_row_idx]
                    result.changes.append(HeaderColorFix(
                        file=file_path,
                        line=header_row_idx + 1,
                        original_line=original,
                        fixed_line=lines[header_row_idx]
                    ))
                    result.fixes_applied += 1
                    modified = True
            i += 1

        return "\n".join(lines), result

    def fix_file(self, file_path: Path, dry_run: bool = False) -> HeaderColorResult:
        """Fix a single file."""
        if not file_path.exists():
            return HeaderColorResult(errors=[f"File not found: {file_path}"])

        content = file_path.read_text(encoding="utf-8")
        fixed, result = self.fix_content(content, str(file_path))

        if not dry_run and result.fixes_applied > 0:
            file_path.write_text(fixed, encoding="utf-8")

        return result

    def to_dict(self, result: HeaderColorResult) -> Dict:
        """Convert result to dictionary for reporting."""
        return {
            "skill": "qa-table-header-color-fix",
            "status": result.status,
            "fixes_applied": result.fixes_applied,
            "changes": [
                {"file": c.file, "line": c.line}
                for c in result.changes
            ],
            "errors": result.errors,
        }
