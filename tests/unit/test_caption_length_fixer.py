"""
Tests for CaptionLengthFixer.

Tests caption length fixing - adding short titles for LOF/LOT.
"""

import pytest

from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.infrastructure.fixing.caption_length_fixer import (
    CaptionLengthFixer,
    CaptionLengthFix,
    CaptionLengthFixResult,
)


class TestCaptionLengthFixer:
    """Tests for CaptionLengthFixer."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = CaptionLengthFixer()

    def test_fix_adds_short_title_colon_pattern(self):
        """Test that short title is added based on colon pattern."""
        caption = "System Architecture: This diagram shows the complete system architecture"
        content = f"\\caption{{{caption}}}"

        issues = [Issue(
            rule="caption-description-pattern",
            file="test.tex",
            line=1,
            content=caption,
            severity=Severity.WARNING,
            context={
                "caption_text": caption,
                "suggested_short_title": "System Architecture",
            }
        )]

        fixed = self.fixer.fix(content, issues)
        assert "[System Architecture]" in fixed
        assert f"{{{caption}}}" in fixed

    def test_fix_content_auto_detect_mode(self):
        """Test fix_content auto-detects and fixes long captions."""
        long_text = "Long Caption Text: " + "A" * 100
        content = f"\\caption{{{long_text}}}"

        fixed, result = self.fixer.fix_content(content, "test.tex")

        assert result.fixes_applied > 0
        assert "[Long Caption Text]" in fixed

    def test_fix_preserves_existing_short_title(self):
        """Test that existing short titles are not modified."""
        content = "\\caption[Existing Title]{Long description text that goes on and on and on}"

        fixed, result = self.fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 0
        assert fixed == content

    def test_fix_skips_short_captions(self):
        """Test that short captions are not modified."""
        content = "\\caption{Short caption}"

        fixed, result = self.fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 0
        assert fixed == content

    def test_fix_skips_comments(self):
        """Test that commented lines are skipped."""
        long_text = "A" * 100
        content = f"% \\caption{{{long_text}}}"

        fixed, result = self.fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 0
        assert fixed == content

    def test_extract_short_title_colon(self):
        """Test short title extraction from colon pattern."""
        caption = "System Overview: This is a detailed description of the system"
        short = self.fixer._extract_short_title(caption)
        assert short == "System Overview"

    def test_extract_short_title_sentence(self):
        """Test short title extraction from first sentence."""
        caption = "System Architecture Overview. This shows all components."
        short = self.fixer._extract_short_title(caption)
        assert short == "System Architecture Overview"

    def test_extract_short_title_truncate(self):
        """Test short title extraction by truncation."""
        # No colon, no period - should truncate at word boundary
        caption = "A very long caption without any sentence breaks that just goes on and on"
        short = self.fixer._extract_short_title(caption)
        assert len(short) <= 60
        assert not short.endswith(" ")  # Should end at word boundary

    def test_result_to_dict_format(self):
        """Test result serialization to dict."""
        result = CaptionLengthFixResult(
            fixes_applied=2,
            changes=[
                CaptionLengthFix(
                    file="test.tex",
                    line=1,
                    old_caption="\\caption{...}",
                    new_caption="\\caption[Short]{...}",
                    short_title="Short",
                    pattern="add-short-title",
                ),
            ],
        )

        d = self.fixer.to_dict(result)

        assert d["skill"] == "qa-img-fix-caption-length"
        assert d["status"] == "DONE"
        assert d["fixes_applied"] == 2
        assert len(d["changes"]) == 1

    def test_result_status_no_changes(self):
        """Test result status when no changes made."""
        result = CaptionLengthFixResult()
        assert result.status == "NO_CHANGES"

    def test_result_status_with_changes(self):
        """Test result status when changes made."""
        result = CaptionLengthFixResult(fixes_applied=1)
        assert result.status == "DONE"

    def test_fix_hebrew_caption(self):
        """Test fixing Hebrew caption with colon pattern."""
        caption = "ארכיטקטורת המערכת: הסבר מפורט על כל הרכיבים והקשרים ביניהם"
        content = f"\\caption{{{caption}}}"

        issues = [Issue(
            rule="caption-description-pattern",
            file="test.tex",
            line=1,
            content=caption,
            severity=Severity.WARNING,
            context={
                "caption_text": caption,
                "suggested_short_title": "ארכיטקטורת המערכת",
            }
        )]

        fixed = self.fixer.fix(content, issues)
        assert "[ארכיטקטורת המערכת]" in fixed

    def test_get_patterns(self):
        """Test get_patterns returns expected structure."""
        patterns = self.fixer.get_patterns()
        assert "add-short-title" in patterns
        assert "description" in patterns["add-short-title"]

    def test_multiple_captions_in_file(self):
        """Test fixing multiple captions in same file."""
        # Captions must be 80+ chars for auto-detection
        content = """
\\begin{figure}
\\caption{First Caption: This is a very long and detailed description of the first figure that explains all the components}
\\end{figure}

\\begin{figure}
\\caption{Second Caption: Another very long and detailed description of the second figure that also needs to be fixed}
\\end{figure}
"""
        fixed, result = self.fixer.fix_content(content, "test.tex")

        # Should fix both captions
        assert "[First Caption]" in fixed
        assert "[Second Caption]" in fixed
        assert result.fixes_applied == 2
