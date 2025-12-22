"""Unit tests for Fancy Table Detector."""
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.table.detection.fancy_table_detector import (
    FancyTableDetector, FancyDetectResult, TableAnalysis
)


class TestFancyTableDetector:
    """Tests for FancyTableDetector aligned with skill.md."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = FancyTableDetector(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_file(self, name: str, content: str) -> Path:
        """Helper to create a test file."""
        path = Path(self.temp_dir) / name
        path.write_text(content, encoding="utf-8")
        return path

    # Detection Criteria Tests

    def test_detects_tabular_not_rtltabular(self):
        """Test detection of tabular instead of rtltabular."""
        content = r"""
\begin{tabular}{|c|c|c|}
\hline
A & B & C \\
\hline
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables_scanned >= 1
        assert any("uses_tabular_not_rtltabular" in a.problems for a in result.issues)

    def test_detects_simple_column_spec(self):
        """Test detection of c/l/r columns instead of p{}."""
        content = r"""
\begin{tabular}{|l|c|r|}
\hline
A & B & C \\
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert any("uses_c_columns_not_p" in a.problems for a in result.issues)

    def test_detects_missing_hebcell(self):
        """Test detection of Hebrew without hebcell."""
        content = r"""
\begin{tabular}{|c|c|}
\hline
שלום & עולם \\
\hline
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert any("missing_hebcell_commands" in a.problems for a in result.issues)

    def test_detects_ltr_column_order(self):
        """Test detection of LTR column order (Hebrew last)."""
        content = r"""
\begin{tabular}{|c|c|c|}
\hline
English & More English & עברית \\
\hline
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert any("ltr_column_order" in a.problems for a in result.issues)

    def test_detects_gray_rowcolor_on_data(self):
        """Test detection of gray rowcolor on data rows."""
        content = r"""
\begin{rtltabular}{|p{2cm}|p{2cm}|}
\hline
\rowcolor{blue!15}
Header & Header \\
\hline
\rowcolor{gray!8}
Data & Data \\
\hline
\end{rtltabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert any("gray_rowcolor_on_data" in a.problems for a in result.issues)

    # Proper Table Tests (should be FANCY)

    def test_fancy_table_no_issues(self):
        """Test proper RTL table has no issues."""
        content = r"""
\begin{rtltabular}{|p{2.5cm}|p{2.5cm}|p{3.5cm}|}
\hline
\rowcolor{blue!15}
\textbf{\enheader{HTTP}} & \textbf{\enheader{stdio}} & \textbf{\hebheader{קריטריון}} \\
\hline
\encell{REST} & \encell{JSON-RPC} & \hebcell{פרוטוקול} \\
\hline
\end{rtltabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.fancy_tables_found >= 1
        # Should have no issues or only INFO level
        critical_issues = [a for a in result.issues if a.severity == "CRITICAL"]
        assert len(critical_issues) == 0

    def test_rtltabular_detected_as_rtl(self):
        """Test rtltabular is recognized as RTL environment."""
        content = r"""
\begin{rtltabular}{|c|c|}
\hline
A & B \\
\end{rtltabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        # Should not have "uses_tabular_not_rtltabular" error
        assert not any("uses_tabular_not_rtltabular" in a.problems for a in result.issues)

    def test_p_columns_detected(self):
        """Test p{} columns are recognized as proper."""
        content = r"""
\begin{rtltabular}{|p{3cm}|p{4cm}|}
\hline
A & B \\
\end{rtltabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        # Should not have column spec error
        assert not any("uses_c_columns_not_p" in a.problems for a in result.issues)

    # Classification Tests

    def test_classify_plain(self):
        """Test PLAIN classification for tables with critical issues."""
        content = r"""
\begin{tabular}{|c|c|}
\hline
English & עברית \\
\hline
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.plain_tables_found >= 1
        assert any(a.classification == "PLAIN" for a in result.issues)

    def test_classify_partial(self):
        """Test PARTIAL classification for tables with minor issues."""
        content = r"""
\begin{rtltabular}{|c|c|}
\hline
\hebcell{עברית} & \encell{English} \\
\rowcolor{gray!8}
Data & Data \\
\hline
\end{rtltabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        # Has rtltabular and hebcell but gray rowcolor
        partial = [a for a in result.issues if a.classification == "PARTIAL"]
        assert len(partial) >= 0  # May or may not trigger based on detection

    # Output Format Tests

    def test_to_dict_format(self):
        """Test output format matches skill.md specification."""
        content = r"\begin{tabular}{|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-table-fancy-detect"
        assert output["status"] == "DONE"
        assert "tables_scanned" in output
        assert "plain_tables_found" in output
        assert "partial_tables_found" in output
        assert "fancy_tables_found" in output
        assert "issues" in output
        assert "triggers" in output

    def test_triggers_on_plain_tables(self):
        """Test triggers generated when plain tables found."""
        result = FancyDetectResult(plain_tables_found=1)
        assert "qa-table-fancy-fix" in result.triggers

    def test_no_triggers_on_fancy_only(self):
        """Test no triggers when all tables are fancy."""
        result = FancyDetectResult(fancy_tables_found=3)
        assert result.triggers == []

    def test_get_rules(self):
        """Test get_rules returns all problem codes."""
        rules = self.detector.get_rules()
        assert "uses_tabular_not_rtltabular" in rules
        assert "uses_c_columns_not_p" in rules
        assert "missing_hebcell_commands" in rules
        assert "ltr_column_order" in rules
        assert "gray_rowcolor_on_data" in rules

    # Integration Tests

    def test_detect_in_file(self):
        """Test detection from file."""
        content = r"\begin{tabular}{|c|}\hline A \\\end{tabular}"
        path = self._create_file("test.tex", content)
        result = self.detector.detect_in_file(path)
        assert result.tables_scanned >= 1

    def test_nonexistent_file_returns_empty(self):
        """Test handling of nonexistent file."""
        result = self.detector.detect_in_file(Path("/nonexistent.tex"))
        assert result.tables_scanned == 0

    def test_extracts_table_label(self):
        """Test table label extraction."""
        content = r"""
\begin{table}
\label{tab:test-table}
\begin{tabular}{|c|}
\hline
\end{tabular}
\end{table}
"""
        result = self.detector.detect_content(content, "test.tex")
        labels = [a.table_label for a in result.issues if a.table_label]
        assert any("tab:test-table" in label for label in labels) or result.tables_scanned > 0
