"""Unit tests for Hebrew Math Detector."""
import pytest
from qa_engine.infrastructure.detection.heb_math_detector import HebMathDetector
from qa_engine.domain.models.issue import Severity


class TestHebMathDetector:
    """Tests for HebMathDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = HebMathDetector()

    def test_get_rules_returns_all_6_rules(self):
        """Test that all 6 rules are returned."""
        rules = self.detector.get_rules()
        assert len(rules) == 6
        assert "heb-math-text" in rules
        assert "heb-math-textbf" in rules
        assert "heb-math-subscript" in rules
        assert "heb-math-superscript" in rules
        assert "heb-math-cases" in rules
        assert "heb-math-definition" in rules

    def test_rule1_hebrew_in_text_detected(self):
        """Rule 1: Hebrew in \\text{} should be detected."""
        content = r"$P(\text{שפעת}) = 0.025$"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 1
        assert issues[0].rule == "heb-math-text"

    def test_rule1_hebrew_in_hebmath_not_detected(self):
        """Rule 1: Hebrew wrapped in \\hebmath{} should NOT trigger."""
        content = r"$P(\hebmath{שפעת}) = 0.025$"
        issues = self.detector.detect(content, "test.tex")
        text_issues = [i for i in issues if i.rule == "heb-math-text"]
        assert len(text_issues) == 0

    def test_rule2_hebrew_in_textbf_in_math(self):
        """Rule 2: Hebrew in \\textbf{} in math mode detected."""
        content = r"$\textbf{מורכבות}$"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 1
        assert issues[0].rule == "heb-math-textbf"

    def test_rule2_textbf_outside_math_not_detected(self):
        """Rule 2: \\textbf{} outside math mode should NOT trigger."""
        content = r"\textbf{מורכבות}"
        issues = self.detector.detect(content, "test.tex")
        textbf_issues = [i for i in issues if i.rule == "heb-math-textbf"]
        assert len(textbf_issues) == 0

    def test_rule3_hebrew_subscript_detected(self):
        """Rule 3: Hebrew in subscript should be detected."""
        content = r"$x_{מקסימום}$"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 1
        assert issues[0].rule == "heb-math-subscript"

    def test_rule3_hebrew_subscript_wrapped_not_detected(self):
        """Rule 3: Hebrew subscript wrapped in \\hebsub{} NOT detected."""
        content = r"$x_{\hebsub{מקסימום}}$"
        issues = self.detector.detect(content, "test.tex")
        sub_issues = [i for i in issues if i.rule == "heb-math-subscript"]
        assert len(sub_issues) == 0

    def test_rule3_hebrew_superscript_detected(self):
        """Rule 3: Hebrew in superscript should be detected."""
        content = r"$y^{ערך}$"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 1
        assert issues[0].rule == "heb-math-superscript"

    def test_rule4_hebrew_in_cases_detected(self):
        """Rule 4: Hebrew in cases environment detected."""
        content = r"""\begin{cases}
  x^2 & \text{אם } x > 0 \\
  0 & \text{אחרת}
\end{cases}"""
        issues = self.detector.detect(content, "test.tex")
        cases_issues = [i for i in issues if i.rule == "heb-math-cases"]
        assert len(cases_issues) == 2

    def test_rule5_incorrect_hebmath_definition_detected(self):
        """Rule 5: Incorrect \\hebmath{} definition detected."""
        content = r"\newcommand{\hebmath}[1]{\text{\texthebrew{#1}}}"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 1
        assert issues[0].rule == "heb-math-definition"
        assert issues[0].severity == Severity.CRITICAL

    def test_rule5_correct_hebmath_definition_not_detected(self):
        """Rule 5: Correct \\hebmath{} with \\textdir TRT NOT detected."""
        content = r"\newcommand{\hebmath}[1]{\text{\begingroup\selectlanguage{hebrew}\textdir TRT #1\endgroup}}"
        issues = self.detector.detect(content, "test.tex")
        def_issues = [i for i in issues if i.rule == "heb-math-definition"]
        assert len(def_issues) == 0

    def test_skip_comment_lines(self):
        """Comments should be skipped."""
        content = r"% $\text{שפעת}$"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) == 0

    def test_offset_parameter(self):
        """Test that offset is correctly applied to line numbers."""
        content = r"$\text{שפעת}$"
        issues = self.detector.detect(content, "test.tex", offset=100)
        assert issues[0].line == 101

    def test_suggest_fix_formats_correctly(self):
        """Test fix suggestions contain content."""
        content = r"$x_{מקסימום}$"
        issues = self.detector.detect(content, "test.tex")
        assert "hebsub" in issues[0].fix.lower()
