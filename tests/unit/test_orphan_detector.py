"""Unit tests for Section Orphan Detector."""
import pytest
from qa_engine.typeset.detection import SectionOrphanDetector, OrphanDetectResult


class TestSectionOrphanDetector:
    """Tests for SectionOrphanDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = SectionOrphanDetector()

    def test_detect_missing_needspace_section(self):
        """Test detecting section without needspace."""
        content = r"""Some content here.

\section{Test Section}
Section content goes here.
"""
        result = self.detector.detect_in_content(content)
        assert len(result.issues) >= 1
        assert any(i.rule == "missing-needspace-section" for i in result.issues)

    def test_detect_missing_needspace_hebrewsection(self):
        """Test detecting hebrewsection without needspace."""
        content = r"""תוכן קודם.

\hebrewsection{מבנה הפרוטוקול}
תוכן הקטע.
"""
        result = self.detector.detect_in_content(content)
        assert any(i.rule == "missing-needspace-section" for i in result.issues)
        assert any(i.section_type == "hebrewsection" for i in result.issues)

    def test_protected_section_no_issue(self):
        """Test that protected section doesn't trigger issue."""
        content = r"""Some content here.

\par\needspace{5\baselineskip}
\section{Protected Section}
This section is properly protected.
"""
        result = self.detector.detect_in_content(content)
        # Should not have missing-needspace issue for this section
        needspace_issues = [i for i in result.issues if i.rule == "missing-needspace-section"]
        assert len(needspace_issues) == 0

    def test_count_sections(self):
        """Test section counting."""
        content = r"""\section{First}
Content 1.

\subsection{Sub1}
Content 2.

\section{Second}
Content 3.
"""
        result = self.detector.detect_in_content(content)
        assert result.sections_checked == 3

    def test_count_protected_sections(self):
        """Test protected section counting."""
        content = r"""\needspace{5\baselineskip}
\section{Protected}
Content.

\section{Unprotected}
Content.
"""
        result = self.detector.detect_in_content(content)
        assert result.sections_protected == 1
        assert result.sections_unprotected == 1

    def test_subsection_threshold(self):
        """Test subsection uses 4-line threshold."""
        content = r"""Content.

\subsection{Sub Section}
"""
        result = self.detector.detect_in_content(content)
        issues = [i for i in result.issues if i.section_type == "subsection"]
        assert len(issues) >= 1
        # Check the fix mentions 4 baselineskip for subsection
        assert any("4" in i.fix for i in issues)

    def test_verdict_fail_on_high_severity(self):
        """Test verdict is FAIL when HIGH severity issues exist."""
        content = r"""\section{Unprotected}
Content.
"""
        result = self.detector.detect_in_content(content)
        assert result.verdict == "FAIL"

    def test_verdict_pass_when_protected(self):
        """Test verdict is PASS when all sections protected."""
        content = r"""\needspace{5\baselineskip}
\section{Protected}
This is a section with enough content.
More content here to fill the space.
Even more content for good measure.
And some additional text to be safe.
Final line of content.
"""
        result = self.detector.detect_in_content(content)
        # Should pass because section is protected
        needspace_issues = [i for i in result.issues if "needspace" in i.rule]
        assert len(needspace_issues) == 0

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"""\section{Test}
Content.
"""
        result = self.detector.detect_in_content(content)
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-section-orphan-detect"
        assert output["status"] == "DONE"
        assert output["verdict"] in ["PASS", "WARNING", "FAIL"]
        assert "issues" in output
        assert "summary" in output
        assert "sections_checked" in output["summary"]
        assert "sections_protected" in output["summary"]

    def test_get_rules(self):
        """Test get_rules returns all rules."""
        rules = self.detector.get_rules()
        assert "missing-needspace-section" in rules
        assert "missing-needspace-subsection" in rules
        assert "short-content-after-section" in rules
