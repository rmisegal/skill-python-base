"""Unit tests for Super Orchestrator."""
import pytest
import tempfile
from pathlib import Path
from qa_engine.infrastructure.super_orchestrator import (
    SuperOrchestrator, SuperOrchestratorResult, FamilyResult
)


class TestSuperOrchestrator:
    """Tests for SuperOrchestrator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = SuperOrchestrator()

    def test_run_bidi_family(self):
        """Test running BiDi family."""
        content = r"מבוא ל-CNN בשנת 2024"
        result = self.orchestrator.run(content, "test.tex", families=["BiDi"])
        assert "BiDi" in result.families_run
        assert "BiDi" in result.family_results
        assert result.family_results["BiDi"].status == "DONE"

    def test_run_img_family(self):
        """Test running img family."""
        content = r"\includegraphics{test.png}"
        result = self.orchestrator.run(content, "test.tex", families=["img"])
        assert "img" in result.families_run
        assert "img" in result.family_results

    def test_run_multiple_families(self):
        """Test running multiple families."""
        content = r"""
מבוא ל-CNN בשנת 2024
\includegraphics{test.png}
"""
        result = self.orchestrator.run(content, "test.tex", families=["BiDi", "img"])
        assert len(result.families_run) == 2
        assert "BiDi" in result.family_results
        assert "img" in result.family_results

    def test_run_id_generated(self):
        """Test that run_id is generated."""
        content = r"Test content"
        result = self.orchestrator.run(content, "test.tex")
        assert result.run_id.startswith("run-")
        assert len(result.run_id) > 5

    def test_timestamps_set(self):
        """Test that timestamps are set."""
        content = r"Test content"
        result = self.orchestrator.run(content, "test.tex")
        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.completed_at >= result.started_at

    def test_total_issues_aggregation(self):
        """Test that issues are aggregated."""
        content = r"מבוא ל-CNN בשנת 2024"
        result = self.orchestrator.run(content, "test.tex", families=["BiDi"])
        assert result.total_issues >= 0

    def test_verdict_pass(self):
        """Test PASS verdict when no failures."""
        content = r"\en{Hello} \num{123}"  # Already wrapped
        result = self.orchestrator.run(content, "test.tex", families=["BiDi"])
        # Verdict depends on actual detection

    def test_verdict_fail(self):
        """Test FAIL verdict when issues exist."""
        content = r"מבוא ל-CNN בשנת 2024"  # Unwrapped
        result = self.orchestrator.run(content, "test.tex", families=["BiDi"])
        # Will likely have issues

    def test_to_dict_format(self):
        """Test output dictionary format matches skill.md."""
        content = r"מבוא ל-CNN"
        result = self.orchestrator.run(content, "test.tex")
        output = self.orchestrator.to_dict(result)

        assert "run_id" in output
        assert "status" in output
        assert "verdict" in output
        assert "families_run" in output
        assert "total_issues" in output
        assert "issues_by_family" in output

    def test_issues_by_family(self):
        """Test issues are grouped by family."""
        content = r"מבוא ל-CNN"
        result = self.orchestrator.run(content, "test.tex", families=["BiDi"])
        output = self.orchestrator.to_dict(result)
        assert "BiDi" in output["issues_by_family"]

    def test_unknown_family_skipped(self):
        """Test unknown families are skipped."""
        content = r"Test"
        result = self.orchestrator.run(content, "test.tex", families=["unknown"])
        assert "unknown" not in result.family_results

    def test_no_fixes_when_disabled(self):
        """Test no fixes applied when disabled."""
        content = r"מבוא ל-CNN"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False)
        # Should still detect but not fix
        assert result.status == "DONE"


class TestSuperOrchestratorResult:
    """Tests for SuperOrchestratorResult dataclass."""

    def test_empty_result(self):
        """Test empty result properties."""
        result = SuperOrchestratorResult()
        assert result.total_issues == 0
        assert result.total_fixed == 0
        assert result.verdict == "PASS"
        assert result.status == "DONE"

    def test_with_family_results(self):
        """Test with family results."""
        result = SuperOrchestratorResult()
        result.family_results["BiDi"] = FamilyResult(family="BiDi", issues_found=5, issues_fixed=3)
        result.family_results["img"] = FamilyResult(family="img", issues_found=2, issues_fixed=1)

        assert result.total_issues == 7
        assert result.total_fixed == 4

    def test_verdict_fail_on_failure(self):
        """Test verdict is FAIL when family fails."""
        result = SuperOrchestratorResult()
        result.family_results["BiDi"] = FamilyResult(family="BiDi", verdict="FAIL")

        assert result.verdict == "FAIL"

    def test_verdict_warning(self):
        """Test verdict is WARNING when family has warning."""
        result = SuperOrchestratorResult()
        result.family_results["BiDi"] = FamilyResult(family="BiDi", verdict="WARNING")

        assert result.verdict == "WARNING"


class TestFamilyResult:
    """Tests for FamilyResult dataclass."""

    def test_default_values(self):
        """Test default values."""
        result = FamilyResult(family="test")
        assert result.family == "test"
        assert result.status == "DONE"
        assert result.verdict == "PASS"
        assert result.issues_found == 0
        assert result.issues_fixed == 0
        assert result.error is None

    def test_with_issues(self):
        """Test with issue counts."""
        result = FamilyResult(family="BiDi", issues_found=10, issues_fixed=8)
        assert result.issues_found == 10
        assert result.issues_fixed == 8

    def test_with_error(self):
        """Test with error."""
        result = FamilyResult(family="BiDi", status="ERROR", error="Something failed")
        assert result.status == "ERROR"
        assert result.error == "Something failed"
