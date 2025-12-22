"""Unit tests for Table Overflow Detector."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.table.detection.table_overflow_detector import (
    TableOverflowDetector, OverflowDetectResult, TableOverflowIssue
)


class TestTableOverflowDetector:
    """Tests for TableOverflowDetector aligned with skill.md."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = TableOverflowDetector()

    # Step 1: Find Table Environments

    def test_detects_tabular(self):
        """Test detection of tabular environment."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.total_tables == 1
        assert result.tables[0].table_type == "tabular"

    def test_detects_rtltabular(self):
        """Test detection of rtltabular environment."""
        content = r"\begin{rtltabular}{|c|c|c|c|c|}\hline\end{rtltabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.total_tables == 1
        assert result.tables[0].table_type == "rtltabular"

    def test_detects_tabularx(self):
        """Test detection of tabularx environment."""
        content = r"\begin{tabularx}{\textwidth}{|X|X|X|}\hline\end{tabularx}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.total_tables == 1
        assert result.tables[0].table_type == "tabularx"

    def test_detects_longtable(self):
        """Test detection of longtable environment."""
        content = r"\begin{longtable}{|c|c|c|c|c|}\hline\end{longtable}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.total_tables == 1
        assert result.tables[0].table_type == "longtable"

    # Step 2: Check for Resizebox Wrapper

    def test_detects_resizebox_wrapper(self):
        """Test detection of resizebox wrapper."""
        content = r"""
\resizebox{\textwidth}{!}{%
\begin{tabular}{|c|c|c|c|c|}
\hline
\end{tabular}%
}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].has_resizebox is True
        assert result.tables[0].severity == "SAFE"

    def test_no_resizebox_detected(self):
        """Test detection when no resizebox present."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].has_resizebox is False

    def test_tabularx_textwidth_safe(self):
        """Test tabularx with textwidth is considered safe."""
        content = r"\begin{tabularx}{\textwidth}{|X|X|X|X|X|}\hline\end{tabularx}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].severity == "SAFE"
        assert result.tables[0].has_resizebox is True  # Treated as safe

    # Step 3: Count Columns

    def test_count_simple_columns(self):
        """Test counting simple columns (c, l, r)."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].columns == 5

    def test_count_mixed_columns(self):
        """Test counting mixed column types."""
        content = r"\begin{tabular}{|l|c|r|p{2cm}|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].columns == 4

    def test_count_p_columns(self):
        """Test counting p{width} columns."""
        content = r"\begin{tabular}{|p{2cm}|p{3cm}|p{4cm}|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].columns == 3

    def test_count_X_columns(self):
        """Test counting X columns in tabularx."""
        content = r"\begin{tabularx}{\linewidth}{|X|X|X|X|}\hline\end{tabularx}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].columns == 4

    # Detection Rules / Severity

    def test_critical_5_plus_columns_no_resizebox(self):
        """Test CRITICAL for 5+ columns without resizebox."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].severity == "CRITICAL"
        assert result.tables[0].columns >= 5

    def test_critical_6_plus_columns_no_resizebox(self):
        """Test CRITICAL for 6+ columns without resizebox."""
        content = r"\begin{tabular}{|l|l|l|l|l|l|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].severity == "CRITICAL"
        assert result.tables[0].columns >= 5

    def test_warning_4_columns_no_resizebox(self):
        """Test WARNING for 4 columns without resizebox."""
        content = r"\begin{tabular}{|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].severity == "WARNING"
        assert result.tables[0].columns == 4

    def test_safe_3_columns_no_resizebox(self):
        """Test SAFE for 3 columns without resizebox."""
        content = r"\begin{tabular}{|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].severity == "SAFE"

    def test_safe_with_resizebox(self):
        """Test SAFE when resizebox is present regardless of columns."""
        content = r"""
\resizebox{\textwidth}{!}{%
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\end{tabular}%
}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables[0].severity == "SAFE"

    # Verdict and Triggers

    def test_verdict_fail_on_critical(self):
        """Test verdict is FAIL when CRITICAL issues exist."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.verdict == "FAIL"

    def test_verdict_warning_on_warning(self):
        """Test verdict is WARNING when only WARNING issues exist."""
        content = r"\begin{tabular}{|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.verdict == "WARNING"

    def test_verdict_pass_on_safe(self):
        """Test verdict is PASS when all tables are safe."""
        content = r"\begin{tabular}{|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.verdict == "PASS"

    def test_triggers_on_unsafe(self):
        """Test triggers generated when unsafe tables found."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert "qa-table-overflow-fix" in result.triggers

    def test_no_triggers_on_safe(self):
        """Test no triggers when all tables are safe."""
        content = r"\begin{tabular}{|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.triggers == []

    # Output Format

    def test_output_format(self):
        """Test output format matches skill.md specification."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-table-overflow-detect"
        assert output["status"] == "DONE"
        assert "verdict" in output
        assert "tables" in output
        assert "summary" in output
        assert "triggers" in output

        # Check table entry format
        table_entry = output["tables"][0]
        assert "file" in table_entry
        assert "line" in table_entry
        assert "type" in table_entry
        assert "columns" in table_entry
        assert "has_resizebox" in table_entry
        assert "severity" in table_entry
        assert "fix" in table_entry

        # Check summary format
        assert "total_tables" in output["summary"]
        assert "unsafe" in output["summary"]
        assert "safe" in output["summary"]

    def test_fix_suggestion(self):
        """Test fix suggestion is provided for unsafe tables."""
        content = r"\begin{tabular}{|c|c|c|c|c|}\hline\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert "resizebox" in result.tables[0].fix.lower()

    def test_get_rules(self):
        """Test get_rules returns all detection rules."""
        rules = self.detector.get_rules()
        assert "5+_columns_no_resizebox" in rules
        assert "4_columns_no_resizebox" in rules
        assert "any_with_resizebox" in rules
        assert "tabularx_textwidth" in rules

    # Summary Counts

    def test_summary_counts(self):
        """Test summary counts are correct."""
        content = r"""
\begin{tabular}{|c|c|c|c|c|}
\hline
\end{tabular}
\begin{tabular}{|c|c|c|}
\hline
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.total_tables == 2
        assert result.unsafe == 1  # 5 columns
        assert result.safe == 1    # 3 columns

    def test_no_tables_returns_empty(self):
        """Test content without tables returns empty result."""
        content = r"Some text without tables."
        result = self.detector.detect_content(content, "test.tex")
        assert result.total_tables == 0
        assert result.verdict == "PASS"
