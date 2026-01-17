"""
Tests for BiDi fixer - fixing BiDi issues in Hebrew-English LaTeX.
"""

import pytest

from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.infrastructure.fixing.bidi_fixer import BiDiFixer


class TestBiDiFixer:
    """Tests for BiDiFixer."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = BiDiFixer()

    def test_fix_number_single_year(self):
        """Test fixing a single year uses hebyear."""
        result = self.fixer._fix_number("2025")
        assert result == r"\hebyear{2025}"

    def test_fix_number_regular(self):
        """Test fixing regular numbers uses num."""
        result = self.fixer._fix_number("123")
        assert result == r"\num{123}"

    def test_fix_number_decimal(self):
        """Test fixing decimal numbers uses num."""
        result = self.fixer._fix_number("99.99")
        assert result == r"\num{99.99}"

    def test_fix_year_range(self):
        """Test fixing year range uses hebyear."""
        result = self.fixer._fix_year_range("2025-2026")
        assert result == r"\hebyear{2025-2026}"

    def test_fix_year_range_different_years(self):
        """Test fixing different year ranges."""
        result = self.fixer._fix_year_range("2026-2028")
        assert result == r"\hebyear{2026-2028}"

    def test_get_fix_routes_year_range(self):
        """Test _get_fix correctly routes year range rule."""
        result = self.fixer._get_fix("bidi-year-range", "2025-2026")
        assert result == r"\hebyear{2025-2026}"

    def test_get_fix_routes_numbers(self):
        """Test _get_fix correctly routes number rule."""
        result = self.fixer._get_fix("bidi-numbers", "2025")
        assert result == r"\hebyear{2025}"

    def test_get_fix_routes_english(self):
        """Test _get_fix correctly routes English rule."""
        result = self.fixer._get_fix("bidi-english", "Python")
        assert result == r"\en{Python}"

    def test_get_fix_routes_acronym(self):
        """Test _get_fix correctly routes acronym rule."""
        result = self.fixer._get_fix("bidi-acronym", "API")
        assert result == r"\en{API}"

    def test_fix_content_with_year_range_issue(self):
        """Test full fix flow with year range issue."""
        content = "תחזיות לשנים 2025-2026 הבאות"
        issue = Issue(
            rule="bidi-year-range",
            file="test.tex",
            line=1,
            content="2025-2026",
            severity=Severity.WARNING,
            fix=r"\hebyear{2025-2026}",
            context={"match_start": 14},
        )
        result = self.fixer.fix(content, [issue])
        assert r"\hebyear{2025-2026}" in result

    def test_fix_skips_already_wrapped(self):
        """Test fixer skips content already wrapped."""
        content = r"תחזיות לשנים \hebyear{2025-2026} הבאות"
        issue = Issue(
            rule="bidi-year-range",
            file="test.tex",
            line=1,
            content="2025-2026",
            severity=Severity.WARNING,
            fix=r"\hebyear{2025-2026}",
            context={"match_start": 22},
        )
        result = self.fixer.fix(content, [issue])
        # Should not double-wrap
        assert result.count(r"\hebyear") == 1

    def test_fix_prevents_double_wrapping_en(self):
        r"""Test fixer prevents double-wrapping \en{} commands."""
        content = r"מעבד \en{CPU} מהיר"
        issue = Issue(
            rule="bidi-acronym",
            file="test.tex",
            line=1,
            content="CPU",
            severity=Severity.WARNING,
            fix=r"\en{CPU}",
            context={"match_start": 9},  # Position of 'C' in CPU
        )
        result = self.fixer.fix(content, [issue])
        # Should not create \en{\en{CPU}}
        assert r"\en{\en{" not in result
        assert result.count(r"\en{") == 1

    def test_fix_prevents_double_wrapping_num(self):
        """Test fixer prevents double-wrapping \num{} commands."""
        content = r"יש \num{42} פריטים"
        issue = Issue(
            rule="bidi-numbers",
            file="test.tex",
            line=1,
            content="42",
            severity=Severity.WARNING,
            fix=r"\num{42}",
            context={"match_start": 8},  # Position of '4' in 42
        )
        result = self.fixer.fix(content, [issue])
        # Should not create \num{\num{42}}
        assert r"\num{\num{" not in result
        assert result.count(r"\num{") == 1

    def test_is_wrapped_at_position_detects_wrapper(self):
        """Test _is_wrapped_at_position correctly detects wrappers."""
        line = r"מעבד \en{CPU} מהיר"
        # Position 9 is 'C' in CPU, which is inside \en{}
        assert self.fixer._is_wrapped_at_position(line, "CPU", 9) is True

    def test_is_wrapped_at_position_no_wrapper(self):
        """Test _is_wrapped_at_position returns False when no wrapper."""
        line = r"מעבד CPU מהיר"
        # Position 5 is 'C' in CPU, not wrapped
        assert self.fixer._is_wrapped_at_position(line, "CPU", 5) is False

    def test_would_double_wrap_detection(self):
        """Test _would_double_wrap correctly detects potential double-wrapping."""
        line = r"מעבד \en{CPU} מהיר"
        # Trying to wrap CPU again would create double-wrapping
        assert self.fixer._would_double_wrap(line, "CPU", r"\en{CPU}", 9) is True

    def test_is_already_wrapped_content(self):
        """Test _is_already_wrapped detects wrapped content."""
        assert self.fixer._is_already_wrapped(r"\en{CPU}") is True
        assert self.fixer._is_already_wrapped(r"\num{42}") is True
        assert self.fixer._is_already_wrapped("CPU") is False

    def test_get_tikz_lines_simple(self):
        """Test _get_tikz_lines identifies lines inside tikzpicture."""
        lines = [
            "Some text before",
            r"\begin{tikzpicture}",
            r"\node[below] at (0,0) {label};",
            r"\draw (0,0) -- (1,1);",
            r"\end{tikzpicture}",
            "Some text after",
        ]
        tikz_lines = self.fixer._get_tikz_lines(lines)
        # Lines 2,3,4 are inside TikZ (depth > 0 after processing)
        assert 2 in tikz_lines
        assert 3 in tikz_lines
        assert 4 in tikz_lines
        assert 1 not in tikz_lines
        assert 5 not in tikz_lines  # \end line brings depth to 0
        assert 6 not in tikz_lines

    def test_get_tikz_lines_nested_axis(self):
        """Test _get_tikz_lines handles nested axis environment."""
        lines = [
            "Text",
            r"\begin{tikzpicture}",
            r"\begin{axis}",
            r"\addplot coordinates {(0,0) (1,1)};",
            r"\end{axis}",
            r"\end{tikzpicture}",
            "More text",
        ]
        tikz_lines = self.fixer._get_tikz_lines(lines)
        # Lines 2-5 are inside TikZ environments (depth > 0 after processing)
        # Line 6 (\end{tikzpicture}) brings depth to 0, so it's excluded
        # (which is fine - no content to wrap on closing tag)
        assert 2 in tikz_lines
        assert 3 in tikz_lines
        assert 4 in tikz_lines
        assert 5 in tikz_lines
        assert 1 not in tikz_lines
        assert 6 not in tikz_lines  # Closing tag, depth=0 after
        assert 7 not in tikz_lines

    def test_fix_skips_tikz_content(self):
        """Test fixer skips issues inside TikZ environments."""
        content = r"""טקסט עם CPU לפני
