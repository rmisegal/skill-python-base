"""Unit tests for VboxFixer aligned with qa-typeset-fix-vbox skill.md v1.0."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.typeset.fixing import VboxFixer, VboxFixResult, VboxFix, VboxManualReview


class TestVboxFixer:
    """Tests for VboxFixer aligned with skill.md."""

    def setup_method(self):
        self.fixer = VboxFixer()

    # Severity Classification Tests

    def test_severity_overfull_critical(self):
        """Test overfull vbox is always CRITICAL."""
        assert self.fixer.classify_severity(is_overfull=True) == "CRITICAL"

    def test_severity_badness_low_info(self):
        """Test badness < 1000 is INFO."""
        assert self.fixer.classify_severity(badness=500) == "INFO"

    def test_severity_badness_consider_info(self):
        """Test badness 1000-5000 is INFO (consider)."""
        assert self.fixer.classify_severity(badness=3000) == "INFO"

    def test_severity_badness_should_fix_warning(self):
        """Test badness 5000-9999 is WARNING."""
        assert self.fixer.classify_severity(badness=7000) == "WARNING"

    def test_severity_badness_10000_warning(self):
        """Test badness 10000 is WARNING."""
        assert self.fixer.classify_severity(badness=10000) == "WARNING"

    # Option B: Raggedbottom (Global Fix)

    def test_fix_preamble_adds_raggedbottom(self):
        """Test raggedbottom is added to preamble."""
        content = r"""\documentclass{book}
\usepackage{graphicx}
\begin{document}
Hello
\end{document}"""
        fixed, result = self.fixer.fix_preamble(content, "test.tex")
        assert "\\raggedbottom" in fixed
        assert len(result.fixes_applied) == 1
        assert result.fixes_applied[0].fix_type == "raggedbottom"

    def test_fix_preamble_skips_existing(self):
        """Test raggedbottom is not duplicated."""
        content = r"""\documentclass{book}
