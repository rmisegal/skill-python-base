"""
Tests for CaptionLengthDetector.

Tests all caption length detection rules for identifying
descriptions used as figure/table titles.
"""

import pytest

from qa_engine.domain.models.issue import Severity
from qa_engine.infrastructure.detection.caption_length_detector import CaptionLengthDetector


class TestCaptionLengthDetector:
    """Tests for CaptionLengthDetector."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = CaptionLengthDetector()

    def test_get_rules_returns_all_rules(self):
        """Test get_rules returns all expected rules."""
        rules = self.detector.get_rules()
        assert len(rules) >= 3
        assert "caption-too-long" in rules
        assert "caption-description-pattern" in rules
        assert "caption-multi-sentence" in rules

    # Rule 1: Caption too long
    def test_rule1_caption_too_long_detected(self):
        """Test detection of captions exceeding max length."""
        # Caption over 100 chars without short title
        long_caption = "A" * 120
        content = f"\\caption{{{long_caption}}}"
        issues = self.detector.detect(content, "test.tex")
        long_issues = [i for i in issues if i.rule == "caption-too-long"]
        assert len(long_issues) > 0

    def test_rule1_caption_with_short_title_no_issue(self):
        """Test no issue when caption has short title."""
        long_caption = "A" * 120
        content = f"\\caption[Short Title]{{{long_caption}}}"
        issues = self.detector.detect(content, "test.tex")
        long_issues = [i for i in issues if i.rule == "caption-too-long"]
        assert len(long_issues) == 0

    def test_rule1_short_caption_no_issue(self):
        """Test no issue for short captions."""
        content = "\\caption{Short title}"
        issues = self.detector.detect(content, "test.tex")
        long_issues = [i for i in issues if i.rule == "caption-too-long"]
        assert len(long_issues) == 0

    # Rule 2: Caption with description pattern (colon)
    def test_rule2_colon_pattern_detected(self):
        """Test detection of title: description pattern."""
        content = "\\caption{Architecture Overview: This diagram shows the complete system " \
                  "architecture with all components and their interactions.}"
        issues = self.detector.detect(content, "test.tex")
        desc_issues = [i for i in issues if i.rule == "caption-description-pattern"]
        assert len(desc_issues) > 0

    def test_rule2_colon_with_short_title_no_issue(self):
        """Test no issue when has short title already."""
        content = "\\caption[Architecture Overview]{Architecture Overview: Full description here.}"
        issues = self.detector.detect(content, "test.tex")
        desc_issues = [i for i in issues if i.rule == "caption-description-pattern"]
        assert len(desc_issues) == 0

    # Rule 3: Multi-sentence caption
    def test_rule3_multi_sentence_detected(self):
        """Test detection of multi-sentence captions."""
        content = "\\caption{This is the first sentence. This is the second sentence explaining more.}"
        issues = self.detector.detect(content, "test.tex")
        multi_issues = [i for i in issues if i.rule == "caption-multi-sentence"]
        assert len(multi_issues) > 0

    # General tests
    def test_skip_comment_lines(self):
        """Test that comment lines are skipped."""
        content = "% \\caption{Very long caption text that would trigger detection " + "A" * 100 + "}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 0

    def test_non_tex_file_skipped(self):
        """Test that non-tex files are skipped."""
        content = "\\caption{Very long caption " + "A" * 100 + "}"
        issues = self.detector.detect(content, "test.py")
        assert len(issues) == 0

    def test_offset_parameter(self):
        """Test line offset is applied correctly."""
        long_caption = "A" * 120
        content = f"\\caption{{{long_caption}}}"
        issues = self.detector.detect(content, "test.tex", offset=100)
        assert len(issues) > 0
        assert issues[0].line == 101

    def test_suggested_short_title_colon_split(self):
        """Test short title extraction from colon pattern."""
        content = "\\caption{System Architecture: This shows the complete architecture with " \
                  "all components and their connections and interactions.}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) > 0
        context = issues[0].context
        assert "suggested_short_title" in context
        assert context["suggested_short_title"] == "System Architecture"

    def test_suggested_short_title_sentence_split(self):
        """Test short title extraction from first sentence."""
        content = "\\caption{System Architecture Overview. This diagram shows the complete " \
                  "system with all components and their interactions shown clearly.}"
        issues = self.detector.detect(content, "test.tex")
        # Should detect multi-sentence
        multi_issues = [i for i in issues if i.rule == "caption-multi-sentence"]
        assert len(multi_issues) > 0

    def test_hebrew_caption_detected(self):
        """Test detection of long Hebrew captions."""
        # Hebrew caption with description pattern
        content = "\\caption{ארכיטקטורת המערכת: הסבר מפורט על כל הרכיבים והקשרים ביניהם " \
                  "ותפקידם בתהליך העבודה הכולל של המערכת.}"
        issues = self.detector.detect(content, "test.tex")
        # Should detect description pattern
        assert len(issues) > 0

    def test_caption_length_in_context(self):
        """Test that caption length is included in context."""
        long_caption = "A" * 120
        content = f"\\caption{{{long_caption}}}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) > 0
        context = issues[0].context
        assert "caption_length" in context
        assert context["caption_length"] == 120

    # Tests for nested brace handling
    def test_nested_braces_en_command_detected(self):
        """Test detection of long captions with nested \\en{} commands."""
        content = r"\caption{Long Hebrew caption with \en{English text} inside. " \
                  r"This continues with more text and \en{more English} to make it very long.}"
        issues = self.detector.detect(content, "test.tex")
        # Should detect multi-sentence or too-long
        assert len(issues) > 0
        # Check that full caption text was captured
        caption_len = issues[0].context.get("caption_length", 0)
        assert caption_len > 80  # Should capture full length

    def test_nested_braces_num_command_detected(self):
        """Test detection of captions with \\num{} commands."""
        content = r"\caption{Risk chart showing OWASP Top \num{10}. Risks rated from \num{1} " \
                  r"to \num{10} with critical being above \num{8.5}.}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) > 0
        # Verify full caption was captured (not broken at first })
        caption_text = issues[0].context.get("caption_text", "")
        assert "\\num{10}" in caption_text or "num{10}" in caption_text

    def test_nested_braces_multiple_levels(self):
        """Test detection with multiple nesting levels."""
        content = r"\caption{Figure showing \en{AI \num{2025}} architecture. " \
                  r"The system uses \en{LLM} for processing and \en{Agent} for action execution.}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) > 0

    def test_nested_braces_math_mode(self):
        """Test detection of captions with math mode containing braces."""
        content = r"\caption{Risk severity: critical risks have score $\geq\en{8.5}$. " \
                  r"Medium risks are below $<\en{7.5}$ and require standard controls.}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) > 0

    def test_nested_braces_hebrew_with_en(self):
        """Test detection of Hebrew captions with nested \\en{} commands."""
        content = r"\caption{משטח התקיפה של סוכן \en{AI} אוטונומי. " \
                  r"בניגוד ל\en{-LLM} שחשוף דרך קלט טקסטואלי, סוכן חשוף לשמונה וקטורי תקיפה.}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) > 0
        # Check caption was fully captured
        caption_len = issues[0].context.get("caption_length", 0)
        assert caption_len > 100

    def test_short_caption_with_nested_braces_no_issue(self):
        """Test that short captions with nested braces don't trigger false positives."""
        content = r"\caption{Simple \en{AI} diagram}"
        issues = self.detector.detect(content, "test.tex")
        # Short caption should not trigger caption-too-long
        long_issues = [i for i in issues if i.rule == "caption-too-long"]
        assert len(long_issues) == 0
