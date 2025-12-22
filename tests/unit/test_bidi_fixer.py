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
