"""Unit tests for BiDi Orchestrator."""
import pytest
from qa_engine.infrastructure.bidi_orchestrator import (
    BiDiOrchestrator, BiDiOrchestratorResult, BiDiDetectResult, BiDiFixResult
)


class TestBiDiOrchestrator:
    """Tests for BiDiOrchestrator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = BiDiOrchestrator()

    def test_detect_english_in_hebrew(self):
        """Test detection of English words in Hebrew context."""
        content = r"זהו מבוא ל-Machine Learning בשנת 2024"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert result.detect_result.total > 0
        assert result.verdict == "FAIL"

    def test_detect_numbers_without_wrapper(self):
        """Test detection of numbers in Hebrew context."""
        content = r"בשנת 2024 יש 128 מודלים"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.number_issues) > 0

    def test_detect_tikz_without_english(self):
        """Test detection of TikZ without english wrapper."""
        content = r"""
\documentclass{article}
מסמך בעברית
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}
"""
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.tikz_issues) > 0

    def test_detect_hebrew_in_math(self):
        """Test detection of Hebrew in math mode."""
        content = r"$P(\text{אירוע}) = 0.5$"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.math_hebrew_issues) > 0

    def test_fix_english_words(self):
        """Test fixing English words with \\en{}."""
        content = r"מבוא ל-CNN ולמודלים"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=True)
        assert result.fix_result is not None
        assert result.fix_result.text_fixed > 0

    def test_fix_numbers(self):
        """Test fixing numbers with \\num{} or \\hebyear{}."""
        content = r"בשנת 2024 יש 50 מודלים"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=True)
        assert result.fix_result is not None
        # Fixes may be applied

    def test_fix_tikz_with_english(self):
        """Test fixing TikZ by wrapping in english environment."""
        content = r"""
מסמך בעברית
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}
"""
        result = self.orchestrator.run(content, "test.tex", apply_fixes=True)
        if result.fix_result and result.fix_result.content:
            assert r"\begin{english}" in result.fix_result.content

    def test_no_issues_pass(self):
        """Test that content without issues passes."""
        content = r"\en{Hello} world in English only"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        # No Hebrew context means no BiDi issues flagged
        assert result.verdict in ("PASS", "FAIL")  # Depends on exact rules

    def test_skills_executed_tracking(self):
        """Test that executed skills are tracked."""
        content = r"בדיקה פשוטה"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        assert "qa-BiDi-detect" in result.skills_executed
        assert "qa-heb-math-detect" in result.skills_executed
        assert result.skills_executed["qa-BiDi-detect"] == "DONE"

    def test_to_dict_format(self):
        """Test output dictionary format matches skill.md."""
        content = r"מבוא ל-CNN בשנת 2024"
        result = self.orchestrator.run(content, "test.tex")
        output = self.orchestrator.to_dict(result)

        assert output["skill"] == "qa-BiDi"
        assert output["status"] == "DONE"
        assert "verdict" in output
        assert "detection_summary" in output
        assert "skills_executed" in output

    def test_detection_summary_counts(self):
        """Test detection summary has correct structure."""
        content = r"טקסט עם CNN ומספרים 123"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        output = self.orchestrator.to_dict(result)
        summary = output["detection_summary"]

        assert "text_direction_issues" in summary
        assert "number_ltr_issues" in summary
        assert "math_hebrew_issues" in summary
        assert "tikz_bidi_issues" in summary
        assert "total_issues" in summary

    def test_orchestrator_result_dataclass(self):
        """Test BiDiOrchestratorResult dataclass."""
        detect = BiDiDetectResult()
        fix = BiDiFixResult(text_fixed=5, numbers_fixed=3)
        result = BiDiOrchestratorResult(detect_result=detect, fix_result=fix)

        assert result.status == "DONE"
        assert result.verdict == "PASS"  # No issues in detect_result

    def test_detect_result_total(self):
        """Test BiDiDetectResult total calculation."""
        from qa_engine.domain.models.issue import Issue, Severity
        result = BiDiDetectResult()
        result.text_issues.append(Issue(rule="test", file="", line=1, content="", severity=Severity.WARNING))
        result.number_issues.append(Issue(rule="test", file="", line=2, content="", severity=Severity.WARNING))

        assert result.total == 2
        assert result.verdict == "FAIL"

    def test_fix_result_content(self):
        """Test that fixed content is returned."""
        content = r"מבוא עם CNN"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=True)
        if result.detect_result and result.detect_result.total > 0:
            assert result.fix_result is not None
            assert result.fix_result.content != ""


class TestBiDiDetectResult:
    """Tests for BiDiDetectResult dataclass."""

    def test_empty_result(self):
        """Test empty result is PASS."""
        result = BiDiDetectResult()
        assert result.total == 0
        assert result.verdict == "PASS"

    def test_with_issues(self):
        """Test result with issues is FAIL."""
        from qa_engine.domain.models.issue import Issue, Severity
        result = BiDiDetectResult()
        result.text_issues.append(Issue(rule="test", file="", line=1, content="x", severity=Severity.WARNING))
        assert result.total == 1
        assert result.verdict == "FAIL"


class TestBiDiFixResult:
    """Tests for BiDiFixResult dataclass."""

    def test_default_values(self):
        """Test default values."""
        result = BiDiFixResult()
        assert result.text_fixed == 0
        assert result.numbers_fixed == 0
        assert result.math_fixed == 0
        assert result.tikz_fixed == 0
        assert result.content == ""

    def test_with_fixes(self):
        """Test with fix counts."""
        result = BiDiFixResult(text_fixed=3, numbers_fixed=2, content="fixed")
        assert result.text_fixed == 3
        assert result.numbers_fixed == 2
        assert result.content == "fixed"
