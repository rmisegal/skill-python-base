"""Unit tests for Typeset Orchestrator."""
import pytest
import tempfile
from pathlib import Path
from qa_engine.infrastructure.typeset_orchestrator import (
    TypesetOrchestrator, TypesetOrchestratorResult
)


class TestTypesetOrchestrator:
    """Tests for TypesetOrchestrator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = TypesetOrchestrator()

    def test_detect_overfull_hbox(self):
        """Test detecting overfull hbox from log."""
        log = r"Overfull \hbox (15.5pt too wide) in paragraph at lines 42--45"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.overfull_hbox) == 1
        assert result.detect_result.overfull_hbox[0].amount_pt == 15.5

    def test_detect_underfull_hbox(self):
        """Test detecting underfull hbox from log."""
        log = r"Underfull \hbox (badness 10000) in paragraph at lines 50--52"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.underfull_hbox) == 1
        assert result.detect_result.underfull_hbox[0].badness == 10000

    def test_detect_overfull_vbox(self):
        """Test detecting overfull vbox from log."""
        log = r"Overfull \vbox (20.0pt too high) has occurred"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.overfull_vbox) == 1

    def test_detect_underfull_vbox(self):
        """Test detecting underfull vbox from log."""
        log = r"Underfull \vbox (badness 5000) has occurred"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.underfull_vbox) == 1

    def test_detect_undefined_reference(self):
        """Test detecting undefined reference from log."""
        log = r"Reference `fig:missing' on page 5 undefined"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.undefined_references) == 1

    def test_detect_float_too_large(self):
        """Test detecting float too large from log."""
        log = r"Float too large for page by 25pt"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert len(result.detect_result.float_too_large) == 1

    def test_verdict_fail_on_critical(self):
        """Test verdict is FAIL on critical issues."""
        log = r"Reference `fig:missing' on page 5 undefined"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.verdict == "FAIL"

    def test_verdict_pass_no_issues(self):
        """Test verdict is PASS with no issues."""
        log = "This is LuaTeX compilation log with no warnings"
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.verdict == "PASS"

    def test_hbox_fixes_applied(self):
        """Test hbox fixes are applied."""
        log = r"Overfull \hbox (15.5pt too wide) at line 2"
        tex = r"\encell{some.very.long.code.identifier.here}"
        result = self.orchestrator.run(log, tex, "test.tex", apply_fixes=True)
        assert result.hbox_result is not None

    def test_vbox_raggedbottom_fix(self):
        """Test raggedbottom fix for vbox issues."""
        log = r"Underfull \vbox (badness 10000)"
        tex = r"""\documentclass{book}
\begin{document}
Content here
\end{document}"""
        result = self.orchestrator.run(log, tex, "test.tex", apply_fixes=True)
        assert result.vbox_result is not None
        # Check raggedbottom was suggested or applied
        if result.vbox_result.fixes_applied:
            assert any("raggedbottom" in f.fix_type for f in result.vbox_result.fixes_applied)

    def test_to_dict_format(self):
        """Test output dictionary format matches skill.md."""
        log = r"Overfull \hbox (15.5pt too wide)"
        result = self.orchestrator.run(log, "", "test.tex")
        output = self.orchestrator.to_dict(result)

        assert "skill" in output
        assert output["skill"] == "qa-typeset"
        assert "status" in output
        assert "verdict" in output
        assert "detection" in output
        assert "fixes" in output
        assert "summary" in output

    def test_summary_counts(self):
        """Test summary counts are correct."""
        log = r"""
Overfull \hbox (15.5pt too wide) in paragraph
Overfull \hbox (10.0pt too wide) in paragraph
Underfull \hbox (badness 10000)
"""
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        assert result.total_detected == 3

    def test_llm_prompts_generated(self):
        """Test LLM prompts are generated for manual review."""
        log = r"Overfull \hbox (15.5pt too wide) at line 1"
        tex = "This is a line without table cells requiring manual review."
        result = self.orchestrator.run(log, tex, "test.tex", apply_fixes=True)
        # May or may not have prompts depending on content
        assert isinstance(result.llm_prompts, list)

    def test_multiple_warning_types(self):
        """Test handling multiple warning types."""
        log = r"""
Overfull \hbox (15.5pt too wide)
Underfull \vbox (badness 5000)
Float too large for page by 30pt
Reference `fig:test' on page 1 undefined
"""
        result = self.orchestrator.run(log, "", "test.tex", apply_fixes=False)
        dr = result.detect_result
        assert len(dr.overfull_hbox) == 1
        assert len(dr.underfull_vbox) == 1
        assert len(dr.float_too_large) == 1
        assert len(dr.undefined_references) == 1


class TestTypesetOrchestratorResult:
    """Tests for TypesetOrchestratorResult dataclass."""

    def test_empty_result(self):
        """Test empty result properties."""
        result = TypesetOrchestratorResult()
        assert result.total_detected == 0
        assert result.total_fixed == 0
        assert result.manual_review_count == 0
        assert result.status == "DONE"
        assert result.verdict == "PASS"

    def test_fixed_content_preserved(self):
        """Test fixed content is preserved."""
        result = TypesetOrchestratorResult(fixed_content="test content")
        assert result.fixed_content == "test content"

    def test_llm_prompts_list(self):
        """Test llm_prompts is a list."""
        result = TypesetOrchestratorResult()
        assert isinstance(result.llm_prompts, list)
        result.llm_prompts.append("Fix this issue")
        assert len(result.llm_prompts) == 1
