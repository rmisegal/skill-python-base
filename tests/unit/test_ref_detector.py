"""
Tests for Cross-Reference detector.

Tests for cross-chapter reference detection rules.
"""

import pytest
import sys
from pathlib import Path

# Add skill tool to path - must clear any cached 'tool' module
skill_path = Path(__file__).parent.parent.parent / ".claude" / "skills" / "qa-ref-detect"
if 'tool' in sys.modules:
    del sys.modules['tool']
sys.path.insert(0, str(skill_path))

from tool import RefDetector, detect_in_content, get_rules


class TestRefDetector:
    """Tests for RefDetector."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = RefDetector()

    def test_get_rules_returns_all_rules(self):
        """Test get_rules returns expected rules."""
        rules = self.detector.get_rules()
        assert len(rules) >= 4
        assert "ref-hardcoded-chapter" in rules
        assert "ref-hardcoded-chapters-range" in rules
        assert "ref-hardcoded-chapters-list" in rules
        assert "ref-undefined-label" in rules
        assert "ref-orphan-label" in rules

    # Rule 1: Hardcoded single chapter reference
    def test_rule1_hardcoded_chapter_see(self):
        """Test detection of 'ראה פרק X' pattern."""
        content = r"לפירוט טכניקות אלו ראה פרק \en{2}."
        issues = self.detector.detect_in_content(content, "test.tex")
        chapter_issues = [i for i in issues if i.rule == "ref-hardcoded-chapter"]
        assert len(chapter_issues) == 1
        assert "2" in chapter_issues[0].chapter_refs

    def test_rule1_hardcoded_chapter_parentheses(self):
        """Test detection of '(ראה פרק X)' pattern."""
        content = r"(ראה פרק \en{10} לפירוט)"
        issues = self.detector.detect_in_content(content, "test.tex")
        chapter_issues = [i for i in issues if i.rule == "ref-hardcoded-chapter"]
        assert len(chapter_issues) == 1
        assert "10" in chapter_issues[0].chapter_refs

    def test_rule1_hardcoded_chapter_in(self):
        """Test detection of 'בפרק X' pattern."""
        content = r"כמתואר בפרק \en{5}"
        issues = self.detector.detect_in_content(content, "test.tex")
        chapter_issues = [i for i in issues if i.rule == "ref-hardcoded-chapter"]
        assert len(chapter_issues) == 1
        assert "5" in chapter_issues[0].chapter_refs

    # Rule 2: Hardcoded chapter range
    def test_rule2_chapter_range_dash(self):
        """Test detection of 'פרקים X-Y' pattern."""
        content = r"ראה פרקים \en{2-3} לסיכוני OWASP"
        issues = self.detector.detect_in_content(content, "test.tex")
        range_issues = [i for i in issues if i.rule == "ref-hardcoded-chapters-range"]
        assert len(range_issues) == 1
        assert "2" in range_issues[0].chapter_refs
        assert "3" in range_issues[0].chapter_refs

    def test_rule2_chapter_range_endash(self):
        """Test detection of 'פרקים X--Y' pattern (en-dash)."""
        content = r"פרקים \en{6--9} בספר המלא"
        issues = self.detector.detect_in_content(content, "test.tex")
        range_issues = [i for i in issues if i.rule == "ref-hardcoded-chapters-range"]
        assert len(range_issues) == 1

    # Rule 3: Hardcoded chapter list
    def test_rule3_chapter_list(self):
        """Test detection of 'פרקים X, Y' pattern."""
        content = r"ראה פרקים \en{6, 9} לפירוט"
        issues = self.detector.detect_in_content(content, "test.tex")
        list_issues = [i for i in issues if i.rule == "ref-hardcoded-chapters-list"]
        assert len(list_issues) == 1
        assert "6" in list_issues[0].chapter_refs
        assert "9" in list_issues[0].chapter_refs

    def test_rule3_chapter_list_three(self):
        """Test detection of 'פרקים X, Y, Z' pattern."""
        content = r"פרקים \en{2, 5, 8}"
        issues = self.detector.detect_in_content(content, "test.tex")
        list_issues = [i for i in issues if i.rule == "ref-hardcoded-chapters-list"]
        assert len(list_issues) == 1
        assert len(list_issues[0].chapter_refs) == 3

    # No false positives
    def test_no_false_positive_chapterref(self):
        """Test that \\chapterref{} is not flagged."""
        content = r"ראה \chapterref{5} לפירוט"
        issues = self.detector.detect_in_content(content, "test.tex")
        chapter_issues = [i for i in issues if i.rule == "ref-hardcoded-chapter"]
        assert len(chapter_issues) == 0

    def test_no_false_positive_comment(self):
        """Test that comments are skipped."""
        content = r"% ראה פרק \en{2}"
        issues = self.detector.detect_in_content(content, "test.tex")
        chapter_issues = [i for i in issues if i.rule == "ref-hardcoded-chapter"]
        assert len(chapter_issues) == 0

    # Multiple issues
    def test_multiple_issues_same_line(self):
        """Test detection of multiple issues in same line."""
        content = r"ראה פרק \en{2} ופרק \en{3}"
        issues = self.detector.detect_in_content(content, "test.tex")
        chapter_issues = [i for i in issues if i.rule == "ref-hardcoded-chapter"]
        assert len(chapter_issues) >= 2

    def test_multiple_issues_different_lines(self):
        """Test detection of multiple issues across lines."""
        content = r"""
ראה פרק \en{2} לפירוט.
לסיכונים ראה פרק \en{3}.
פרקים \en{6, 9} מכילים מידע נוסף.
"""
        issues = self.detector.detect_in_content(content, "test.tex")
        assert len(issues) >= 3


class TestRefDetectorModuleFunctions:
    """Test module-level functions."""

    def test_detect_in_content(self):
        """Test detect_in_content function."""
        content = r"ראה פרק \en{2}"
        issues = detect_in_content(content, "test.tex")
        assert len(issues) >= 1
        assert issues[0]["rule"] == "ref-hardcoded-chapter"

    def test_get_rules(self):
        """Test get_rules function."""
        rules = get_rules()
        assert "ref-hardcoded-chapter" in rules


class TestRefDetectorFix:
    """Test fix suggestions."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = RefDetector()

    def test_fix_suggestion_chapterref(self):
        """Test that fix suggests \\chapterref{}."""
        content = r"ראה פרק \en{5}"
        issues = self.detector.detect_in_content(content, "test.tex")
        assert len(issues) == 1
        assert "\\chapterref{5}" in issues[0].fix

    def test_fix_suggestion_chapterrefrange(self):
        """Test that fix suggests \\chapterrefrange{}{}."""
        content = r"פרקים \en{2-3}"
        issues = self.detector.detect_in_content(content, "test.tex")
        range_issues = [i for i in issues if i.rule == "ref-hardcoded-chapters-range"]
        assert len(range_issues) == 1
        assert "\\chapterrefrange{2}{3}" in range_issues[0].fix

    def test_fix_suggestion_chapterreflist(self):
        """Test that fix suggests \\chapterreflist{}."""
        content = r"פרקים \en{6, 9}"
        issues = self.detector.detect_in_content(content, "test.tex")
        list_issues = [i for i in issues if i.rule == "ref-hardcoded-chapters-list"]
        assert len(list_issues) == 1
        assert "\\chapterreflist" in list_issues[0].fix
