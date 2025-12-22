"""
Tests for Bibliography detector.

Tests for citation and bibliography detection rules.
"""

import pytest

from qa_engine.infrastructure.detection.bib_detector import BibDetector


class TestBibDetector:
    """Tests for BibDetector."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = BibDetector()

    def test_get_rules_returns_all_rules(self):
        """Test get_rules returns expected rules."""
        rules = self.detector.get_rules()
        assert len(rules) >= 5
        assert "bib-missing-file" in rules
        assert "bib-empty-cite" in rules
        assert "bib-standalone-missing" in rules

    # Rule 1: Bibliography file reference
    def test_rule1_addbibresource(self):
        """Test detection of addbibresource command."""
        content = "\\addbibresource{references.bib}"
        issues = self.detector.detect(content, "test.tex")
        bib_issues = [i for i in issues if i.rule == "bib-missing-file"]
        assert len(bib_issues) > 0
        assert bib_issues[0].content == "references.bib"

    def test_rule1_bibliography_command(self):
        """Test detection of bibliography command."""
        content = "\\bibliography{refs}"
        issues = self.detector.detect(content, "test.tex")
        bib_issues = [i for i in issues if i.rule == "bib-missing-file"]
        assert len(bib_issues) > 0
        assert bib_issues[0].content == "refs"

    # Rule 2: Citation detection
    def test_rule2_cite_command(self):
        """Test detection of cite command."""
        content = "See \\cite{smith2020} for details."
        issues = self.detector.detect(content, "test.tex")
        cite_issues = [i for i in issues if i.rule == "bib-undefined-cite"]
        assert len(cite_issues) > 0
        assert cite_issues[0].content == "smith2020"

    # Rule 3: Empty citation
    def test_rule3_empty_cite(self):
        """Test detection of empty cite command."""
        content = "See \\cite{} for details."
        issues = self.detector.detect(content, "test.tex")
        empty_issues = [i for i in issues if i.rule == "bib-empty-cite"]
        assert len(empty_issues) > 0

    def test_rule3_cite_with_spaces(self):
        """Test detection of cite with only spaces."""
        content = "See \\cite{  } for details."
        issues = self.detector.detect(content, "test.tex")
        empty_issues = [i for i in issues if i.rule == "bib-empty-cite"]
        assert len(empty_issues) > 0

    # Rule 4: Standalone missing biblatex
    def test_rule4_standalone_without_biblatex(self):
        """Test detection of subfile without biblatex."""
        content = "\\documentclass[../main.tex]{subfiles}\\n\\cite{test}"
        issues = self.detector.detect(content, "chapter.tex")
        standalone_issues = [i for i in issues if i.rule == "bib-standalone-missing"]
        assert len(standalone_issues) > 0

    def test_rule4_standalone_with_biblatex_no_issue(self):
        """Test no issue when subfile has biblatex."""
        content = "\\documentclass[../main.tex]{subfiles}\\n\\usepackage{biblatex}\\n\\cite{test}"
        issues = self.detector.detect(content, "chapter.tex")
        standalone_issues = [i for i in issues if i.rule == "bib-standalone-missing"]
        assert len(standalone_issues) == 0

    def test_rule4_standalone_no_cite_no_issue(self):
        """Test no issue when subfile has no citations."""
        content = "\\documentclass[../main.tex]{subfiles}\\nNo citations here."
        issues = self.detector.detect(content, "chapter.tex")
        standalone_issues = [i for i in issues if i.rule == "bib-standalone-missing"]
        assert len(standalone_issues) == 0

    # Rule 5: Style mismatch
    def test_rule5_style_with_biblatex(self):
        """Test detection of bibliographystyle with biblatex."""
        content = "\\usepackage{biblatex}\\n\\bibliographystyle{plain}"
        issues = self.detector.detect(content, "test.tex")
        style_issues = [i for i in issues if i.rule == "bib-style-mismatch"]
        assert len(style_issues) > 0

    def test_rule5_style_without_biblatex_no_issue(self):
        """Test no issue when biblatex not used."""
        content = "\\usepackage{natbib}\\n\\bibliographystyle{plain}"
        issues = self.detector.detect(content, "test.tex")
        style_issues = [i for i in issues if i.rule == "bib-style-mismatch"]
        assert len(style_issues) == 0

    # General tests
    def test_skip_comments(self):
        """Test that comment lines are skipped."""
        content = "% \\cite{}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 0

    def test_offset_parameter(self):
        """Test line offset is applied correctly."""
        content = "\\cite{test}"
        issues = self.detector.detect(content, "test.tex", offset=100)
        assert len(issues) > 0
        assert issues[0].line == 101

    def test_fix_suggestion_formats_content(self):
        """Test fix suggestion includes matched content."""
        content = "\\addbibresource{myfile.bib}"
        issues = self.detector.detect(content, "test.tex")
        bib_issues = [i for i in issues if i.rule == "bib-missing-file"]
        assert len(bib_issues) > 0
        assert "myfile.bib" in bib_issues[0].fix
