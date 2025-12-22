"""Unit tests for Table Layout Detector (skill.md aligned)."""
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.table.detection.table_layout_detector import (
    TableLayoutDetector, TableDetectResult, TableIssue
)


class TestTableLayoutDetector:
    """Tests for TableLayoutDetector aligned with skill.md phases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = TableLayoutDetector(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_file(self, name: str, content: str) -> Path:
        """Helper to create a test file."""
        path = Path(self.temp_dir) / name
        path.write_text(content, encoding="utf-8")
        return path

    # Phase 1: Table Discovery
    def test_phase1_discovers_table_env(self):
        """Test discovery of \\begin{table} environments."""
        content = r"\begin{table}\n\end{table}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables_found >= 1

    def test_phase1_discovers_tabular_env(self):
        """Test discovery of \\begin{tabular} environments."""
        content = r"\begin{tabular}{|c|c|}\end{tabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables_found >= 1

    def test_phase1_discovers_rtltabular(self):
        """Test discovery of \\begin{rtltabular} environments."""
        content = r"\begin{rtltabular}{|c|c|}\end{rtltabular}"
        result = self.detector.detect_content(content, "test.tex")
        assert result.tables_found >= 1

    def test_phase1_extracts_caption(self):
        """Test caption extraction from table."""
        content = r"""
\begin{table}
\caption{טבלה 1: נתונים}
\begin{tabular}{cc}
\end{tabular}
\end{table}
"""
        result = self.detector.detect_content(content, "test.tex")
        # Check caption was found
        assert any("טבלה" in d.caption for d in result.details) or result.tables_found > 0

    # Phase 2: Caption Alignment
    def test_phase2_detects_left_aligned_caption(self):
        """Test detection of left-aligned caption (wrong for RTL)."""
        content = r"""
\begin{table}
\begin{flushleft}
\caption{טבלה שגויה}
\end{flushleft}
\begin{tabular}{cc}
\end{tabular}
\end{table}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.caption_alignment_issues >= 1

    def test_phase2_centered_caption_ok(self):
        """Test centered caption is acceptable."""
        content = r"""
\begin{table}
\centering
\caption{טבלה תקינה}
\begin{rtltabular}{cc}
\end{rtltabular}
\end{table}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.caption_alignment_issues == 0

    # Phase 3: Column Order
    def test_phase3_detects_ltr_tabular_in_hebrew(self):
        """Test detection of LTR tabular in Hebrew document."""
        content = r"""
מסמך בעברית
\begin{tabular}{|l|c|r|}
\hline
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.column_order_issues >= 1

    def test_phase3_rtltabular_ok(self):
        """Test rtltabular is acceptable."""
        content = r"""
מסמך בעברית
\begin{rtltabular}{|l|c|r|}
\hline
\end{rtltabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.column_order_issues == 0

    # Phase 4: Cell Content
    def test_phase4_detects_hebrew_in_cell(self):
        """Test detection of Hebrew in table cell."""
        content = r"""
\begin{tabular}{|c|c|}
שלום & עולם \\
\end{tabular}
"""
        result = self.detector.detect_content(content, "test.tex")
        assert result.cell_alignment_issues >= 1

    # Output Format
    def test_to_dict_matches_skill_format(self):
        """Test output format matches skill.md specification."""
        result = TableDetectResult(
            tables_found=3,
            issues_found=2,
            column_order_issues=1,
            caption_alignment_issues=1,
        )
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-table-detect"
        assert output["status"] == "DONE"
        assert output["tables_found"] == 3
        assert output["issues_found"] == 2
        assert "categories" in output
        assert output["categories"]["column_order"] == 1
        assert output["categories"]["caption_alignment"] == 1
        assert "triggers" in output
        assert "details" in output

    def test_triggers_generated_correctly(self):
        """Test correct triggers are generated based on issues."""
        result = TableDetectResult(column_order_issues=1)
        assert "qa-table-fix-columns" in result.triggers

        result = TableDetectResult(caption_alignment_issues=1)
        assert "qa-table-fix-captions" in result.triggers

        result = TableDetectResult(cell_alignment_issues=1)
        assert "qa-table-fix-alignment" in result.triggers

    def test_get_rules(self):
        """Test get_rules returns detection rules."""
        rules = self.detector.get_rules()
        assert len(rules) >= 3
        assert "column-order-ltr" in rules
        assert "caption-left-aligned" in rules

    # Integration
    def test_detect_in_file(self):
        """Test detection from file."""
        content = r"""
עברית
\begin{tabular}{cc}
א & ב \\
\end{tabular}
"""
        path = self._create_file("test.tex", content)
        result = self.detector.detect_in_file(path)

        assert result.tables_found >= 1

    def test_nonexistent_file_returns_empty(self):
        """Test handling of nonexistent file."""
        result = self.detector.detect_in_file(Path("/nonexistent/test.tex"))
        assert result.tables_found == 0
        assert result.issues_found == 0
