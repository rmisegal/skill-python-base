"""
Tests for Table detector - RTL table issues.

Tests for table layout detection rules in Hebrew-English LaTeX.
"""

import pytest

from qa_engine.infrastructure.detection.table_detector import TableDetector


class TestTableDetector:
    """Tests for TableDetector."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = TableDetector()

    def test_get_rules_returns_all_rules(self):
        """Test get_rules returns expected rules."""
        rules = self.detector.get_rules()
        assert len(rules) >= 5
        assert "table-no-rtl-env" in rules
        assert "table-overflow" in rules

    # Rule 1: Table without RTL environment
    def test_rule1_tabular_in_hebrew_context(self):
        """Test detection of tabular without rtltabular in Hebrew doc."""
        content = "שלום\\n\\begin{tabular}{|c|c|}\\n...\\n\\end{tabular}"
        issues = self.detector.detect(content, "test.tex")
        rtl_issues = [i for i in issues if i.rule == "table-no-rtl-env"]
        assert len(rtl_issues) > 0

    def test_rule1_tabular_english_only_no_issue(self):
        """Test no issue when no Hebrew context."""
        content = "\\begin{tabular}{|c|c|}\\n...\\n\\end{tabular}"
        issues = self.detector.detect(content, "test.tex")
        rtl_issues = [i for i in issues if i.rule == "table-no-rtl-env"]
        assert len(rtl_issues) == 0

    # Rule 2: Caption position
    def test_rule2_caption_before_table(self):
        """Test detection of caption before tabular."""
        content = "\\caption{טבלה} \\begin{tabular}{cc}"
        issues = self.detector.detect(content, "test.tex")
        caption_issues = [i for i in issues if i.rule == "table-caption-position"]
        assert len(caption_issues) > 0

    # Rule 3: Hebrew in table cell
    def test_rule3_hebrew_in_cell(self):
        """Test detection of Hebrew text in table cell."""
        content = "col1 & שלום עולם & col3 \\\\"
        issues = self.detector.detect(content, "test.tex")
        cell_issues = [i for i in issues if i.rule == "table-cell-hebrew"]
        assert len(cell_issues) > 0

    def test_rule3_english_cell_no_issue(self):
        """Test no issue for English-only cells."""
        content = "col1 & hello world & col3 \\\\"
        issues = self.detector.detect(content, "test.tex")
        cell_issues = [i for i in issues if i.rule == "table-cell-hebrew"]
        assert len(cell_issues) == 0

    # Rule 4: Plain unstyled table
    def test_rule4_plain_tabular_in_hebrew(self):
        """Test detection of plain tabular in Hebrew document."""
        content = "מסמך עברי\\n\\begin{tabular}{|l|c|r|}"
        issues = self.detector.detect(content, "test.tex")
        plain_issues = [i for i in issues if i.rule == "table-plain-unstyled"]
        assert len(plain_issues) > 0

    # Rule 5: Wide table overflow
    def test_rule5_wide_table_without_resizebox(self):
        """Test detection of wide table without resizebox."""
        content = "\\begin{tabular}{|l|c|c|c|c|c|}"
        issues = self.detector.detect(content, "test.tex")
        overflow_issues = [i for i in issues if i.rule == "table-overflow"]
        assert len(overflow_issues) > 0

    def test_rule5_wide_table_with_resizebox_no_issue(self):
        """Test no issue when table is wrapped with resizebox."""
        content = "\\resizebox{\\textwidth}{!}{\\begin{tabular}{|l|c|c|c|c|c|}"
        issues = self.detector.detect(content, "test.tex")
        overflow_issues = [i for i in issues if i.rule == "table-overflow"]
        assert len(overflow_issues) == 0

    def test_rule5_narrow_table_no_issue(self):
        """Test no issue for narrow tables."""
        content = "\\begin{tabular}{|c|c|}"
        issues = self.detector.detect(content, "test.tex")
        overflow_issues = [i for i in issues if i.rule == "table-overflow"]
        assert len(overflow_issues) == 0

    # General tests
    def test_skip_comments(self):
        """Test that comment lines are skipped."""
        content = "% \\begin{tabular}{|c|c|c|c|c|c|}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 0

    def test_offset_parameter(self):
        """Test line offset is applied correctly."""
        content = "col1 & שלום & col3 \\\\"
        issues = self.detector.detect(content, "test.tex", offset=50)
        assert len(issues) > 0
        assert issues[0].line == 51
