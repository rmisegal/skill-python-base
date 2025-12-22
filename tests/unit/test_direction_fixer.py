"""Unit tests for DirectionFixer."""

import pytest
from qa_engine.infrastructure.fixing.direction_fixer import (
    DirectionFixer, DirectionFix, DirectionFixResult,
)


class TestDirectionFixer:
    """Test cases for DirectionFixer."""

    def test_fix_hebrew_in_pythonbox(self):
        """Test fixing Hebrew text inside pythonbox."""
        content = r"""
\begin{pythonbox}
print("שלום")  # Hebrew greeting
\end{pythonbox}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 1  # Only "שלום", comment is English
        assert r"\texthebrew{שלום}" in fixed

    def test_fix_hebrew_in_lstlisting(self):
        """Test fixing Hebrew text inside lstlisting."""
        content = r"""
\begin{lstlisting}
# תגובה בעברית
x = "טקסט"
\end{lstlisting}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        # 3 fixes: "תגובה", "בעברית", "טקסט"
        assert result.fixes_applied == 3
        assert r"\texthebrew{תגובה}" in fixed
        assert r"\texthebrew{טקסט}" in fixed

    def test_fix_hebrew_in_minted(self):
        """Test fixing Hebrew text inside minted."""
        content = r"""
\begin{minted}{python}
name = "שם"
\end{minted}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        assert result.fixes_applied >= 1
        assert r"\texthebrew{" in fixed

    def test_no_fix_outside_code_block(self):
        """Test that Hebrew text outside code blocks is not modified."""
        content = r"""
זה טקסט עברי רגיל

\begin{pythonbox}
print("hello")
\end{pythonbox}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        # Hebrew outside code block should not be wrapped
        assert result.fixes_applied == 0
        assert fixed == content

    def test_skip_already_wrapped(self):
        """Test that already wrapped Hebrew is not double-wrapped."""
        content = r"""
\begin{pythonbox}
print("\texthebrew{שלום}")
\end{pythonbox}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 0
        assert fixed == content

    def test_fix_with_he_wrapper(self):
        """Test fixing with \\he{} wrapper instead of texthebrew."""
        content = r"""
\begin{pythonbox}
x = "עברית"
\end{pythonbox}
"""
        fixer = DirectionFixer(wrapper="he")
        fixed, result = fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 1
        assert r"\he{עברית}" in fixed

    def test_fix_multiple_hebrew_words(self):
        """Test fixing multiple Hebrew words in same line."""
        content = r"""
\begin{pythonbox}
msg = "שלום עולם"
\end{pythonbox}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        # The pattern matches consecutive Hebrew chars, so "שלום עולם"
        # might be 2 matches (separated by space)
        assert result.fixes_applied >= 1
        assert r"\texthebrew{" in fixed

    def test_fix_hebrew_in_tcolorbox(self):
        """Test fixing Hebrew in tcolorbox."""
        content = r"""
\begin{tcolorbox}
# קוד
def foo(): pass
\end{tcolorbox}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 1
        assert r"\texthebrew{קוד}" in fixed

    def test_fix_result_contains_details(self):
        """Test that fix result contains detailed information."""
        content = r"""
\begin{pythonbox}
x = "טקסט"
\end{pythonbox}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "chapter1.tex")

        assert result.fixes_applied == 1
        assert len(result.fixes) == 1

        fix = result.fixes[0]
        assert fix.file == "chapter1.tex"
        assert fix.line == 3
        assert fix.original == "טקסט"
        assert r"\texthebrew{טקסט}" in fix.replacement
        assert fix.pattern_id == "hebrew-in-code"

    def test_get_patterns(self):
        """Test get_patterns returns valid dictionary."""
        fixer = DirectionFixer()
        patterns = fixer.get_patterns()

        assert "hebrew-in-code" in patterns
        assert "find" in patterns["hebrew-in-code"]
        assert "replace" in patterns["hebrew-in-code"]
        assert "description" in patterns["hebrew-in-code"]

    def test_fix_interface_method(self):
        """Test fix() method from FixerInterface."""
        from qa_engine.domain.models.issue import Issue, Severity

        content = r"""
\begin{pythonbox}
print("בדיקה")
\end{pythonbox}
"""
        issues = [
            Issue(
                rule="code-direction-hebrew",
                file="test.tex",
                line=3,
                content="בדיקה",
                severity=Severity.WARNING,
            )
        ]

        fixer = DirectionFixer()
        fixed = fixer.fix(content, issues)

        assert r"\texthebrew{בדיקה}" in fixed

    def test_fix_with_wrapper_method(self):
        """Test fix_with_wrapper convenience method."""
        content = r"""
\begin{pythonbox}
x = "עברית"
\end{pythonbox}
"""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_with_wrapper(content, wrapper="he", file_path="t.tex")

        assert result.fixes_applied == 1
        assert r"\he{עברית}" in fixed

    def test_empty_content(self):
        """Test with empty content."""
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content("", "test.tex")

        assert result.fixes_applied == 0
        assert fixed == ""

    def test_no_code_blocks(self):
        """Test content without any code blocks."""
        content = "Just regular text with עברית here."
        fixer = DirectionFixer()
        fixed, result = fixer.fix_content(content, "test.tex")

        assert result.fixes_applied == 0
        assert fixed == content
