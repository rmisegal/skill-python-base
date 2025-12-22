"""
QA-compliant table templates for BC content generation.

All templates pass these QA rules:
- table-no-rtl-env: Uses rtltabular
- table-not-hebrewtable: Uses hebrewtable
- table-missing-header-color: Has rowcolor{blue!15}
- table-cell-hebrew: Hebrew uses \\hebcell{}, headers use \\hebheader{}
- table-overflow: Uses resizebox when needed

CRITICAL FORMAT (CLS v6.3+):
- hebrewtable takes [H] or [htbp], NOT [caption={...}]
- Caption and label go INSIDE the environment
- Use m{Xcm} columns, NOT R{} (which doesn't exist)
- Hebrew cells MUST use \\hebcell{} for RTL direction
- Hebrew headers MUST use \\hebheader{} for RTL direction
"""

from typing import List, Optional
import re


def _is_hebrew(text: str) -> bool:
    """Check if text contains Hebrew characters."""
    return bool(re.search(r'[\u0590-\u05FF]', text))


def _wrap_cell(content: str) -> str:
    """Wrap cell content with appropriate wrapper."""
    # Already wrapped
    if content.startswith(r'\hebcell{') or content.startswith(r'\en{'):
        return content
    # Hebrew content
    if _is_hebrew(content):
        return f"\\hebcell{{{content}}}"
    # English/technical content
    return f"\\en{{{content}}}"


def _wrap_header(content: str) -> str:
    """Wrap header content with hebheader."""
    # Already wrapped
    if r'\hebheader{' in content:
        return content
    # Extract text from \textbf{} if present
    match = re.match(r'\\textbf\{(.+)\}', content)
    if match:
        inner = match.group(1)
        if _is_hebrew(inner):
            return f"\\textbf{{\\hebheader{{{inner}}}}}"
        return f"\\textbf{{\\en{{{inner}}}}}"
    # Plain text
    if _is_hebrew(content):
        return f"\\textbf{{\\hebheader{{{content}}}}}"
    return f"\\textbf{{\\en{{{content}}}}}"


class TableTemplates:
    """QA-compliant table templates."""

    @staticmethod
    def basic_table(
        caption: str,
        label: str,
        headers: List[str],
        rows: List[List[str]],
        col_widths_cm: Optional[List[float]] = None,
    ) -> str:
        """
        Generate a QA-compliant Hebrew RTL table.

        Args:
            caption: Hebrew caption for the table
            label: LaTeX label (e.g., 'tbl:example')
            headers: List of header cell contents
            rows: List of rows, each row is list of cell contents
            col_widths_cm: Optional column widths in cm (default 3cm each)

        Returns:
            LaTeX code for QA-compliant table
        """
        num_cols = len(headers)
        if col_widths_cm is None:
            col_widths_cm = [3.0] * num_cols

        # Build column spec with m{Xcm} for vertical centering
        col_spec = "|".join([f"m{{{w:.1f}cm}}" for w in col_widths_cm])
        col_spec = f"|{col_spec}|"

        # Build header row with rowcolor and hebheader wrappers
        header_cells = " & ".join([_wrap_header(h) for h in headers])
        header_row = f"\\rowcolor{{blue!15}} {header_cells} \\\\"

        # Build data rows with hebcell/en wrappers
        data_rows = []
        for row in rows:
            cells = " & ".join([_wrap_cell(c) for c in row])
            data_rows.append(f"{cells} \\\\")

        rows_text = "\n\\hline\n".join(data_rows)

        return f"""\\begin{{hebrewtable}}[H]
\\caption{{{caption}}}
\\label{{{label}}}
\\begin{{rtltabular}}{{|{col_spec}|}}
\\hline
{header_row}
\\hline
{rows_text}
\\hline
\\end{{rtltabular}}
\\end{{hebrewtable}}"""

    @staticmethod
    def comparison_table(
        caption: str,
        label: str,
        aspect_header: str,
        option1_header: str,
        option2_header: str,
        comparisons: List[tuple],
    ) -> str:
        """
        Generate a comparison table (3 columns).

        Args:
            caption: Hebrew caption
            label: LaTeX label
            aspect_header: Header for aspect column
            option1_header: Header for first option
            option2_header: Header for second option
            comparisons: List of (aspect, option1, option2) tuples

        Returns:
            LaTeX code for comparison table
        """
        headers = [aspect_header, option1_header, option2_header]
        rows = [list(comp) for comp in comparisons]
        # Column widths in cm: aspect 4cm, options 5cm each
        return TableTemplates.basic_table(
            caption, label, headers, rows, [4.0, 5.0, 5.0]
        )

    @staticmethod
    def summary_table(
        caption: str,
        label: str,
        categories: List[tuple],
    ) -> str:
        """
        Generate a summary table (2 columns: category, description).

        Args:
            caption: Hebrew caption
            label: LaTeX label
            categories: List of (category, description) tuples

        Returns:
            LaTeX code for summary table
        """
        headers = ["קטגוריה", "תיאור"]
        rows = [list(cat) for cat in categories]
        # Column widths in cm: category 3.5cm, description 10cm
        return TableTemplates.basic_table(
            caption, label, headers, rows, [3.5, 10.0]
        )
