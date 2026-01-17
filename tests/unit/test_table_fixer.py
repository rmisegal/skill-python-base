"""
Tests for Table fixer - fixing table issues in Hebrew RTL LaTeX.
"""

import pytest

from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.infrastructure.fixing.table_fixer import TableFixer


class TestTableFixer:
    """Tests for TableFixer."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = TableFixer()

    def test_fix_plain_table_converts_to_rtltabular(self):
        """Test converting plain tabular to rtltabular."""
        content = r"""
\begin{table}
\begin{tabular}{|c|c|}
\hline
A & B \\
\hline
\end{tabular}
\end{table}
"""
        issue = Issue(
            rule="table-plain-unstyled",
            file="test.tex",
            line=3,
            content="",
            severity=Severity.WARNING,
        )
        result = self.fixer.fix(content, [issue])
        assert r"\begin{rtltabular}" in result
        assert r"\end{rtltabular}" in result
        assert r"\begin{tabular}" not in result

    def test_fix_no_rtl_env_adds_wrapper(self):
        """Test adding RTL wrapper to table without one."""
        content = r"""Some text
\begin{table}
\begin{tabular}{|c|}
A \\
\end{tabular}
\end{table}
More text"""
        issue = Issue(
            rule="table-no-rtl-env",
            file="test.tex",
            line=2,
            content="",
            severity=Severity.WARNING,
        )
        result = self.fixer.fix(content, [issue])
        assert r"\begin{RTL}" in result
        assert r"\end{RTL}" in result

    def test_fix_no_rtl_env_skips_if_already_wrapped(self):
        """Test that fixer skips tables already in RTL environment."""
        content = r"""\begin{RTL}
\begin{table}
\begin{tabular}{|c|}
A \\
\end{tabular}
\end{table}
\end{RTL}"""
        issue = Issue(
            rule="table-no-rtl-env",
            file="test.tex",
            line=2,
            content="",
            severity=Severity.WARNING,
        )
        result = self.fixer.fix(content, [issue])
        # Should NOT add another RTL wrapper
        assert result.count(r"\begin{RTL}") == 1
        assert result.count(r"\end{RTL}") == 1

    def test_fix_no_rtl_env_skips_if_in_hebrew_env(self):
        """Test that fixer skips tables inside hebrew environment."""
        content = r"""\begin{hebrew}
\begin{table}
\begin{tabular}{|c|}
A \\
\end{tabular}
\end{table}
\end{hebrew}"""
        issue = Issue(
            rule="table-no-rtl-env",
            file="test.tex",
            line=2,
            content="",
            severity=Severity.WARNING,
        )
        result = self.fixer.fix(content, [issue])
        # Should NOT add RTL wrapper
        assert r"\begin{RTL}" not in result

    def test_fix_no_rtl_env_skips_if_in_english_env(self):
        """Test that fixer skips tables inside english environment."""
        content = r"""\begin{english}
\begin{table}
\begin{tabular}{|c|}
A \\
\end{tabular}
\end{table}
\end{english}"""
        issue = Issue(
            rule="table-no-rtl-env",
            file="test.tex",
            line=2,
            content="",
            severity=Severity.WARNING,
        )
        result = self.fixer.fix(content, [issue])
        # Should NOT add RTL wrapper (already in english env)
        assert r"\begin{RTL}" not in result

    def test_is_already_rtl_wrapped_detects_wrapper(self):
        """Test _is_already_rtl_wrapped correctly detects wrappers."""
        lines = [
            r"\begin{RTL}",
            r"\begin{table}",
            r"\begin{tabular}{|c|}",
            r"A \\",
            r"\end{tabular}",
            r"\end{table}",
            r"\end{RTL}",
        ]
        # Table starts at line 1, ends at line 5
        assert self.fixer._is_already_rtl_wrapped(lines, 1, 5) is True

    def test_is_already_rtl_wrapped_no_wrapper(self):
        """Test _is_already_rtl_wrapped returns False when no wrapper."""
        lines = [
            r"Some text",
            r"\begin{table}",
            r"\begin{tabular}{|c|}",
            r"A \\",
            r"\end{tabular}",
            r"\end{table}",
            r"More text",
        ]
        assert self.fixer._is_already_rtl_wrapped(lines, 1, 5) is False

    def test_is_already_rtl_wrapped_nested_env(self):
        """Test detection with nested environments."""
        lines = [
            r"\begin{hebrew}",
            r"Some Hebrew text",
            r"\begin{table}",
            r"\begin{tabular}{|c|}",
            r"A \\",
            r"\end{tabular}",
            r"\end{table}",
            r"\end{hebrew}",
        ]
        # Table at lines 2-6
        assert self.fixer._is_already_rtl_wrapped(lines, 2, 6) is True

    def test_prevents_triple_wrapping(self):
        """Test that multiple fix calls don't create triple wrappers."""
        content = r"""\begin{RTL}
\begin{table}
\begin{tabular}{|c|}
A \\
\end{tabular}
\end{table}
\end{RTL}"""
        issue = Issue(
            rule="table-no-rtl-env",
            file="test.tex",
            line=2,
            content="",
            severity=Severity.WARNING,
        )
        # Apply fix multiple times
        result = self.fixer.fix(content, [issue])
        result = self.fixer.fix(result, [issue])
        result = self.fixer.fix(result, [issue])
        # Should still have only one RTL wrapper
        assert result.count(r"\begin{RTL}") == 1
        assert result.count(r"\end{RTL}") == 1
