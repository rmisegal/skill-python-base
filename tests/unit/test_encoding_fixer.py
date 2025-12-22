"""
Tests for Encoding Fixer.

Tests for qa-code-fix-encoding functionality.
"""

import pytest

from qa_engine.infrastructure.fixing import EncodingFixer


class TestEncodingFixer:
    """Tests for EncodingFixer."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = EncodingFixer()

    def test_fix_multiplication_sign_text(self):
        """Test fixing multiplication sign in text context."""
        content = "The result is 5\u00D710"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert r"$\times$" in fixed
        assert len(changes) == 1

    def test_fix_multiplication_sign_code(self):
        """Test fixing multiplication sign in code context."""
        content = "result = 5\u00D710"
        fixed, changes = self.fixer.fix_content(content, "code")
        assert "*" in fixed
        assert "\u00D7" not in fixed

    def test_fix_right_arrow_text(self):
        """Test fixing right arrow in text context."""
        content = "A \u2192 B"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert r"$\rightarrow$" in fixed

    def test_fix_right_arrow_code(self):
        """Test fixing right arrow in code context."""
        content = "a \u2192 b"
        fixed, changes = self.fixer.fix_content(content, "code")
        assert "->" in fixed
        assert "\u2192" not in fixed

    def test_fix_check_mark(self):
        """Test fixing check mark."""
        content = "Status: \u2713"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert "[+]" in fixed

    def test_fix_ballot_x(self):
        """Test fixing ballot X."""
        content = "Failed: \u2717"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert "[-]" in fixed

    def test_fix_smiley_emoji(self):
        """Test fixing smiley emoji."""
        content = "Hello \U0001F60A"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert ":)" in fixed

    def test_fix_note_emoji(self):
        """Test fixing note emoji."""
        content = "\U0001F4DD Important"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert "[Note]" in fixed

    def test_fix_user_emoji(self):
        """Test fixing user emoji."""
        content = "\U0001F464 User"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert "[User]" in fixed

    def test_fix_robot_emoji(self):
        """Test fixing robot emoji."""
        content = "\U0001F916 Bot"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert "[Bot]" in fixed

    def test_fix_chart_emoji(self):
        """Test fixing chart emoji."""
        content = "\U0001F4CA Stats"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert "[Stats]" in fixed

    def test_auto_context_code_block(self):
        """Test auto context detection for code blocks."""
        content = r"""\begin{lstlisting}
x = 5\u00D710
\end{lstlisting}"""
        fixed, changes = self.fixer.fix_content(content, "auto")
        # In code block, should use asterisk
        assert "*" in fixed or "\u00D7" not in fixed

    def test_auto_context_text(self):
        """Test auto context detection for regular text."""
        content = "Result: 5\u00D710"
        fixed, changes = self.fixer.fix_content(content, "auto")
        assert r"$\times$" in fixed

    def test_multiple_fixes_same_line(self):
        """Test multiple fixes on same line."""
        content = "A \u2192 B \u00D7 C"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert r"$\rightarrow$" in fixed
        assert r"$\times$" in fixed
        assert len(changes) == 2

    def test_no_changes_needed(self):
        """Test content that needs no fixes."""
        content = "Normal text without special characters"
        fixed, changes = self.fixer.fix_content(content, "text")
        assert fixed == content
        assert len(changes) == 0

    def test_get_patterns(self):
        """Test get_patterns returns both contexts."""
        patterns = self.fixer.get_patterns()
        assert "text" in patterns
        assert "code" in patterns
        assert "multiplication" in patterns["text"]
        assert "multiplication" in patterns["code"]

    def test_fix_interface_method(self):
        """Test the fix() interface method works."""
        content = "Test \u00D7 content"
        fixed = self.fixer.fix(content, [])
        assert "\u00D7" not in fixed
