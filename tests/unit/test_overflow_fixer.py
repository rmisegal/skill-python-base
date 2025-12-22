"""Unit tests for Table Overflow Fixer."""
import pytest
from qa_engine.table.fixing import TableOverflowFixer, OverflowFixResult


class TestTableOverflowFixer:
    """Tests for TableOverflowFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = TableOverflowFixer()

    def test_wrap_simple_table(self):
        """Test wrapping a simple table with resizebox."""
        content = r"""\begin{tabular}{|c|c|c|c|c|}
\hline
A & B & C & D & E \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\resizebox{\textwidth}{!}{%" in fixed
        assert result.tables_fixed == 1

    def test_wrap_rtltabular(self):
        """Test wrapping rtltabular."""
        content = r"""\begin{rtltabular}{|c|c|c|c|c|}
\hline
A & B & C & D & E \\
\hline
\end{rtltabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\resizebox{\textwidth}{!}{%" in fixed
        assert r"\end{rtltabular}%" in fixed
        assert result.tables_fixed == 1

    def test_add_percent_after_end(self):
        """Test that % is added after \\end{...}."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\end{tabular}%" in fixed

    def test_preserve_already_wrapped(self):
        """Test that already wrapped tables are not double-wrapped."""
        content = r"""\resizebox{\textwidth}{!}{%
\begin{tabular}{|c|c|}
A & B \\
\end{tabular}%
}"""
        fixed, result = self.fixer.fix_content(content)
        # Should not add another resizebox
        assert fixed.count(r"\resizebox") == 1
        assert result.tables_fixed == 0

    def test_multiple_tables(self):
        """Test fixing multiple tables."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}

\begin{rtltabular}{|c|c|c|}
X & Y & Z \\
\end{rtltabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert result.tables_fixed == 2
        assert fixed.count(r"\resizebox") == 2

    def test_preserve_caption_outside(self):
        """Test that caption stays outside resizebox."""
        content = r"""\begin{hebrewtable}[htbp]
\caption{Test table}
\begin{rtltabular}{|c|c|c|c|c|}
\hline
A & B & C & D & E \\
\hline
\end{rtltabular}
\end{hebrewtable}"""
        fixed, result = self.fixer.fix_content(content)
        # Caption should come before resizebox
        caption_pos = fixed.find(r"\caption")
        resize_pos = fixed.find(r"\resizebox")
        assert caption_pos < resize_pos

    def test_preserve_indentation(self):
        """Test that indentation is preserved."""
        content = r"""    \begin{tabular}{|c|c|}
    A & B \\
    \end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert "    \\resizebox" in fixed

    def test_fix_with_issues_list(self):
        """Test fixing with pre-detected issues."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}

\begin{tabular}{|c|c|}
X & Y \\
\end{tabular}"""
        # Only fix the first table (line 1)
        issues = [{"line": 1, "type": "tabular", "severity": "CRITICAL"}]
        fixed, result = self.fixer.fix_content(content, issues=issues)
        assert result.tables_fixed == 1

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"""\begin{tabular}{|c|c|}
A & B \\
\end{tabular}"""
        _, result = self.fixer.fix_content(content, "test.tex")
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-table-overflow-fix"
        assert output["status"] == "DONE"
        assert output["tables_fixed"] == 1
        assert "changes" in output
        assert len(output["changes"]) == 1
        assert output["changes"][0]["action"] == "wrapped with resizebox"

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

    def test_longtable_support(self):
        """Test that longtable is also wrapped."""
        content = r"""\begin{longtable}{|c|c|c|c|c|}
\hline
A & B & C & D & E \\
\hline
\end{longtable}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\resizebox{\textwidth}{!}{%" in fixed
        assert result.tables_fixed == 1
