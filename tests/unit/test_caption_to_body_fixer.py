"""
Tests for CaptionToBodyFixer.

Tests caption-to-body text migration for figure captions.
"""

import pytest

from qa_engine.infrastructure.fixing.caption_to_body_fixer import (
    CaptionToBodyFixer,
    CaptionToBodyResult,
)


class TestCaptionToBodyFixer:
    """Tests for CaptionToBodyFixer."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = CaptionToBodyFixer()

    def test_split_caption_by_period(self):
        """Test splitting caption at first period."""
        caption = "Short title. This is the long description that explains more."
        short, desc = self.fixer._split_caption(caption)
        assert short == "Short title"
        assert "long description" in desc

    def test_split_caption_by_colon(self):
        """Test splitting caption at colon."""
        caption = "Architecture Overview: This diagram shows the system layout."
        short, desc = self.fixer._split_caption(caption)
        assert short == "Architecture Overview"
        assert "diagram shows" in desc

    def test_split_caption_truncate(self):
        """Test truncation when no clear split point."""
        # Use words so truncation can find a word boundary
        long_text = "This is a very long caption text " * 5
        short, desc = self.fixer._split_caption(long_text)
        assert len(short) <= 60
        assert len(desc) > 0

    def test_fix_content_basic(self):
        """Test basic figure caption fix."""
        content = r"""
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{test.png}
\caption{Short title. This is a very long description that explains the figure in detail and should be moved to body text.}
\label{fig:test}
\end{figure}
"""
        fixed, result = self.fixer.fix_content(content, "test.tex")
        assert result.fixes_applied == 1
        assert "Short title" in fixed
        assert r"\end{figure}" in fixed
        # Description should be after figure
        end_figure_pos = fixed.find(r"\end{figure}")
        desc_pos = fixed.find("very long description")
        assert desc_pos > end_figure_pos

    def test_fix_content_with_label(self):
        """Test that figure reference is added when label exists."""
        content = r"""
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{test.png}
\caption{Short title. Long description here that needs to be moved to body text for better table of contents entry in the list of figures because this is way too long.}
\label{fig:mytest}
\end{figure}
"""
        fixed, result = self.fixer.fix_content(content, "test.tex")
        assert result.fixes_applied == 1
        # Should contain reference to the figure
        assert r"\ref{fig:mytest}" in fixed

    def test_fix_content_short_caption_unchanged(self):
        """Test that short captions are not modified."""
        content = r"""
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{test.png}
\caption{Short title only}
\label{fig:test}
\end{figure}
"""
        fixed, result = self.fixer.fix_content(content, "test.tex")
        assert result.fixes_applied == 0
        assert fixed == content

    def test_fix_content_nested_braces(self):
        """Test fix works with nested LaTeX commands."""
        content = r"""
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{test.png}
\caption{Risk chart for \en{OWASP Top 10}. The risks are rated from \en{1} to \en{10} with critical being above \en{8.5} and requiring immediate attention.}
\label{fig:risks}
\end{figure}
"""
        fixed, result = self.fixer.fix_content(content, "test.tex")
        assert result.fixes_applied == 1
        # Caption should be shortened
        assert r"\caption{Risk chart for \en{OWASP Top 10}}" in fixed

    def test_get_patterns(self):
        """Test get_patterns returns expected structure."""
        patterns = self.fixer.get_patterns()
        assert "caption-to-body" in patterns
        assert "description" in patterns["caption-to-body"]

    def test_to_dict(self):
        """Test result conversion to dict format."""
        result = CaptionToBodyResult()
        result.fixes_applied = 2
        output = self.fixer.to_dict(result)
        assert output["status"] == "DONE"
        assert output["fixes_applied"] == 2
        assert "skill" in output

    def test_result_status_no_changes(self):
        """Test result status when no changes made."""
        result = CaptionToBodyResult()
        assert result.status == "NO_CHANGES"

    def test_result_status_done(self):
        """Test result status when changes made."""
        result = CaptionToBodyResult()
        result.fixes_applied = 1
        assert result.status == "DONE"
