"""Unit tests for Mdframed Detector."""
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.typeset.detection.mdframed_detector import (
    MdframedDetector, MdframedDetectResult, MdframedIssue
)


class TestMdframedDetector:
    """Tests for MdframedDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = MdframedDetector(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_log(self, name: str, content: str) -> Path:
        """Helper to create a log file."""
        path = Path(self.temp_dir) / name
        path.write_text(content, encoding="utf-8")
        return path

    def _create_tex(self, name: str, content: str) -> Path:
        """Helper to create a tex file."""
        path = Path(self.temp_dir) / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_detect_mdframed_warning(self):
        """Test Rule 1: Detect mdframed bad break warning."""
        log_content = """
(./chapters/chapter02.tex)
Package mdframed Warning: You got a bad break
(mdframed)                because the last box will be
(mdframed)                splitted!
(mdframed)                Please insert a clearpage before this box.
"""
        log_path = self._create_log("main.log", log_content)
        result = self.detector.detect_in_log(log_path)

        assert result.mdframed_warnings == 1
        assert len(result.issues) == 1
        assert result.issues[0].issue_type == "mdframed-bad-break"
        assert result.verdict == "WARNING"

    def test_detect_tcolorbox_warning(self):
        """Test Rule 2: Detect tcolorbox split warning."""
        log_content = """
(./chapters/chapter03.tex)
Package tcolorbox Warning: This box will be splitted due to breakable
"""
        log_path = self._create_log("main.log", log_content)
        result = self.detector.detect_in_log(log_path)

        assert result.tcolorbox_warnings == 1
        assert len(result.issues) == 1
        assert result.issues[0].issue_type == "tcolorbox-split"

    def test_detect_multiple_warnings(self):
        """Test detection of multiple warnings."""
        log_content = """
Package mdframed Warning: You got a bad break
Package tcolorbox Warning: This box will be splitted
Package mdframed Warning: You got a bad break
"""
        log_path = self._create_log("main.log", log_content)
        result = self.detector.detect_in_log(log_path)

        assert result.mdframed_warnings == 2
        assert result.tcolorbox_warnings == 1
        assert result.total == 3

    def test_no_warnings_pass(self):
        """Test verdict PASS when no warnings."""
        log_content = """
This is pdfTeX, Version 3.14159265
(./main.tex)
Output written on main.pdf
"""
        log_path = self._create_log("main.log", log_content)
        result = self.detector.detect_in_log(log_path)

        assert result.verdict == "PASS"
        assert result.total == 0

    def test_detect_box_near_section_in_source(self):
        """Test Rule 4: Detect box environments near sections."""
        tex_content = r"""
\chapter{Introduction}

\section{Background}
Some introductory text here.

\begin{dobox}[title=Important]
This box is close to the section heading.
\end{dobox}
"""
        tex_path = self._create_tex("chapter.tex", tex_content)
        issues = self.detector.detect_in_source(tex_path)

        assert len(issues) == 1
        assert issues[0].issue_type == "box-near-section"
        assert issues[0].environment == "dobox"
        assert "Background" in issues[0].section

    def test_to_dict_format(self):
        """Test output matches skill.md JSON format."""
        log_content = """Package mdframed Warning: You got a bad break"""
        log_path = self._create_log("main.log", log_content)
        result = self.detector.detect_in_log(log_path)
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-mdframed-detect"
        assert output["status"] == "DONE"
        assert output["verdict"] == "WARNING"
        assert "issues" in output
        assert "summary" in output
        assert "triggers" in output
        assert "qa-mdframed-fix" in output["triggers"]

    def test_to_dict_no_triggers_on_pass(self):
        """Test no triggers when verdict is PASS."""
        result = MdframedDetectResult()
        output = self.detector.to_dict(result)

        assert output["verdict"] == "PASS"
        assert output["triggers"] == []

    def test_get_rules(self):
        """Test get_rules returns all 4 rules."""
        rules = self.detector.get_rules()
        assert len(rules) == 4
        assert "mdframed-bad-break" in rules
        assert "tcolorbox-split" in rules
        assert "underfull-vbox-near-box" in rules
        assert "box-near-section" in rules

    def test_extracts_fix_recommendation(self):
        """Test that fix recommendations are generated."""
        log_content = """Package mdframed Warning: You got a bad break"""
        log_path = self._create_log("main.log", log_content)
        result = self.detector.detect_in_log(log_path)

        assert result.issues[0].fix
        assert "clearpage" in result.issues[0].fix.lower()

    def test_nonexistent_log_returns_empty(self):
        """Test handling of nonexistent log file."""
        result = self.detector.detect_in_log(Path("/nonexistent/path.log"))
        assert result.verdict == "PASS"
        assert result.total == 0
