"""Unit tests for Subfiles Chapter Detector."""
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.infrastructure.detection.subfiles_chapter_detector import (
    SubfilesChapterDetector, SubfilesDetectResult, SubfilesIssue
)


class TestSubfilesChapterDetector:
    """Tests for SubfilesChapterDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = SubfilesChapterDetector(Path(self.temp_dir))
        (Path(self.temp_dir) / "chapters").mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_chapter(self, name: str, content: str) -> Path:
        """Helper to create a chapter file."""
        path = Path(self.temp_dir) / "chapters" / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_detect_properly_configured_file(self):
        """Test that properly configured file has no issues."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\begin{document}
\chapter{Test}
Content here.
\end{document}
"""
        self._create_chapter("chapter-good.tex", content)
        result = self.detector.detect_in_directory()
        assert result.verdict == "PASS"
        assert len(result.issues) == 0

    def test_detect_missing_documentclass(self):
        """Test Rule 1: Missing documentclass subfiles."""
        content = r"""
\chapter{Test}
Content here.
\begin{document}
\end{document}
"""
        self._create_chapter("chapter-bad.tex", content)
        result = self.detector.detect_in_directory()
        issues = [i for i in result.issues if i.rule == "missing-subfiles-documentclass"]
        assert len(issues) == 1
        assert issues[0].severity == "CRITICAL"

    def test_detect_missing_begin_document(self):
        """Test Rule 2: Missing begin{document}."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\chapter{Test}
Content here.
\end{document}
"""
        self._create_chapter("chapter-bad.tex", content)
        result = self.detector.detect_in_directory()
        issues = [i for i in result.issues if i.rule == "missing-begin-document"]
        assert len(issues) == 1
        assert issues[0].severity == "CRITICAL"

    def test_detect_missing_end_document(self):
        """Test Rule 3: Missing end{document}."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\begin{document}
\chapter{Test}
Content here.
"""
        self._create_chapter("chapter-bad.tex", content)
        result = self.detector.detect_in_directory()
        issues = [i for i in result.issues if i.rule == "missing-end-document"]
        assert len(issues) == 1
        assert issues[0].severity == "CRITICAL"

    def test_detect_all_three_missing(self):
        """Test file missing all three required elements."""
        content = r"""
\chapter{Test}
Content here without any subfiles structure.
"""
        self._create_chapter("chapter-bad.tex", content)
        result = self.detector.detect_in_directory()
        assert len(result.issues) == 3
        rules = [i.rule for i in result.issues]
        assert "missing-subfiles-documentclass" in rules
        assert "missing-begin-document" in rules
        assert "missing-end-document" in rules

    def test_multiple_files(self):
        """Test scanning multiple files."""
        good = r"""
\documentclass[../main.tex]{subfiles}
\begin{document}
\chapter{Good}
\end{document}
"""
        bad = r"\chapter{Bad}"

        self._create_chapter("chapter-01.tex", good)
        self._create_chapter("chapter-02.tex", bad)
        result = self.detector.detect_in_directory()

        assert result.files_checked == 2
        assert result.files_with_issues == 1

    def test_to_dict_output_format(self):
        """Test output matches skill.md JSON format."""
        content = r"\chapter{Test}"
        self._create_chapter("chapter.tex", content)
        result = self.detector.detect_in_directory()
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-infra-subfiles-detect"
        assert output["status"] == "DONE"
        assert output["verdict"] in ["PASS", "FAIL"]
        assert "issues" in output
        assert "summary" in output
        assert "triggers" in output

    def test_triggers_fix_skill_on_issues(self):
        """Test that fix skill is triggered when issues found."""
        content = r"\chapter{Test}"
        self._create_chapter("chapter.tex", content)
        result = self.detector.detect_in_directory()
        output = self.detector.to_dict(result)

        assert "qa-infra-subfiles-fix" in output["triggers"]

    def test_no_triggers_when_pass(self):
        """Test no fix trigger when all files pass."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\begin{document}
\chapter{Good}
\end{document}
"""
        self._create_chapter("chapter.tex", content)
        result = self.detector.detect_in_directory()
        output = self.detector.to_dict(result)

        assert output["triggers"] == []

    def test_get_rules(self):
        """Test get_rules returns all 3 rules."""
        rules = self.detector.get_rules()
        assert len(rules) == 3
        assert "missing-subfiles-documentclass" in rules
        assert "missing-begin-document" in rules
        assert "missing-end-document" in rules
