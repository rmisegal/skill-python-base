"""Unit tests for Infrastructure Orchestrator."""
import pytest
from pathlib import Path
from qa_engine.infrastructure.infra_orchestrator import InfraOrchestrator


class TestInfraOrchestrator:
    """Tests for InfraOrchestrator."""

    def setup_method(self):
        self.orch = InfraOrchestrator(project_root=Path.cwd())

    def test_run_scan_only(self):
        """Test running scan without fixes."""
        result = self.orch.run(apply_fixes=False)
        assert result.scan_result is not None
        assert result.skills_executed["qa-infra-scan"] == "DONE"
        assert result.skills_executed["qa-infra-reorganize"] == "SKIP"

    def test_result_properties(self):
        """Test result properties work correctly."""
        result = self.orch.run(apply_fixes=False)
        assert isinstance(result.total_issues, int)
        assert isinstance(result.total_fixed, int)
        assert result.verdict in ["PASS", "WARNING", "FAIL"]
        assert result.status == "DONE"

    def test_to_dict_format(self):
        """Test to_dict returns correct format."""
        result = self.orch.run(apply_fixes=False)
        d = self.orch.to_dict(result)
        assert d["family"] == "infra"
        assert "scan" in d
        assert "reorganize" in d
        assert "skills_executed" in d

    def test_scan_detects_directories(self):
        """Test scan detects required directories."""
        result = self.orch.run(apply_fixes=False)
        scan = result.scan_result
        assert scan.required_dirs > 0
        assert isinstance(scan.missing_dirs, list)
