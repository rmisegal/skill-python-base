"""Unit tests for Table Column Fixer."""
import pytest
from qa_engine.table.fixing import TableColumnFixer, ColumnFixResult


class TestTableColumnFixer:
    """Tests for TableColumnFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = TableColumnFixer()

    def test_reverse_simple_row(self):
        """Test reversing a simple 3-column row."""
        content = r"""\begin{tabular}{|c|c|c|}
\hline
A & B & C \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert "C & B & A" in fixed
        assert result.tables_fixed == 1

    def test_reverse_multiple_rows(self):
        """Test reversing multiple rows."""
        content = r"""\begin{tabular}{|c|c|c|}
\hline
H1 & H2 & H3 \\
\hline
D1 & D2 & D3 \\
E1 & E2 & E3 \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert "H3 & H2 & H1" in fixed
        assert "D3 & D2 & D1" in fixed
        assert "E3 & E2 & E1" in fixed

    def test_preserve_environment(self):
        """Test that environment is not changed."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\begin{tabular}" in fixed
        assert r"\end{tabular}" in fixed
        # Should NOT convert to rtltabular
        assert "rtltabular" not in fixed

    def test_preserve_rtltabular(self):
        """Test that rtltabular stays rtltabular."""
        content = r"""\begin{rtltabular}{|c|c|}
A & B \\
\end{rtltabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\begin{rtltabular}" in fixed
        assert r"\end{rtltabular}" in fixed

    def test_preserve_column_spec(self):
        """Test that column spec is not changed."""
        content = r"""\begin{tabular}{|l|c|r|}
A & B & C \\
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert "{|l|c|r|}" in fixed

    def test_preserve_row_endings(self):
        """Test that \\\\ row endings are preserved."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\\" in fixed

    def test_preserve_hline(self):
        """Test that \\hline is preserved."""
        content = r"""\begin{tabular}{|c|c|}
\hline
A & B \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\hline" in fixed

    def test_multiple_tables(self):
        """Test fixing multiple tables."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}

Some text.

\begin{tabular}{|c|c|c|}
X & Y & Z \\
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert result.tables_fixed == 2
        assert "B & A" in fixed
        assert "Z & Y & X" in fixed

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}"""
        _, result = self.fixer.fix_content(content, "test.tex")
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-table-fix-columns"
        assert output["status"] == "DONE"
        assert output["tables_fixed"] == 1
        assert "changes" in output
        assert len(output["changes"]) == 1
        assert output["changes"][0]["action"] == "reversed column order"

    def test_change_has_required_fields(self):
        """Test that change records have all required fields."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}"""
        _, result = self.fixer.fix_content(content, "chapter.tex")
        output = self.fixer.to_dict(result)

        change = output["changes"][0]
        assert "table" in change
        assert "file" in change
        assert "line" in change
        assert "action" in change

    def test_no_changes_when_no_tables(self):
        """Test status when no tables found."""
        content = "Just some text without tables."
        _, result = self.fixer.fix_content(content)
        assert result.status == "NO_CHANGES"

    def test_done_status(self):
        """Test status when changes applied."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}"""
        _, result = self.fixer.fix_content(content)
        assert result.status == "DONE"

    def test_preserve_cell_content(self):
        """Test that cell content with special chars is preserved."""
        content = r"""\begin{tabular}{|c|c|}
\textbf{Header1} & \textbf{Header2} \\
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\textbf{Header2} & \textbf{Header1}" in fixed
