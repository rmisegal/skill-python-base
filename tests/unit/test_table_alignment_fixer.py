"""Unit tests for Table Alignment Fixer."""
import pytest
from qa_engine.infrastructure.fixing import TableAlignmentFixer, AlignmentFixResult


class TestTableAlignmentFixer:
    """Tests for TableAlignmentFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = TableAlignmentFixer()

    def test_fix_english_header(self):
        """Test fixing English header cells."""
        content = r"""\begin{tabular}{|c|c|}
\hline
Header1 & Header2 \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert result.cells_fixed >= 2
        assert r'\enheader{Header1}' in fixed
        assert r'\enheader{Header2}' in fixed

    def test_fix_hebrew_header(self):
        """Test fixing Hebrew header cells."""
        content = r"""\begin{tabular}{|c|c|}
\hline
כותרת & עמודה \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert result.cells_fixed >= 2
        assert r'\hebheader{' in fixed

    def test_fix_english_data_cell(self):
        """Test fixing English data cells."""
        content = r"""\begin{tabular}{|c|c|}
\hline
Col1 & Col2 \\
\hline
Data1 & Data2 \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r'\encell{Data1}' in fixed
        assert r'\encell{Data2}' in fixed

    def test_fix_hebrew_data_cell(self):
        """Test fixing Hebrew data cells."""
        content = r"""\begin{tabular}{|c|c|}
\hline
Col1 & Col2 \\
\hline
תוכן & עוד תוכן \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert r'\hebcell{' in fixed

    def test_fix_mixed_content(self):
        """Test fixing mixed Hebrew/English content."""
        content = r"""\begin{tabular}{|c|}
\hline
Header \\
\hline
עברית English \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        # Should wrap with hebcell and English part with \en{}
        assert r'\hebcell{' in fixed
        assert r'\en{English}' in fixed

    def test_skip_already_wrapped(self):
        """Test that already wrapped cells are skipped."""
        content = r"""\begin{tabular}{|c|}
\hline
\hebheader{כותרת} \\
\hline
\hebcell{תוכן} \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        # Should not double-wrap
        assert result.cells_fixed == 0
        assert r'\hebheader{\hebheader' not in fixed

    def test_skip_empty_cells(self):
        """Test that empty cells are skipped."""
        content = r"""\begin{tabular}{|c|c|}
\hline
Header &  \\
\hline
\end{tabular}"""
        fixed, result = self.fixer.fix_content(content)
        # Only the non-empty cell should be fixed
        changes_for_empty = [c for c in result.changes if c.old.strip() == '']
        assert len(changes_for_empty) == 0

    def test_rtltabular_support(self):
        """Test that rtltabular environment is supported."""
        content = r"""\begin{rtltabular}{|c|c|}
\hline
כותרת & עמודה \\
\hline
\end{rtltabular}"""
        fixed, result = self.fixer.fix_content(content)
        assert result.cells_fixed >= 2
        assert r'\hebheader{' in fixed

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"""\begin{tabular}{|c|}
\hline
Header \\
\hline
Data \\
\hline
\end{tabular}"""
        _, result = self.fixer.fix_content(content)
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-table-fix-alignment"
        assert output["status"] in ["DONE", "NO_CHANGES"]
        assert "cells_fixed" in output
        assert "changes" in output

    def test_change_has_required_fields(self):
        """Test that change records have all required fields."""
        content = r"""\begin{tabular}{|c|}
\hline
Header \\
\hline
Data \\
\hline
\end{tabular}"""
        _, result = self.fixer.fix_content(content)
        output = self.fixer.to_dict(result)

        if output["changes"]:
            change = output["changes"][0]
            assert "table" in change
            assert "cell" in change
            assert "old" in change
            assert "new" in change

    def test_no_changes_status(self):
        """Test status when no changes needed."""
        content = r"""\begin{tabular}{|c|}
\hline
\hebheader{כותרת} \\
\hline
\hebcell{תוכן} \\
\hline
\end{tabular}"""
        _, result = self.fixer.fix_content(content)
        assert result.status == "NO_CHANGES"

    def test_done_status(self):
        """Test status when changes applied."""
        content = r"""\begin{tabular}{|c|}
\hline
Header \\
\hline
\end{tabular}"""
        _, result = self.fixer.fix_content(content)
        assert result.status == "DONE"
