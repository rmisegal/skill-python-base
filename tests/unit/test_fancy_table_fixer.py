"""Unit tests for Fancy Table Fixer."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.table.fixing.fancy_table_fixer import FancyTableFixer, FancyFixResult
from qa_engine.table.fixing.table_parser import TableParser, ParsedTable
from qa_engine.table.fixing.column_transformer import ColumnTransformer


class TestTableParser:
    """Tests for TableParser."""

    def setup_method(self):
        self.parser = TableParser()

    def test_parse_simple_table(self):
        """Test parsing a simple tabular."""
        content = r"""
\begin{tabular}{|c|c|c|}
\hline
A & B & C \\
\hline
\end{tabular}
"""
        result = self.parser.parse(content)
        assert result is not None
        assert result.environment == "tabular"
        assert len(result.rows) >= 1

    def test_parse_column_spec(self):
        """Test column spec extraction."""
        content = r"\begin{tabular}{|l|c|r|}\hline\end{tabular}"
        result = self.parser.parse(content)
        assert result.column_spec == "|l|c|r|"

    def test_parse_hebrew_cells(self):
        """Test Hebrew cell detection."""
        content = r"""
\begin{tabular}{|c|c|}
\hline
English & עברית \\
\hline
\end{tabular}
"""
        result = self.parser.parse(content)
        assert result is not None
        assert len(result.rows) >= 1
        # Check that Hebrew is detected
        has_hebrew = any(cell.is_hebrew for row in result.rows for cell in row.cells)
        assert has_hebrew

    def test_count_columns(self):
        """Test column counting."""
        assert self.parser.count_columns("|c|c|c|") == 3
        assert self.parser.count_columns("|l|r|") == 2
        assert self.parser.count_columns("|p{2cm}|p{3cm}|") == 2


class TestColumnTransformer:
    """Tests for ColumnTransformer."""

    def setup_method(self):
        self.transformer = ColumnTransformer()

    def test_convert_simple_spec(self):
        """Test converting c/l/r to p{}."""
        table = ParsedTable(rows=[])
        result = self.transformer.convert_column_spec("|c|c|c|", table)
        assert "p{" in result
        assert "|" in result

    def test_reverse_row(self):
        """Test row reversal."""
        from qa_engine.table.fixing.table_parser import TableRow, TableCell
        row = TableRow(cells=[
            TableCell(content="A", is_hebrew=False),
            TableCell(content="B", is_hebrew=False),
            TableCell(content="C", is_hebrew=True),
        ])
        reversed_row = self.transformer.reverse_row(row)
        assert reversed_row.cells[0].content == "C"
        assert reversed_row.cells[2].content == "A"

    def test_format_hebrew_cell(self):
        """Test Hebrew cell formatting."""
        from qa_engine.table.fixing.table_parser import TableCell
        cell = TableCell(content="עברית", is_hebrew=True, is_header=False, original="עברית")
        result = self.transformer.format_cell(cell)
        assert r"\hebcell{" in result

    def test_format_english_cell(self):
        """Test English cell formatting."""
        from qa_engine.table.fixing.table_parser import TableCell
        cell = TableCell(content="English", is_hebrew=False, is_header=False, original="English")
        result = self.transformer.format_cell(cell)
        assert r"\encell{" in result

    def test_format_header_cell(self):
        """Test header cell formatting."""
        from qa_engine.table.fixing.table_parser import TableCell
        cell = TableCell(content="Header", is_hebrew=False, is_header=True, original="Header")
        result = self.transformer.format_cell(cell)
        assert r"\textbf" in result
        assert r"\enheader{" in result


class TestFancyTableFixer:
    """Tests for FancyTableFixer."""

    def setup_method(self):
        self.fixer = FancyTableFixer()

    def test_fix_simple_table(self):
        """Test fixing a simple plain table."""
        content = r"""
\begin{tabular}{|c|c|c|}
\hline
A & B & C \\
\hline
\end{tabular}
"""
        result = self.fixer.fix_content(content, "test.tex")
        assert result.tables_fixed >= 1
        assert len(result.fixes) >= 1

    def test_environment_change(self):
        """Test environment is changed to rtltabular."""
        content = r"\begin{tabular}{|c|c|}\hline A & B \\\hline\end{tabular}"
        result = self.fixer.fix_content(content, "test.tex")
        if result.fixes:
            assert "rtltabular" in result.fixes[0].fixed

    def test_column_spec_change(self):
        """Test column spec is changed to p{}."""
        content = r"\begin{tabular}{|c|c|}\hline A & B \\\hline\end{tabular}"
        result = self.fixer.fix_content(content, "test.tex")
        if result.fixes:
            assert "p{" in result.fixes[0].fixed

    def test_column_order_reversed(self):
        """Test columns are reversed for RTL."""
        content = r"""
\begin{tabular}{|c|c|}
\hline
English & עברית \\
\hline
\end{tabular}
"""
        result = self.fixer.fix_content(content, "test.tex")
        if result.fixes:
            # In fixed output, Hebrew should come before English (reversed)
            fixed = result.fixes[0].fixed
            # Check that the reversal happened
            assert "reversed for RTL" in result.fixes[0].changes.get("column_order", "")

    def test_cell_commands_applied(self):
        """Test cell commands are applied."""
        content = r"""
\begin{tabular}{|c|c|}
\hline
Header1 & Header2 \\
\hline
Hello & שלום \\
\hline
\end{tabular}
"""
        result = self.fixer.fix_content(content, "test.tex")
        if result.fixes:
            fixed = result.fixes[0].fixed
            # Header row uses hebheader/enheader, data rows use hebcell/encell
            has_cell_cmds = (r"\hebcell{" in fixed or r"\encell{" in fixed or
                            r"\hebheader{" in fixed or r"\enheader{" in fixed)
            assert has_cell_cmds

    def test_header_styling(self):
        """Test header row gets styling."""
        content = r"""
\begin{tabular}{|c|c|}
\hline
Header1 & Header2 \\
\hline
Data1 & Data2 \\
\hline
\end{tabular}
"""
        result = self.fixer.fix_content(content, "test.tex")
        if result.fixes:
            fixed = result.fixes[0].fixed
            assert r"\rowcolor{blue!15}" in fixed

    def test_output_format(self):
        """Test output format matches skill.md."""
        content = r"\begin{tabular}{|c|}\hline A \\\hline\end{tabular}"
        result = self.fixer.fix_content(content, "test.tex")
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-table-fancy-fix"
        assert output["status"] == "DONE"
        assert "tables_fixed" in output
        assert "changes" in output
        assert "environment" in output["changes"]
        assert "column_spec" in output["changes"]
        assert "column_order" in output["changes"]
        assert "cell_commands" in output["changes"]

    def test_no_tables_returns_empty(self):
        """Test content without tables returns empty result."""
        content = r"Some text without tables."
        result = self.fixer.fix_content(content, "test.tex")
        assert result.tables_fixed == 0
        assert len(result.fixes) == 0

    def test_rtltabular_not_fixed(self):
        """Test rtltabular tables are not modified."""
        content = r"\begin{rtltabular}{|p{2cm}|}\hline A \\\hline\end{rtltabular}"
        result = self.fixer.fix_content(content, "test.tex")
        # rtltabular should not be "fixed" as it's already correct
        assert result.tables_fixed == 0
