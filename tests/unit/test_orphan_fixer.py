"""Unit tests for Section Orphan Fixer."""
import pytest
from qa_engine.typeset.fixing import SectionOrphanFixer, OrphanFixResult


class TestSectionOrphanFixer:
    """Tests for SectionOrphanFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = SectionOrphanFixer()

    def test_fix_unprotected_section(self):
        """Test fixing section without needspace."""
        content = r"""\section{Test Section}
Section content goes here.
"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 1
        assert r"\par\needspace{5\baselineskip}" in fixed

    def test_fix_unprotected_hebrewsection(self):
        """Test fixing hebrewsection without needspace."""
        content = r"""\hebrewsection{מבנה הפרוטוקול}
תוכן הקטע.
"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 1
        assert r"\par\needspace{5\baselineskip}" in fixed
        assert result.fixes_applied[0].section_type == "hebrewsection"

    def test_skip_protected_section(self):
        """Test that protected section is not modified."""
        content = r"""\par\needspace{5\baselineskip}
\section{Protected Section}
This section is already protected.
"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 0

    def test_fix_subsection_with_correct_threshold(self):
        """Test subsection uses 4-line threshold."""
        content = r"""\subsection{Sub Section}
Content.
"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 1
        # Check that 4 baselineskip is used for subsection
        assert r"\par\needspace{4\baselineskip}" in fixed
        assert result.fixes_applied[0].threshold == 4

    def test_fix_subsubsection_with_correct_threshold(self):
        """Test subsubsection uses 3-line threshold."""
        content = r"""\subsubsection{Sub Sub Section}
Content.
"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 1
        assert r"\par\needspace{3\baselineskip}" in fixed
        assert result.fixes_applied[0].threshold == 3

    def test_fix_multiple_sections(self):
        """Test fixing multiple unprotected sections."""
        content = r"""\section{First}
Content 1.

\subsection{Sub1}
Content 2.

\section{Second}
Content 3.
"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 3
        assert result.sections_protected == 3

    def test_fix_specific_lines_only(self):
        """Test fixing only specific line numbers."""
        content = r"""\section{First}
Content 1.

\section{Second}
Content 2.
"""
        # Only fix line 4 (second section)
        fixed, result = self.fixer.fix_content(content, line_numbers=[4])
        assert len(result.fixes_applied) == 1
        # First section should not be protected
        lines = fixed.split("\n")
        assert lines[0] == r"\section{First}"  # No needspace before

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"""\section{Test}
Content.
"""
        _, result = self.fixer.fix_content(content)
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-section-orphan-fix"
        assert output["status"] == "DONE"
        assert "fixes_applied" in output
        assert "summary" in output
        assert "files_modified" in output["summary"]
        assert "fixes_applied" in output["summary"]
        assert "sections_protected" in output["summary"]

    def test_fix_applied_has_required_fields(self):
        """Test that fix applied has all required fields."""
        content = r"""\section{Test Section}
Content.
"""
        _, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 1

        fix = result.fixes_applied[0]
        assert fix.section_type == "section"
        assert fix.section_title == "Test Section"
        assert fix.fix_type == "needspace"
        assert fix.threshold == 5
        assert fix.before is not None
        assert fix.after is not None

    def test_no_changes_status(self):
        """Test status when no changes needed."""
        content = r"""\par\needspace{5\baselineskip}
\section{Protected}
Already protected content.
"""
        _, result = self.fixer.fix_content(content)
        assert result.status == "NO_CHANGES"

    def test_done_status(self):
        """Test status when changes applied."""
        content = r"""\section{Unprotected}
Content.
"""
        _, result = self.fixer.fix_content(content)
        assert result.status == "DONE"