\raggedbottom
\begin{document}
Hello
\end{document}"""
        fixed, result = self.fixer.fix_preamble(content, "test.tex")
        assert fixed.count("\\raggedbottom") == 1
        assert len(result.fixes_applied) == 0

    # Option C: Add Vertical Space

    def test_add_vfill(self):
        """Test vfill is added correctly."""
        content = "Line 1\nLine 2\nLine 3"
        fixed, fix = self.fixer.add_vfill(content, 2, "test.tex")
        assert "\\vfill" in fixed
        assert fix.fix_type == "vfill"
        assert fix.issue_type == "underfull"

    def test_add_vspace(self):
        """Test vspace is added correctly."""
        content = "Line 1\nLine 2\nLine 3"
        fixed, fix = self.fixer.add_vspace(content, 2, "3cm", "test.tex")
        assert "\\vspace{3cm}" in fixed
        assert fix.fix_type == "vspace"

    # Option E: Enlargethispage

    def test_add_enlargethispage(self):
        """Test enlargethispage is added correctly."""
        content = "Line 1\nLine 2\nLine 3"
        fixed, fix = self.fixer.add_enlargethispage(content, 2, "2\\baselineskip", "test.tex")
        assert "\\enlargethispage{2\\baselineskip}" in fixed
        assert fix.fix_type == "enlargethispage"

    def test_add_enlargethispage_negative(self):
        """Test negative enlargethispage for overfull."""
        content = "Line 1\nLine 2\nLine 3"
        fixed, fix = self.fixer.add_enlargethispage(content, 2, "-1\\baselineskip", "test.tex")
        assert "\\enlargethispage{-1\\baselineskip}" in fixed

    # Option D: Float Placement

    def test_fix_float_placement_adds_option(self):
        """Test float placement option is added."""
        content = r"\begin{figure}\includegraphics{img}\end{figure}"
        fixed, fix = self.fixer.fix_float_placement(content, 1, "htbp", "test.tex")
        assert "[htbp]" in fixed
        assert fix.fix_type == "float_placement"

    def test_fix_float_placement_replaces_option(self):
        """Test float placement option is replaced."""
        content = r"\begin{figure}[h]\includegraphics{img}\end{figure}"
        fixed, fix = self.fixer.fix_float_placement(content, 1, "htbp", "test.tex")
        assert "[htbp]" in fixed
        assert "[h]" not in fixed

    def test_fix_float_placement_table(self):
        """Test float placement works on tables too."""
        content = r"\begin{table}\centering\end{table}"
        fixed, fix = self.fixer.fix_float_placement(content, 1, "p", "test.tex")
        assert "[p]" in fixed

    # Option A (Overfull): Newpage

    def test_add_newpage(self):
        """Test newpage is added correctly."""
        content = "Line 1\nLine 2\nLine 3"
        fixed, fix = self.fixer.add_newpage(content, 2, "test.tex")
        assert "\\newpage" in fixed
        assert fix.fix_type == "newpage"
        assert fix.issue_type == "overfull"

    # Manual Review Creation

    def test_create_review_underfull(self):
        """Test review creation for underfull vbox."""
        review = self.fixer.create_review("test.tex", 10, "underfull", badness=10000)
        assert review.issue_type == "underfull"
        assert "raggedbottom" in review.suggestion.lower() or "empty" in review.suggestion.lower()
        assert len(review.options) >= 4  # At least 4 options for underfull

    def test_create_review_overfull(self):
        """Test review creation for overfull vbox."""
        review = self.fixer.create_review("test.tex", 10, "overfull", amount_pt=5.2)
        assert review.issue_type == "overfull"
        assert "newpage" in " ".join(review.options).lower()
        assert len(review.options) >= 3  # At least 3 options for overfull

    # Global Settings

    def test_get_global_settings(self):
        """Test global settings are returned."""
        settings = self.fixer.get_global_settings()
        assert "raggedbottom" in settings
        assert "topfraction" in settings
        assert "bottomfraction" in settings
        assert "floatpagefraction" in settings

    # Should Ignore

    def test_should_ignore_chapter_start(self):
        """Test underfull at chapter start is safe to ignore."""
        assert self.fixer.should_ignore("underfull", badness=10000, context="\\chapter{Intro}")

    def test_should_ignore_after_newpage(self):
        """Test underfull after newpage is safe to ignore."""
        assert self.fixer.should_ignore("underfull", badness=10000, context="\\newpage")

    def test_should_ignore_low_badness(self):
        """Test low badness is safe to ignore."""
        assert self.fixer.should_ignore("underfull", badness=1000)

    def test_should_not_ignore_overfull(self):
        """Test overfull is never ignored."""
        assert not self.fixer.should_ignore("overfull")

    def test_should_not_ignore_high_badness(self):
        """Test high badness without special context is not ignored."""
        assert not self.fixer.should_ignore("underfull", badness=10000, context="Some text")

    # Output Format

    def test_to_dict_format(self):
        """Test output format matches skill.md spec."""
        result = VboxFixResult()
        result.fixes_applied.append(VboxFix(
            file="test.tex", line=10, issue_type="underfull",
            fix_type="raggedbottom", before="before", after="after"
        ))
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-typeset-fix-vbox"
        assert output["status"] == "DONE"
        assert "fixes_applied" in output
        assert "manual_review" in output
        assert "summary" in output
        assert output["summary"]["auto_fixed"] == 1

    def test_to_dict_manual_review(self):
        """Test manual review is included in output."""
        result = VboxFixResult()
        result.manual_review.append(VboxManualReview(
            file="test.tex", line=10, issue_type="overfull",
            badness=None, amount_pt=5.2, context="context",
            suggestion="fix it", options=["A", "B"]
        ))
        output = self.fixer.to_dict(result)

        assert output["status"] == "MANUAL_REVIEW"
        assert len(output["manual_review"]) == 1
        assert output["summary"]["needs_review"] == 1

    # Status Tests

    def test_status_done_with_fixes(self):
        """Test status is DONE when fixes applied."""
        result = VboxFixResult()
        result.fixes_applied.append(VboxFix(
            file="t.tex", line=1, issue_type="underfull",
            fix_type="vfill", before="b", after="a"
        ))
        assert result.status == "DONE"

    def test_status_manual_review(self):
        """Test status is MANUAL_REVIEW when reviews pending."""
        result = VboxFixResult()
        result.manual_review.append(VboxManualReview(
            file="t.tex", line=1, issue_type="overfull",
            badness=None, amount_pt=5.0, context="",
            suggestion="", options=[]
        ))
        assert result.status == "MANUAL_REVIEW"

    def test_status_no_changes(self):
        """Test status is NO_CHANGES when empty."""
        result = VboxFixResult()
        assert result.status == "NO_CHANGES"

    # LLM Prompt Generation

    def test_generate_llm_prompt(self):
        """Test LLM prompt generation."""
        review = VboxManualReview(
            file="test.tex", line=50, issue_type="underfull",
            badness=10000, amount_pt=None, context="Line context",
            suggestion="Add raggedbottom", options=["A", "B", "C"]
        )
        prompt = self.fixer.generate_llm_prompt(review)
        assert "underfull" in prompt
        assert "10000" in prompt
        assert "raggedbottom" in prompt.lower()
