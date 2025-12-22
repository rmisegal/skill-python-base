"""
BC Table Validator.

Validates RTL table formatting in Hebrew-English documents.
Wraps TableDetector and TableFixer from QA engine.
"""

from typing import Dict, List, Optional, Tuple

from ...infrastructure.detection import TableDetector
from ...infrastructure.fixing import TableFixer
from .base import BCValidatorInterface


class BCTableValidator(BCValidatorInterface):
    """
    Validator for table formatting issues.

    Checks for:
    - tabular without rtltabular (table-no-rtl-env)
    - Hebrew cell content without wrapper (table-cell-hebrew)
    - Wide table overflow (table-overflow)
    - table instead of hebrewtable (table-not-hebrewtable)
    - Missing rowcolor on header (table-missing-header-color)
    - Wrong hebrewtable syntax (table-wrong-syntax)
    """

    def __init__(
        self,
        detector: Optional[TableDetector] = None,
        fixer: Optional[TableFixer] = None,
    ) -> None:
        """Initialize with Table detector and fixer."""
        super().__init__(
            detector=detector or TableDetector(),
            fixer=fixer or TableFixer(),
            validator_name="BCTableValidator",
        )

    def get_rules(self) -> Dict[str, str]:
        """Return rule name -> description mapping."""
        return {
            "table-no-rtl-env": "Table using tabular without rtltabular",
            "table-cell-hebrew": "Hebrew in table cell without \\hebcell{}",
            "table-header-hebrew": "Hebrew in header without \\hebheader{}",
            "table-overflow": "Wide table without resizebox",
            "table-not-hebrewtable": "Uses table instead of hebrewtable",
            "table-missing-header-color": "Header row missing \\rowcolor{blue!15}",
            "table-wrong-syntax": "hebrewtable uses [caption={...}] instead of [H]",
            "table-caption-outside": "Caption/label outside hebrewtable environment",
        }

    def validate_table_structure(self, content: str) -> bool:
        """
        Quick check if table has proper RTL structure.

        Returns True if table appears valid.
        """
        import re

        # Check for tabular without rtltabular
        if re.search(r"\\begin\{tabular\}", content):
            if not re.search(r"\\begin\{rtltabular\}", content):
                return False

        # Check for table without hebrewtable
        if re.search(r"\\begin\{table\}", content):
            if not re.search(r"\\begin\{hebrewtable\}", content):
                return False

        return True

    def validate_hebrewtable_syntax(self, content: str) -> List[Tuple[int, str]]:
        """
        Check hebrewtable uses correct syntax.

        CORRECT: \\begin{hebrewtable}[H] or [htbp] with caption INSIDE
        WRONG:   \\begin{hebrewtable}[caption={...}, label={...}]
        WRONG:   \\begin{hebrewtable}{arg1}{arg2}... (positional args)

        Returns list of (line_number, issue_description) tuples.
        """
        import re

        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for hebrewtable with positional args (WRONG)
            if re.search(r"\\begin\{hebrewtable\}\{", line):
                issues.append((i, "hebrewtable uses {arg} - use [H] instead"))

            # Check for hebrewtable with [caption={...}] syntax (WRONG!)
            if re.search(r"\\begin\{hebrewtable\}\[caption=", line):
                issues.append((i, "hebrewtable uses [caption={}] - use [H] with caption INSIDE"))

            # Check for hebrewtable with [label={...}] syntax (WRONG!)
            if re.search(r"\\begin\{hebrewtable\}\[.*label=", line):
                issues.append((i, "hebrewtable uses [label={}] - use [H] with label INSIDE"))

        return issues

    def validate_hebrew_wrappers(self, content: str) -> List[Tuple[int, str]]:
        """
        Check Hebrew text in tables uses \\hebcell{} or \\hebheader{}.

        Returns list of (line_number, issue_description) tuples.
        """
        import re

        issues = []
        lines = content.split("\n")

        in_table = False
        in_header_row = False

        for i, line in enumerate(lines, 1):
            # Track table boundaries
            if re.search(r"\\begin\{(rtltabular|hebrewtable)\}", line):
                in_table = True
                continue
            if re.search(r"\\end\{(rtltabular|hebrewtable)\}", line):
                in_table = False
                in_header_row = False
                continue

            if not in_table:
                continue

            # Detect header row (has rowcolor)
            if r"\rowcolor" in line:
                in_header_row = True

            # Check for Hebrew without wrapper in table cells
            # Hebrew range: \u0590-\u05FF
            hebrew_pattern = r'[\u0590-\u05FF]+'

            # Skip if line is just hline or empty
            if line.strip() in [r'\hline', '']:
                in_header_row = False
                continue

            # Find Hebrew text not inside wrappers
            # Remove already wrapped content first
            check_line = re.sub(r'\\hebcell\{[^}]*\}', '', line)
            check_line = re.sub(r'\\hebheader\{[^}]*\}', '', check_line)
            check_line = re.sub(r'\\en\{[^}]*\}', '', check_line)
            check_line = re.sub(r'\\texthebrew\{[^}]*\}', '', check_line)

            # Now check if Hebrew remains unwrapped
            if re.search(hebrew_pattern, check_line):
                if in_header_row:
                    issues.append((i, "Hebrew in header without \\hebheader{}"))
                else:
                    issues.append((i, "Hebrew in cell without \\hebcell{}"))

            # Reset header flag after processing header row
            if r'\\' in line and in_header_row:
                in_header_row = False

        return issues

    def validate_header_rowcolor(self, content: str) -> List[Tuple[int, str]]:
        """
        Check tables have \\rowcolor{blue!15} on header row.

        Returns list of (line_number, issue_description) tuples.
        """
        import re

        issues = []
        lines = content.split("\n")

        in_table = False
        table_start_line = 0
        found_hline = False
        found_rowcolor = False

        for i, line in enumerate(lines, 1):
            if re.search(r"\\begin\{(rtltabular|hebrewtable)\}", line):
                in_table = True
                table_start_line = i
                found_hline = False
                found_rowcolor = False
                continue

            if in_table:
                if r"\hline" in line and not found_hline:
                    found_hline = True
                    continue

                # After first \hline, next content line should have rowcolor
                if found_hline and not found_rowcolor:
                    if line.strip() and not line.strip().startswith("%"):
                        if r"\rowcolor" in line:
                            found_rowcolor = True
                        elif r"\textbf" in line or r"\hebheader" in line:
                            # Header row without rowcolor
                            issues.append((i, "Header row missing \\rowcolor{blue!15}"))
                            found_rowcolor = True  # Stop checking this table

                if re.search(r"\\end\{(rtltabular|hebrewtable)\}", line):
                    in_table = False

        return issues

    def ensure_rtl_table(self, content: str) -> str:
        """
        Convert tabular to rtltabular if needed.

        Returns modified content with proper RTL table.
        """
        import re

        # Replace tabular with rtltabular
        content = re.sub(
            r"\\begin\{tabular\}",
            r"\\begin{rtltabular}",
            content,
        )
        content = re.sub(
            r"\\end\{tabular\}",
            r"\\end{rtltabular}",
            content,
        )

        # Replace table with hebrewtable
        content = re.sub(
            r"\\begin\{table\}",
            r"\\begin{hebrewtable}",
            content,
        )
        content = re.sub(
            r"\\end\{table\}",
            r"\\end{hebrewtable}",
            content,
        )

        return content
