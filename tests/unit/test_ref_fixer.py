"""
Tests for Cross-Reference fixer.

Tests for cross-chapter reference fixing rules.
"""

import pytest
import sys
from pathlib import Path

# Add skill tool to path - must clear any cached 'tool' module
skill_path = Path(__file__).parent.parent.parent / ".claude" / "skills" / "qa-ref-fix"
if 'tool' in sys.modules:
    del sys.modules['tool']
sys.path.insert(0, str(skill_path))

from tool import RefFixer, fix_in_content, get_fixed_content


class TestRefFixer:
    """Tests for RefFixer."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = RefFixer()

    # Rule 1: Single chapter reference
    def test_fix_single_chapter(self):
        """Test fixing 'ראה פרק X' to \\chapterref{X}."""
        content = r"ראה פרק \en{2}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{2}" in fixed
        assert len(fixes) == 1

    def test_fix_chapter_with_prefix(self):
        """Test fixing with prefix like 'ראה'."""
        content = r"ראה פרק \en{5} לפירוט"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{5}" in fixed

    def test_fix_chapter_in_parentheses(self):
        """Test fixing chapter reference in parentheses."""
        content = r"(ראה פרק \en{10})"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{10}" in fixed

    # Rule 2: Chapter range
    def test_fix_chapter_range_dash(self):
        """Test fixing 'פרקים X-Y' to \\chapterrefrange{X}{Y}."""
        content = r"פרקים \en{2-3}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterrefrange{2}{3}" in fixed

    def test_fix_chapter_range_endash(self):
        """Test fixing with en-dash."""
        content = r"פרקים \en{6--9}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterrefrange{6}{9}" in fixed

    # Rule 3: Chapter list
    def test_fix_chapter_list_two(self):
        """Test fixing 'פרקים X, Y' to \\chapterreflist{X,Y}."""
        content = r"פרקים \en{6, 9}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterreflist{6,9}" in fixed

    def test_fix_chapter_list_three(self):
        """Test fixing three chapters."""
        content = r"פרקים \en{2, 5, 8}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterreflist{2,5,8}" in fixed

    # Forward reference
    def test_fix_forward_reference(self):
        """Test fixing 'יוסבר בפרק X' to \\chapterrefforward{X}."""
        content = r"יוסבר בפרק \en{7}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterrefforward{7}" in fixed

    # No modifications needed
    def test_no_fix_chapterref(self):
        """Test that \\chapterref{} is not modified."""
        content = r"\chapterref{5}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert fixed == content
        assert len(fixes) == 0

    def test_no_fix_comment(self):
        """Test that comments are not modified."""
        content = r"% ראה פרק \en{2}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert fixed == content
        assert len(fixes) == 0

    # Multiple fixes
    def test_multiple_fixes_same_line(self):
        """Test fixing multiple references on same line."""
        content = r"ראה פרק \en{2} ופרק \en{3}"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{2}" in fixed
        assert r"\chapterref{3}" in fixed
        assert len(fixes) >= 2

    def test_multiple_fixes_different_lines(self):
        """Test fixing multiple references across lines."""
        content = r"""ראה פרק \en{2}.
פרקים \en{6, 9} מכילים.
יוסבר בפרק \en{10}."""
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{2}" in fixed
        assert r"\chapterreflist{6,9}" in fixed
        assert r"\chapterrefforward{10}" in fixed


class TestRefFixerModuleFunctions:
    """Test module-level functions."""

    def test_fix_in_content(self):
        """Test fix_in_content function."""
        content = r"ראה פרק \en{2}"
        fixed, fixes = fix_in_content(content, "test.tex")
        assert r"\chapterref{2}" in fixed
        assert len(fixes) >= 1

    def test_get_fixed_content(self):
        """Test get_fixed_content function."""
        content = r"ראה פרק \en{5}"
        fixed = get_fixed_content(content)
        assert r"\chapterref{5}" in fixed


class TestRefFixerRealWorld:
    """Test with real-world examples from the book."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = RefFixer()

    def test_chapter04_example(self):
        """Test example from chapter04.tex."""
        content = r"(ראה פרק \en{2}) חודשים לפני שנוצלו"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{2}" in fixed

    def test_chapter05_example(self):
        """Test example from chapter05.tex."""
        content = r"(לסקירה מקיפה של \en{EU AI Act} ראה פרק \en{10}):"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{10}" in fixed

    def test_chapter06_example(self):
        """Test example from chapter06.tex."""
        content = r"לטכניקות \en{Prompt Injection} המלאות ראה פרק \en{2}."
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterref{2}" in fixed

    def test_chapter11_example(self):
        """Test example from chapter11.tex."""
        content = r"(ראה פרקים \en{6, 9})"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterreflist{6,9}" in fixed

    def test_chapter12_example(self):
        """Test example from chapter12.tex."""
        content = r"(ראה פרקים \en{2-3} לסיכוני \en{OWASP})"
        fixed, fixes = self.fixer.fix_in_content(content)
        assert r"\chapterrefrange{2}{3}" in fixed
