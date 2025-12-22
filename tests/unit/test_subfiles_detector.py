"""
Tests for Subfiles detector.

Tests for subfiles package usage detection rules.
"""

import pytest

from qa_engine.infrastructure.detection.subfiles_detector import SubfilesDetector


class TestSubfilesDetector:
    """Tests for SubfilesDetector."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = SubfilesDetector()

    def test_get_rules_returns_all_rules(self):
        """Test get_rules returns expected rules."""
        rules = self.detector.get_rules()
        assert len(rules) >= 3
        assert "subfiles-missing-class" in rules
        assert "subfiles-no-main-ref" in rules
        assert "subfiles-no-preamble" in rules

    # Rule 1: Chapter without subfiles class
    def test_rule1_chapter_without_subfiles(self):
        """Test detection of chapter without subfiles class."""
        content = "\\documentclass{article}"
        issues = self.detector.detect(content, "chapter01.tex")
        missing_issues = [i for i in issues if i.rule == "subfiles-missing-class"]
        assert len(missing_issues) > 0

    def test_rule1_chapter_with_subfiles_no_issue(self):
        """Test no issue when chapter uses subfiles."""
        content = "\\documentclass[../main.tex]{subfiles}"
        issues = self.detector.detect(content, "chapter01.tex")
        missing_issues = [i for i in issues if i.rule == "subfiles-missing-class"]
        assert len(missing_issues) == 0

    def test_rule1_non_chapter_file_ignored(self):
        """Test non-chapter files are ignored for this rule."""
        content = "\\documentclass{article}"
        issues = self.detector.detect(content, "main.tex")
        missing_issues = [i for i in issues if i.rule == "subfiles-missing-class"]
        assert len(missing_issues) == 0

    # Rule 2: Subfiles without main reference
    def test_rule2_subfiles_no_main_ref(self):
        """Test detection of subfiles without main reference."""
        content = "\\documentclass{subfiles}"
        issues = self.detector.detect(content, "test.tex")
        no_ref_issues = [i for i in issues if i.rule == "subfiles-no-main-ref"]
        assert len(no_ref_issues) > 0

    def test_rule2_subfiles_with_main_ref_no_issue(self):
        """Test no issue when subfiles has main reference."""
        content = "\\documentclass[../main.tex]{subfiles}"
        issues = self.detector.detect(content, "test.tex")
        no_ref_issues = [i for i in issues if i.rule == "subfiles-no-main-ref"]
        assert len(no_ref_issues) == 0

    # Rule 3: Missing preamble setup
    def test_rule3_subfiles_no_counter(self):
        """Test detection of subfiles without chapter counter."""
        content = "\\documentclass[../main.tex]{subfiles}\\n\\begin{document}"
        issues = self.detector.detect(content, "test.tex")
        preamble_issues = [i for i in issues if i.rule == "subfiles-no-preamble"]
        assert len(preamble_issues) > 0

    def test_rule3_subfiles_with_counter_no_issue(self):
        """Test no issue when subfiles has counter setup."""
        content = "\\documentclass[../main.tex]{subfiles}\\n\\setcounter{chapter}{5}"
        issues = self.detector.detect(content, "test.tex")
        preamble_issues = [i for i in issues if i.rule == "subfiles-no-preamble"]
        assert len(preamble_issues) == 0

    def test_rule3_subfiles_with_classloaded_no_issue(self):
        """Test no issue when subfiles has ifSubfilesClassLoaded."""
        content = "\\documentclass[../main.tex]{subfiles}\\n\\ifSubfilesClassLoaded{}"
        issues = self.detector.detect(content, "test.tex")
        preamble_issues = [i for i in issues if i.rule == "subfiles-no-preamble"]
        assert len(preamble_issues) == 0

    # General tests
    def test_skip_comments(self):
        """Test that comment lines are skipped."""
        content = "% \\documentclass{subfiles}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 0

    def test_offset_parameter(self):
        """Test line offset is applied correctly."""
        content = "\\documentclass{subfiles}"
        issues = self.detector.detect(content, "test.tex", offset=100)
        assert len(issues) > 0
        assert issues[0].line == 101
