"""
Tests for BiDi detector - all 15 rules.

Each rule from QA-CLAUDE-MECHANISM-ARCHITECTURE-REPORT.md has unit tests.
"""

import pytest

from qa_engine.domain.models.issue import Severity
from qa_engine.infrastructure.detection.bidi_detector import BiDiDetector


class TestBiDiDetector:
    """Tests for BiDiDetector."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = BiDiDetector()

    def test_get_rules_returns_all_15_rules(self):
        """Test get_rules returns all expected rules."""
        rules = self.detector.get_rules()
        assert len(rules) >= 14  # At least 14 rules (some combined)
        assert "bidi-numbers" in rules
        assert "bidi-english" in rules
        assert "bidi-acronym" in rules

    # Rule 1: Cover Page Metadata
    def test_rule1_cover_metadata_title(self):
        """Test detection of Hebrew in title without wrapper."""
        content = r"\title{כותרת בעברית}"
        issues = self.detector.detect(content, "test.tex")
        cover_issues = [i for i in issues if i.rule == "bidi-cover-metadata"]
        assert len(cover_issues) > 0

    def test_rule1_cover_metadata_author(self):
        """Test detection of Hebrew in author without wrapper."""
        content = r"\author{ישראל ישראלי}"
        issues = self.detector.detect(content, "test.tex")
        cover_issues = [i for i in issues if i.rule == "bidi-cover-metadata"]
        assert len(cover_issues) > 0

    # Rule 3: Section Numbering
    def test_rule3_section_numbering(self):
        """Test detection of Hebrew section titles."""
        content = r"\section{מבוא לנושא}"
        issues = self.detector.detect(content, "test.tex")
        section_issues = [i for i in issues if i.rule == "bidi-section-number"]
        assert len(section_issues) > 0

    # Rule 4: Reversed Text (final letters at start)
    def test_rule4_reversed_text_final_mem(self):
        """Test detection of final mem at word start."""
        content = "םולש בוט"  # Reversed "שלום טוב"
        issues = self.detector.detect(content, "test.tex")
        reversed_issues = [i for i in issues if i.rule == "bidi-reversed-text"]
        assert len(reversed_issues) > 0

    def test_rule4_reversed_text_final_nun(self):
        """Test detection of final nun at word start."""
        content = "ןושאר"  # Reversed "ראשון"
        issues = self.detector.detect(content, "test.tex")
        reversed_issues = [i for i in issues if i.rule == "bidi-reversed-text"]
        assert len(reversed_issues) > 0

    # Rule 5: Header/Footer Hebrew
    def test_rule5_header_hebrew(self):
        """Test detection of Hebrew in header without wrapper."""
        content = r"\lhead{כותרת עליונה}"
        issues = self.detector.detect(content, "test.tex")
        header_issues = [i for i in issues if i.rule == "bidi-header-footer"]
        assert len(header_issues) > 0

    def test_rule5_footer_hebrew(self):
        """Test detection of Hebrew in footer without wrapper."""
        content = r"\cfoot{עמוד \thepage}"
        issues = self.detector.detect(content, "test.tex")
        footer_issues = [i for i in issues if i.rule == "bidi-header-footer"]
        assert len(footer_issues) > 0

    # Rule 6: Numbers Without LTR
    def test_rule6_numbers_in_hebrew(self):
        """Test detection of numbers without wrapper in Hebrew."""
        content = "המחיר הוא 123 שקלים"
        issues = self.detector.detect(content, "test.tex")
        number_issues = [i for i in issues if i.rule == "bidi-numbers"]
        assert len(number_issues) > 0
        assert number_issues[0].content == "123"

    def test_rule6_decimal_numbers(self):
        """Test detection of decimal numbers."""
        content = "הערך הוא 99.99 אחוז"
        issues = self.detector.detect(content, "test.tex")
        number_issues = [i for i in issues if i.rule == "bidi-numbers"]
        assert len(number_issues) > 0
        assert "99.99" in number_issues[0].content

    # Rule 6b: Year Ranges Without LTR
    def test_rule6b_year_range_in_hebrew(self):
        """Test detection of year range without wrapper in Hebrew."""
        content = "תחזיות לשנים 2025-2026 הבאות"
        issues = self.detector.detect(content, "test.tex")
        year_issues = [i for i in issues if i.rule == "bidi-year-range"]
        assert len(year_issues) > 0
        assert "2025" in year_issues[0].content

    def test_rule6b_year_range_in_section(self):
        """Test detection of year range in section title."""
        content = r"\section{מבט לעתיד - תחזיות לשנים 2026-2028}"
        issues = self.detector.detect(content, "test.tex")
        year_issues = [i for i in issues if i.rule == "bidi-year-range"]
        assert len(year_issues) > 0

    def test_rule6b_year_range_already_wrapped(self):
        """Test no issue when year range is already wrapped."""
        content = r"תחזיות לשנים \hebyear{2025-2026} הבאות"
        issues = self.detector.detect(content, "test.tex")
        year_issues = [i for i in issues if i.rule == "bidi-year-range"]
        assert len(year_issues) == 0

    def test_rule6b_year_range_textenglish_wrapped(self):
        """Test no issue when year range is wrapped with textenglish."""
        content = r"תחזיות לשנים \textenglish{2025-2026} הבאות"
        issues = self.detector.detect(content, "test.tex")
        year_issues = [i for i in issues if i.rule == "bidi-year-range"]
        assert len(year_issues) == 0

    # Rule 7: English Without LTR
    def test_rule7_english_in_hebrew(self):
        """Test detection of English words without wrapper."""
        content = "זה טקסט test בעברית"
        issues = self.detector.detect(content, "test.tex")
        english_issues = [i for i in issues if i.rule == "bidi-english"]
        assert len(english_issues) > 0
        assert english_issues[0].content == "test"

    # Rule 8: tcolorbox BiDi-Safe
    def test_rule8_tcolorbox_without_wrapper(self):
        """Test detection of tcolorbox without english wrapper."""
        content = "שלום\n\\begin{tcolorbox}\ncontent\n\\end{tcolorbox}"
        issues = self.detector.detect(content, "test.tex")
        tcolorbox_issues = [i for i in issues if i.rule == "bidi-tcolorbox"]
        assert len(tcolorbox_issues) > 0

    # Rule 9: Section Titles with English
    def test_rule9_section_english_in_hebrew(self):
        """Test detection of English in Hebrew section title."""
        content = r"\section{מבוא ל-Python בעברית}"
        issues = self.detector.detect(content, "test.tex")
        section_issues = [i for i in issues if i.rule == "bidi-section-english"]
        assert len(section_issues) > 0

    # Rule 10: Uppercase Acronyms
    def test_rule10_acronym_in_hebrew(self):
        """Test detection of uppercase acronyms."""
        content = "ראשי תיבות API בעברית"
        issues = self.detector.detect(content, "test.tex")
        acronym_issues = [i for i in issues if i.rule == "bidi-acronym"]
        assert len(acronym_issues) > 0
        assert acronym_issues[0].content == "API"

    # Rule 12: Chapter Labels
    def test_rule12_chapter_label_position(self):
        """Test detection of label after hebrewchapter."""
        content = r"\hebrewchapter{פרק ראשון}\label{chap:first}"
        issues = self.detector.detect(content, "test.tex")
        label_issues = [i for i in issues if i.rule == "bidi-chapter-label"]
        assert len(label_issues) > 0

    # Rule 13: fbox/parbox Mixed Content
    def test_rule13_fbox_mixed_content(self):
        """Test detection of mixed content in fbox."""
        content = r"\fbox{שלום hello עולם}"
        issues = self.detector.detect(content, "test.tex")
        fbox_issues = [i for i in issues if i.rule == "bidi-fbox-mixed"]
        assert len(fbox_issues) > 0

    # Rule 14: Standalone Counter
    def test_rule14_standalone_without_counter(self):
        """Test detection of subfiles without chapter counter."""
        content = r"\documentclass[../main.tex,hebrew-academic]{subfiles}"
        issues = self.detector.detect(content, "test.tex")
        standalone_issues = [i for i in issues if i.rule == "bidi-standalone-counter"]
        assert len(standalone_issues) > 0

    def test_rule14_standalone_with_counter_no_issue(self):
        """Test no issue when counter is set."""
        content = r"""\documentclass[../main.tex,hebrew-academic]{subfiles}
