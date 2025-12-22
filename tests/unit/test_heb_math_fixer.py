"""Unit tests for Hebrew Math Fixer."""
import pytest
from qa_engine.infrastructure.fixing.heb_math_fixer import HebMathFixer


class TestHebMathFixer:
    """Tests for HebMathFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = HebMathFixer()

    def test_fix_text_to_hebmath(self):
        """Test converting \\text{Hebrew} to \\hebmath{Hebrew}."""
        content = r"$P(\text{שפעת}) = 0.025$"
        fixed, changes = self.fixer.fix_content(content)
        assert r"\hebmath{שפעת}" in fixed
        assert r"\text{שפעת}" not in fixed
        assert len(changes) == 1

    def test_skip_already_wrapped_hebmath(self):
        """Test that already wrapped content is not double-wrapped."""
        content = r"$P(\hebmath{שפעת}) = 0.025$"
        fixed, changes = self.fixer.fix_content(content)
        assert fixed == content
        assert len(changes) == 0

    def test_fix_textbf_to_hebmath(self):
        """Test converting \\textbf{Hebrew} to \\hebmath{\\textbf{}}."""
        content = r"$\textbf{מורכבות}$"
        fixed, changes = self.fixer.fix_content(content)
        assert r"\hebmath{\textbf{מורכבות}}" in fixed
        assert len(changes) == 1

    def test_fix_subscript_to_hebsub(self):
        """Test converting _{Hebrew} to _{\\hebsub{Hebrew}}."""
        content = r"$x_{מקסימום}$"
        fixed, changes = self.fixer.fix_content(content)
        assert r"_{\hebsub{מקסימום}}" in fixed
        assert len(changes) == 1

    def test_skip_already_wrapped_hebsub(self):
        """Test that already wrapped subscripts are not double-wrapped."""
        content = r"$x_{\hebsub{מקסימום}}$"
        fixed, changes = self.fixer.fix_content(content)
        assert fixed == content
        assert len(changes) == 0

    def test_fix_superscript_to_hebmath(self):
        """Test converting ^{Hebrew} to ^{\\hebmath{Hebrew}}."""
        content = r"$y^{ערך}$"
        fixed, changes = self.fixer.fix_content(content)
        assert r"^{\hebmath{ערך}}" in fixed
        assert len(changes) == 1

    def test_fix_cases_environment(self):
        r"""Test fixing \\text{} in cases environment."""
        content = r"""\begin{cases}
  x^2 & \text{אם } x > 0 \\
  0 & \text{אחרת}
\end{cases}"""
        fixed, changes = self.fixer.fix_content(content)
        assert r"\hebmath{אם }" in fixed
        assert r"\hebmath{אחרת}" in fixed
        assert len(changes) == 2

    def test_fix_incorrect_hebmath_definition(self):
        """Test removing duplicate \\hebmath definition (CLS provides it)."""
        content = r"\newcommand{\hebmath}[1]{\text{\texthebrew{#1}}}"
        fixed, changes = self.fixer.fix_content(content)
        # Fixer removes duplicate definition since CLS provides correct one
        assert fixed == ""
        assert r"\texthebrew" not in fixed
        assert len(changes) == 1

    def test_correct_hebmath_definition_unchanged(self):
        """Test that correct \\hebmath definition is not changed."""
        content = r"\newcommand{\hebmath}[1]{\text{\begingroup\selectlanguage{hebrew}\textdir TRT #1\endgroup}}"
        fixed, changes = self.fixer.fix_content(content)
        assert fixed == content

    def test_get_patterns_returns_all(self):
        """Test that get_patterns returns all fix patterns."""
        patterns = self.fixer.get_patterns()
        assert "text-to-hebmath" in patterns
        assert "textbf-to-hebmath" in patterns
        assert "subscript-to-hebsub" in patterns
        assert "superscript-to-hebmath" in patterns
        assert "hebmath-definition" in patterns

    def test_fix_line_text_rule(self):
        """Test fix_line with heb-math-text rule."""
        line = r"$P(\text{שפעת}) = 0.025$"
        fixed = self.fixer.fix_line(line, "heb-math-text")
        assert r"\hebmath{שפעת}" in fixed

    def test_fix_line_subscript_rule(self):
        """Test fix_line with heb-math-subscript rule."""
        line = r"$x_{מקסימום}$"
        fixed = self.fixer.fix_line(line, "heb-math-subscript")
        assert r"\hebsub{" in fixed

    def test_fix_line_superscript_rule(self):
        """Test fix_line with heb-math-superscript rule."""
        line = r"$y^{ערך}$"
        fixed = self.fixer.fix_line(line, "heb-math-superscript")
        assert r"\hebmath{" in fixed