\begin{tikzpicture}
\node[below] at (0,0) {CPU};
\end{tikzpicture}
טקסט עם GPU אחרי"""
        # Create issues for both CPU occurrences
        issues = [
            Issue(
                rule="bidi-acronym",
                file="test.tex",
                line=1,
                content="CPU",
                severity=Severity.WARNING,
                fix=r"\en{CPU}",
                context={"match_start": 9},
            ),
            Issue(
                rule="bidi-acronym",
                file="test.tex",
                line=3,  # Inside TikZ
                content="CPU",
                severity=Severity.WARNING,
                fix=r"\en{CPU}",
                context={"match_start": 24},
            ),
            Issue(
                rule="bidi-acronym",
                file="test.tex",
                line=5,
                content="GPU",
                severity=Severity.WARNING,
                fix=r"\en{GPU}",
                context={"match_start": 9},
            ),
        ]
        result = self.fixer.fix(content, issues)
        # Line 1 and 5 should be fixed, line 3 (TikZ) should be skipped
        assert r"\en{CPU}" in result.split("\n")[0]  # Line 1 fixed
        assert r"\en{GPU}" in result.split("\n")[4]  # Line 5 fixed
        # TikZ line should remain unchanged
        assert r"\node[below] at (0,0) {CPU};" in result

    def test_is_inside_color_context_tcolorbox(self):
        """Test _is_inside_color_context detects tcolorbox color options."""
        line = r"colback=purple!5, colframe=green!60!black"
        # colback=purple!5, colframe=green!60!black
        # 01234567890123456789...
        # Position 8 is 'p' in purple (first color)
        assert self.fixer._is_inside_color_context(line, 8) is True
        # Position 15 is '5' after purple!
        assert self.fixer._is_inside_color_context(line, 15) is True
        # Position 27 is 'g' in green (second color)
        assert self.fixer._is_inside_color_context(line, 27) is True

    def test_is_inside_color_context_textcolor(self):
        r"""Test _is_inside_color_context detects \textcolor command."""
        line = r"\textcolor{green!60!black}{text}"
        # Position 11 is 'g' in green
        assert self.fixer._is_inside_color_context(line, 11) is True
        # Position 17 is '6' in 60
        assert self.fixer._is_inside_color_context(line, 17) is True
        # Position 27 is 't' in text (outside color spec)
        assert self.fixer._is_inside_color_context(line, 27) is False

    def test_is_inside_color_context_no_color(self):
        """Test _is_inside_color_context returns False for non-color context."""
        line = r"טקסט רגיל עם Python ומספר 42"
        assert self.fixer._is_inside_color_context(line, 15) is False
        assert self.fixer._is_inside_color_context(line, 25) is False

    def test_fix_skips_color_context(self):
        """Test fixer skips issues inside color specifications."""
        content = r"תיבה עם colback=purple!5 צבעונית"
        issue = Issue(
            rule="bidi-english",
            file="test.tex",
            line=1,
            content="purple",
            severity=Severity.WARNING,
            fix=r"\en{purple}",
            context={"match_start": 17},  # Position of 'purple'
        )
        result = self.fixer.fix(content, [issue])
        # Should NOT wrap purple in color context
        assert r"\en{purple}" not in result
        assert "colback=purple!5" in result
