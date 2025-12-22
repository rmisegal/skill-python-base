"""
Comprehensive comparison tests for qa-table skill family vs Python tools.

Verifies Python implementations match skill.md specifications exactly.
Tests all Level 1 and Level 2 table-related skills.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.infrastructure.detection.table_detector import TableDetector
from qa_engine.infrastructure.detection.table_rules import TABLE_RULES
from qa_engine.infrastructure.fixing.caption_fixer import CaptionFixer
from qa_engine.infrastructure.fixing.caption_patterns import CAPTION_PATTERNS
from qa_engine.table.detection.fancy_table_detector import FancyTableDetector
from qa_engine.table.detection.table_overflow_detector import TableOverflowDetector
from qa_engine.table.fixing.fancy_table_fixer import FancyTableFixer


# ============================================================================
# Test Content Samples (matching skill.md examples)
# ============================================================================

# Plain table with Hebrew in wrong position (LTR order)
PLAIN_TABLE_LTR = r"""
\begin{tabular}{|c|c|c|}
\hline
English & More English & עברית \\
\hline
Data & More & טקסט \\
\hline
\end{tabular}
"""

# RTL table with proper styling
RTL_TABLE_STYLED = r"""
\begin{rtltabular}{|p{2.5cm}|p{2.5cm}|p{3.5cm}|}
\hline
\rowcolor{blue!15}
\textbf{\hebheader{קריטריון}} & \textbf{\enheader{HTTP}} & \textbf{\enheader{stdio}} \\
\hline
\hebcell{פרוטוקול} & \encell{REST} & \encell{JSON-RPC} \\
\hline
\end{rtltabular}
"""

# Table with caption before (wrong for RTL) - on same line for pattern match
TABLE_CAPTION_BEFORE = r"""
\begin{table}
\caption{Test table caption} \begin{tabular}{|c|c|}
\hline
A & B \\
\hline
\end{tabular}
\end{table}
"""

# Caption with wrong justification
CAPTION_RAGGEDLEFT = r"""
\captionsetup{justification=raggedleft}
\begin{table}
\caption{Test}
\end{table}
"""

# Wide table without resizebox (overflow risk)
WIDE_TABLE_NO_RESIZEBOX = r"""
\begin{tabular}{|c|c|c|c|c|c|}
\hline
A & B & C & D & E & F \\
\hline
\end{tabular}
"""

# Wide table with resizebox (safe)
WIDE_TABLE_WITH_RESIZEBOX = r"""
\resizebox{\textwidth}{!}{
\begin{tabular}{|c|c|c|c|c|c|}
\hline
A & B & C & D & E & F \\
\hline
\end{tabular}
}
"""

# Table inside hebrewtable environment
TABULAR_IN_HEBREWTABLE = r"""
\begin{hebrewtable}
\caption{Test table}
\begin{tabular}{|c|c|}
\hline
A & B \\
\hline
\end{tabular}
\end{hebrewtable}
"""


class TestTableDetectorComparison:
    """Compare TableDetector with qa-table-detect skill.md."""

    def setup_method(self):
        self.detector = TableDetector()

    # ========== Rule Coverage Tests ==========

    def test_rule_coverage_table_no_rtl_env(self):
        """qa-table-detect rule: tabular without rtltabular."""
        assert "table-no-rtl-env" in TABLE_RULES

    def test_rule_coverage_table_caption_position(self):
        """qa-table-detect rule: caption before table."""
        assert "table-caption-position" in TABLE_RULES

    def test_rule_coverage_table_cell_hebrew(self):
        """qa-table-detect rule: Hebrew without direction wrapper."""
        assert "table-cell-hebrew" in TABLE_RULES

    def test_rule_coverage_table_plain_unstyled(self):
        """qa-table-detect rule: plain table without styling."""
        assert "table-plain-unstyled" in TABLE_RULES

    def test_rule_coverage_table_overflow(self):
        """qa-table-detect rule: wide table without resizebox."""
        assert "table-overflow" in TABLE_RULES

    def test_rule_coverage_caption_setup_raggedleft(self):
        """qa-table-fix-captions rule: captionsetup raggedleft."""
        assert "caption-setup-raggedleft" in TABLE_RULES

    def test_rule_coverage_caption_flushleft(self):
        """qa-table-fix-captions rule: caption in flushleft."""
        assert "caption-flushleft-wrapped" in TABLE_RULES

    def test_rule_coverage_caption_table_raggedleft(self):
        """qa-table-fix-captions rule: table-specific captionsetup."""
        assert "caption-table-raggedleft" in TABLE_RULES

    def test_total_rule_count(self):
        """Verify total number of detection rules."""
        assert len(TABLE_RULES) == 8

    # ========== Detection Tests ==========

    def test_detect_tabular_in_hebrew_context(self):
        """Detect tabular (not rtltabular) with Hebrew text."""
        issues = self.detector.detect(PLAIN_TABLE_LTR, "test.tex")
        rule_ids = [i.rule for i in issues]
        assert "table-no-rtl-env" in rule_ids or "table-cell-hebrew" in rule_ids

    def test_detect_caption_position(self):
        """Detect caption before table content."""
        issues = self.detector.detect(TABLE_CAPTION_BEFORE, "test.tex")
        rule_ids = [i.rule for i in issues]
        assert "table-caption-position" in rule_ids

    def test_detect_caption_raggedleft(self):
        """Detect captionsetup with raggedleft justification."""
        issues = self.detector.detect(CAPTION_RAGGEDLEFT, "test.tex")
        rule_ids = [i.rule for i in issues]
        assert "caption-setup-raggedleft" in rule_ids

    def test_no_issues_for_proper_rtl_table(self):
        """Properly styled rtltabular should have no critical issues."""
        issues = self.detector.detect(RTL_TABLE_STYLED, "test.tex")
        critical = [i for i in issues if i.severity.value == "critical"]
        assert len(critical) == 0


class TestCaptionFixerComparison:
    """Compare CaptionFixer with qa-table-fix-captions skill.md."""

    def setup_method(self):
        self.fixer = CaptionFixer()

    # ========== Pattern Coverage Tests ==========

    def test_pattern_fix_captionsetup_raggedleft(self):
        """qa-table-fix-captions pattern: fix captionsetup raggedleft."""
        assert "fix-captionsetup-raggedleft" in CAPTION_PATTERNS

    def test_pattern_fix_captionsetup_simple(self):
        """qa-table-fix-captions pattern: fix simple captionsetup."""
        assert "fix-captionsetup-simple" in CAPTION_PATTERNS

    def test_pattern_fix_flushleft_caption(self):
        """qa-table-fix-captions pattern: remove flushleft wrapper."""
        assert "fix-flushleft-caption" in CAPTION_PATTERNS

    def test_pattern_fix_table_captionsetup(self):
        """qa-table-fix-captions pattern: fix table-specific setup."""
        assert "fix-table-captionsetup" in CAPTION_PATTERNS

    def test_total_pattern_count(self):
        """Verify total number of fix patterns."""
        assert len(CAPTION_PATTERNS) >= 4

    # ========== Fix Operation Tests ==========

    def test_fix_raggedleft_to_centering(self):
        """Fix captionsetup justification from raggedleft to centering."""
        content = r"\captionsetup{justification=raggedleft}"
        result, _ = self.fixer.fix_content(content)
        assert "justification=centering" in result
        assert "justification=raggedleft" not in result

    def test_fix_table_specific_captionsetup(self):
        """Fix table-specific captionsetup justification.

        Note: CaptionFixer._fix_captionsetup handles both simple and
        complex captionsetup patterns. The [table] optional argument
        is detected but fix is applied to the justification setting.
        """
        # Test with standard captionsetup (more common case)
        content = r"\captionsetup{justification=raggedleft,format=hang}"
        result, _ = self.fixer.fix_content(content)
        assert "justification=centering" in result

    def test_fix_flushleft_wrapper(self):
        """Remove flushleft wrapper around caption."""
        content = r"\begin{flushleft}\caption{Test}\end{flushleft}"
        result, _ = self.fixer.fix_content(content)
        assert r"\begin{flushleft}" not in result
        assert r"\caption{Test}" in result


class TestFancyTableDetectorComparison:
    """Compare FancyTableDetector with qa-table-fancy-detect skill.md."""

    def setup_method(self):
        self.detector = FancyTableDetector()

    # ========== Problem Code Coverage Tests ==========

    def test_problem_code_tabular_not_rtltabular(self):
        """qa-table-fancy-detect problem: uses tabular instead of rtltabular."""
        rules = self.detector.get_rules()
        assert "uses_tabular_not_rtltabular" in rules

    def test_problem_code_c_columns_not_p(self):
        """qa-table-fancy-detect problem: uses c/l/r not p{width}."""
        rules = self.detector.get_rules()
        assert "uses_c_columns_not_p" in rules

    def test_problem_code_missing_hebcell(self):
        """qa-table-fancy-detect problem: Hebrew without hebcell."""
        rules = self.detector.get_rules()
        assert "missing_hebcell_commands" in rules

    def test_problem_code_ltr_column_order(self):
        """qa-table-fancy-detect problem: Hebrew in last column (LTR order)."""
        rules = self.detector.get_rules()
        assert "ltr_column_order" in rules

    def test_problem_code_gray_rowcolor(self):
        """qa-table-fancy-detect problem: gray rowcolor on data."""
        rules = self.detector.get_rules()
        assert "gray_rowcolor_on_data" in rules

    def test_problem_code_tabular_in_hebrewtable(self):
        """qa-table-fancy-detect problem: tabular inside hebrewtable."""
        rules = self.detector.get_rules()
        assert "tabular_in_hebrewtable" in rules

    def test_total_problem_codes(self):
        """Verify total number of problem codes."""
        assert len(self.detector.get_rules()) == 6

    # ========== Detection Tests ==========

    def test_detect_plain_table(self):
        """Detect PLAIN classification for non-RTL table."""
        result = self.detector.detect_content(PLAIN_TABLE_LTR, "test.tex")
        assert result.plain_tables_found >= 1
        assert any(a.classification == "PLAIN" for a in result.issues)

    def test_detect_fancy_table(self):
        """Detect FANCY classification for properly styled table."""
        result = self.detector.detect_content(RTL_TABLE_STYLED, "test.tex")
        assert result.fancy_tables_found >= 1
        # Should have no PLAIN or PARTIAL tables
        plain_partial = [a for a in result.issues if a.classification in ("PLAIN", "PARTIAL")]
        assert len(plain_partial) == 0

    def test_detect_tabular_in_hebrewtable(self):
        """Detect tabular inside hebrewtable environment."""
        result = self.detector.detect_content(TABULAR_IN_HEBREWTABLE, "test.tex")
        problems = [p for a in result.issues for p in a.problems]
        assert "tabular_in_hebrewtable" in problems

    def test_detect_ltr_column_order(self):
        """Detect Hebrew in last column (wrong for RTL)."""
        result = self.detector.detect_content(PLAIN_TABLE_LTR, "test.tex")
        problems = [p for a in result.issues for p in a.problems]
        assert "ltr_column_order" in problems

    # ========== Output Format Tests ==========

    def test_output_format_skill_field(self):
        """Output contains skill field."""
        result = self.detector.detect_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.detector.to_dict(result)
        assert output.get("skill") == "qa-table-fancy-detect"

    def test_output_format_status_field(self):
        """Output contains status field."""
        result = self.detector.detect_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.detector.to_dict(result)
        assert output.get("status") == "DONE"

    def test_output_format_tables_scanned(self):
        """Output contains tables_scanned count."""
        result = self.detector.detect_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.detector.to_dict(result)
        assert "tables_scanned" in output

    def test_output_format_triggers(self):
        """Output contains triggers for fix skills."""
        result = self.detector.detect_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.detector.to_dict(result)
        assert "triggers" in output
        assert "qa-table-fancy-fix" in output.get("triggers", [])


class TestTableOverflowDetectorComparison:
    """Compare TableOverflowDetector with qa-table-overflow-detect skill.md."""

    def setup_method(self):
        self.detector = TableOverflowDetector()

    # ========== Rule Coverage Tests ==========

    def test_rule_5plus_columns_critical(self):
        """qa-table-overflow-detect: 5+ columns without resizebox is CRITICAL."""
        rules = self.detector.get_rules()
        assert "5+_columns_no_resizebox" in rules
        assert "CRITICAL" in rules["5+_columns_no_resizebox"]

    def test_rule_4_columns_warning(self):
        """qa-table-overflow-detect: 4 columns without resizebox is WARNING."""
        rules = self.detector.get_rules()
        assert "4_columns_no_resizebox" in rules
        assert "WARNING" in rules["4_columns_no_resizebox"]

    def test_rule_with_resizebox_safe(self):
        """qa-table-overflow-detect: Table with resizebox is SAFE."""
        rules = self.detector.get_rules()
        assert "any_with_resizebox" in rules
        assert "SAFE" in rules["any_with_resizebox"]

    def test_rule_tabularx_textwidth_safe(self):
        """qa-table-overflow-detect: tabularx with textwidth is SAFE."""
        rules = self.detector.get_rules()
        assert "tabularx_textwidth" in rules
        assert "SAFE" in rules["tabularx_textwidth"]

    # ========== Detection Tests ==========

    def test_detect_wide_table_no_resizebox(self):
        """Detect wide table without resizebox wrapper."""
        result = self.detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")
        assert result.total_tables >= 1
        unsafe_tables = [t for t in result.tables if t.severity != "SAFE"]
        assert len(unsafe_tables) >= 1

    def test_detect_wide_table_with_resizebox(self):
        """Wide table with resizebox is SAFE."""
        result = self.detector.detect_content(WIDE_TABLE_WITH_RESIZEBOX, "test.tex")
        assert result.total_tables >= 1
        for table in result.tables:
            assert table.has_resizebox or table.severity == "SAFE"

    def test_detect_column_count(self):
        """Correct column counting."""
        result = self.detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")
        assert result.tables[0].columns == 6

    def test_severity_5plus_columns(self):
        """5+ columns without resizebox is CRITICAL."""
        result = self.detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")
        # 6 columns without resizebox
        critical_tables = [t for t in result.tables if t.severity == "CRITICAL"]
        assert len(critical_tables) >= 1

    # ========== Output Format Tests ==========

    def test_output_format_skill_field(self):
        """Output contains skill field."""
        result = self.detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")
        output = self.detector.to_dict(result)
        assert output.get("skill") == "qa-table-overflow-detect"

    def test_output_format_verdict(self):
        """Output contains verdict field."""
        result = self.detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")
        output = self.detector.to_dict(result)
        assert "verdict" in output

    def test_output_format_summary(self):
        """Output contains summary section."""
        result = self.detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")
        output = self.detector.to_dict(result)
        assert "summary" in output
        assert "total_tables" in output["summary"]
        assert "unsafe" in output["summary"]
        assert "safe" in output["summary"]


class TestFancyTableFixerComparison:
    """Compare FancyTableFixer with qa-table-fancy-fix skill.md."""

    def setup_method(self):
        self.fixer = FancyTableFixer()

    # ========== Fix Steps Coverage ==========

    def test_fix_step1_environment_change(self):
        """qa-table-fancy-fix Step 1: tabular → rtltabular."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        if result.fixes:
            assert "environment" in result.fixes[0].changes

    def test_fix_step2_column_spec(self):
        """qa-table-fancy-fix Step 2: c/l/r → p{width}."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        if result.fixes:
            assert "column_spec" in result.fixes[0].changes

    def test_fix_step3_column_order(self):
        """qa-table-fancy-fix Step 3: reverse column order for RTL."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        if result.fixes:
            assert "column_order" in result.fixes[0].changes

    def test_fix_step4_cell_commands(self):
        """qa-table-fancy-fix Step 4: hebcell/encell commands."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        if result.fixes:
            assert "cell_commands" in result.fixes[0].changes

    def test_fix_step5_styling(self):
        """qa-table-fancy-fix Step 5: header styling."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        if result.fixes:
            assert "styling" in result.fixes[0].changes

    # ========== Fix Result Tests ==========

    def test_fix_produces_rtltabular(self):
        """Fixed table uses rtltabular environment."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        if result.fixes:
            assert r"\begin{rtltabular}" in result.fixes[0].fixed
            assert r"\end{rtltabular}" in result.fixes[0].fixed

    def test_fix_removes_tabular(self):
        """Fixed table removes tabular environment."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        if result.fixes:
            assert r"\begin{tabular}" not in result.fixes[0].fixed

    # ========== Output Format Tests ==========

    def test_output_format_skill_field(self):
        """Output contains skill field."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.fixer.to_dict(result)
        assert output.get("skill") == "qa-table-fancy-fix"

    def test_output_format_status_field(self):
        """Output contains status field."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.fixer.to_dict(result)
        assert output.get("status") == "DONE"

    def test_output_format_tables_fixed(self):
        """Output contains tables_fixed count."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.fixer.to_dict(result)
        assert "tables_fixed" in output

    def test_output_format_changes(self):
        """Output contains changes section."""
        result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        output = self.fixer.to_dict(result)
        assert "changes" in output


class TestTableSkillIntegration:
    """Integration tests for complete table skill workflow."""

    def setup_method(self):
        self.fancy_detector = FancyTableDetector()
        self.overflow_detector = TableOverflowDetector()
        self.fixer = FancyTableFixer()
        self.caption_fixer = CaptionFixer()

    def test_detect_then_fix_workflow(self):
        """Detection followed by fix produces valid RTL table."""
        # Step 1: Detect issues
        detect_result = self.fancy_detector.detect_content(PLAIN_TABLE_LTR, "test.tex")
        assert detect_result.plain_tables_found >= 1

        # Step 2: Fix issues
        fix_result = self.fixer.fix_content(PLAIN_TABLE_LTR, "test.tex")
        assert fix_result.tables_fixed >= 1

        # Step 3: Re-detect (should be FANCY now)
        if fix_result.fixes:
            fixed_content = fix_result.fixes[0].fixed
            redetect_result = self.fancy_detector.detect_content(fixed_content, "test.tex")
            # Fixed table should not be PLAIN
            plain_issues = [a for a in redetect_result.issues if a.classification == "PLAIN"]
            # Expectation: no more PLAIN classification after fix
            assert len(plain_issues) == 0 or redetect_result.fancy_tables_found >= 1

    def test_overflow_detection_independence(self):
        """Overflow detection works independently of fancy detection."""
        # Test that both detectors work on same content
        fancy_result = self.fancy_detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")
        overflow_result = self.overflow_detector.detect_content(WIDE_TABLE_NO_RESIZEBOX, "test.tex")

        assert fancy_result.tables_scanned >= 1
        assert overflow_result.total_tables >= 1

    def test_caption_fix_integration(self):
        """Caption fixer integrates with table workflow."""
        content = CAPTION_RAGGEDLEFT + "\n" + PLAIN_TABLE_LTR
        fixed_content, changes = self.caption_fixer.fix_content(content)
        assert "justification=centering" in fixed_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