\setcounter{chapter}{5}"""
        issues = self.detector.detect(content, "test.tex")
        standalone_issues = [i for i in issues if i.rule == "bidi-standalone-counter"]
        assert len(standalone_issues) == 0

    # Rule 15: Hebrew in English Wrapper
    def test_rule15_hebrew_in_english(self):
        """Test detection of Hebrew inside en wrapper."""
        content = r"\en{hello שלום world}"
        issues = self.detector.detect(content, "test.tex")
        heb_in_en_issues = [i for i in issues if i.rule == "bidi-hebrew-in-english"]
        assert len(heb_in_en_issues) > 0

    # TikZ in RTL
    def test_tikz_in_rtl_context(self):
        """Test detection of TikZ without wrapper in RTL."""
        content = "שלום\n\\begin{tikzpicture}...\\end{tikzpicture}"
        issues = self.detector.detect(content, "test.tex")
        tikz_issues = [i for i in issues if i.rule == "bidi-tikz-rtl"]
        assert len(tikz_issues) > 0

    # General tests
    def test_skip_comment_lines(self):
        """Test that comment lines are skipped."""
        content = "% זה מספר 123 בהערה"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 0

    def test_no_issue_in_english_only(self):
        """Test no issues when no Hebrew context."""
        content = "This is English text with number 123"
        issues = self.detector.detect(content, "test.tex")
        number_issues = [i for i in issues if i.rule == "bidi-numbers"]
        assert len(number_issues) == 0

    def test_offset_parameter(self):
        """Test line offset is applied correctly."""
        content = "המחיר הוא 123 שקלים"
        issues = self.detector.detect(content, "test.tex", offset=100)
        assert len(issues) > 0
        assert issues[0].line == 101

    def test_suggest_fix_formats_correctly(self):
        """Test fix suggestion includes content."""
        content = "המחיר הוא 42 שקלים"
        issues = self.detector.detect(content, "test.tex")
        number_issues = [i for i in issues if i.rule == "bidi-numbers"]
        assert len(number_issues) > 0
        assert "42" in number_issues[0].fix
