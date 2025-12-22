"""Unit tests for Mdframed Fixer."""
import shutil
import tempfile
from pathlib import Path
import pytest
from qa_engine.typeset.fixing import MdframedFixer, MdframedFixResult


class TestMdframedFixer:
    """Tests for MdframedFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = MdframedFixer()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_fix_content_adds_vspace(self):
        """Test fixing adds vspace before dobox."""
        content = r"""Some text here.

\begin{dobox}[Title]
Content
\end{dobox}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\vspace{1em}" in fixed
        assert len(result.fixes_applied) == 1

    def test_fix_content_adds_nopagebreak_after_heading(self):
        """Test fixing adds nopagebreak when box follows heading."""
        content = r"""\section{Test Section}

\begin{dobox}[Title]
Content
\end{dobox}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\nopagebreak" in fixed
        assert result.fixes_applied[0].strategy == "nopagebreak"

    def test_fix_content_dontbox(self):
        """Test fixing dontbox environment."""
        content = r"""Text here.

\begin{dontbox}[Warning]
Don't do this
\end{dontbox}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\vspace{1em}" in fixed
        assert len(result.fixes_applied) == 1

    def test_fix_content_tcolorbox(self):
        """Test fixing tcolorbox environment."""
        content = r"""Text here.

\begin{tcolorbox}[title=Note]
Note content
\end{tcolorbox}"""
        fixed, result = self.fixer.fix_content(content)
        assert r"\vspace{1em}" in fixed

    def test_fix_specific_line(self):
        """Test fixing specific line number."""
        content = r"""Line 1
Line 2
\begin{dobox}[First]
Content 1
\end{dobox}
Line 6
\begin{dobox}[Second]
Content 2
\end{dobox}"""
        # Only fix line 3
        fixed, result = self.fixer.fix_content(content, line_numbers=[3])
        assert len(result.fixes_applied) == 1
        # The second box (originally line 7) should NOT have vspace before it
        # After fix, line 6 content should appear after end{dobox}
        assert "Line 6" in fixed
        # Only one vspace should be added
        assert fixed.count(r"\vspace") == 1

    def test_fix_file_creates_backup(self):
        """Test fixing a file works correctly."""
        test_file = Path(self.temp_dir) / "test.tex"
        test_file.write_text(r"""Some text.

\begin{dobox}[Title]
Content
\end{dobox}""")

        result = self.fixer.fix_file(test_file)
        assert result.files_modified == 1

        # Check file was modified
        new_content = test_file.read_text()
        assert r"\vspace{1em}" in new_content

    def test_fix_multiple_boxes(self):
        """Test fixing multiple box environments."""
        content = r"""Text 1

\begin{dobox}[First]
First content
\end{dobox}

Text 2

\begin{dontbox}[Second]
Second content
\end{dontbox}"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 2
        assert fixed.count(r"\vspace") == 2

    def test_no_fix_needed(self):
        """Test content without boxes needs no fix."""
        content = r"""Just regular text.

\section{Section}
More text here.
"""
        fixed, result = self.fixer.fix_content(content)
        assert len(result.fixes_applied) == 0
        assert result.status == "NO_CHANGES"

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"""Text

\begin{dobox}[Title]
Content
\end{dobox}"""
        _, result = self.fixer.fix_content(content)
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-mdframed-fix"
        assert output["status"] == "DONE"
        assert "fixes_applied" in output
        assert "summary" in output
        assert "files_modified" in output["summary"]
        assert "fixes_applied" in output["summary"]

    def test_strategy_vspace_long_for_long_paragraph(self):
        """Test vspace_long strategy for long preceding content."""
        # Create content with long paragraph before box
        long_para = "A" * 600  # >500 chars
        content = f"""{long_para}

\\begin{{dobox}}[Title]
Content
\\end{{dobox}}"""
        fixed, result = self.fixer.fix_content(content)
        assert result.fixes_applied[0].strategy == "vspace_long"
        assert r"\vspace{1.5em}" in fixed
