"""Unit tests for code detector."""
import pytest
from qa_engine.infrastructure.detection.code_detector import CodeDetector


class TestCodeDetectorHebrewWrapping:
    """Tests for Hebrew wrapping detection in code blocks."""

    def setup_method(self):
        self.detector = CodeDetector()

    def test_no_issue_when_hebrew_wrapped(self):
        """No issue when Hebrew is in hebtitle."""
        content = r"\begin{pythonbox}[\hebtitle{התקנה}]" + "\ncode\n" + r"\end{pythonbox}"
        issues = list(self.detector.detect(content, "test.tex"))
        hebrew_issues = [i for i in issues if i.rule == "code-direction-hebrew"]
        assert len(hebrew_issues) == 0

    def test_no_issue_on_begin_line(self):
        """No issue for Hebrew on begin line."""
        content = r"\begin{pythonbox}[התקנה]" + "\ncode\n" + r"\end{pythonbox}"
        issues = list(self.detector.detect(content, "test.tex"))
        hebrew_issues = [i for i in issues if i.rule == "code-direction-hebrew"]
        assert len(hebrew_issues) == 0

    def test_detect_unwrapped_hebrew_in_code(self):
        """Detect Hebrew text without wrapper in code."""
        content = r"\begin{pythonbox}" + "\n# שלום\n" + r"\end{pythonbox}"
        issues = list(self.detector.detect(content, "test.tex"))
        hebrew_issues = [i for i in issues if i.rule == "code-direction-hebrew"]
        assert len(hebrew_issues) > 0


class TestCodeDetectorBackgroundOverflow:
    """Tests for background overflow detection."""

    def setup_method(self):
        self.detector = CodeDetector()

    def test_detect_pythonbox_without_english(self):
        """Detect pythonbox without english wrapper."""
        content = r"\begin{pythonbox}" + "\ncode\n" + r"\end{pythonbox}"
        issues = list(self.detector.detect(content, "test.tex"))
        overflow = [i for i in issues if i.rule == "code-background-overflow"]
        assert len(overflow) == 1

    def test_no_issue_when_wrapped_in_english(self):
        """No issue when pythonbox is in english environment."""
        content = r"\begin{english}" + "\n" + r"\begin{pythonbox}" + "\n" + r"\end{pythonbox}" + "\n" + r"\end{english}"
        issues = list(self.detector.detect(content, "test.tex"))
        overflow = [i for i in issues if i.rule == "code-background-overflow"]
        assert len(overflow) == 0
