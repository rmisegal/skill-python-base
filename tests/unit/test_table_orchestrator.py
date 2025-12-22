"""Unit tests for Table Orchestrator."""
import pytest
from qa_engine.infrastructure.table_orchestrator import TableOrchestrator


class TestTableOrchestrator:
    """Tests for TableOrchestrator."""

    def setup_method(self):
        self.orch = TableOrchestrator()

    def test_run_no_tables(self):
        """Test with content that has no tables."""
        content = r"\documentclass{article}\begin{document}Hello\end{document}"
        result = self.orch.run(content, "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert result.total_issues == 0
        assert result.verdict == "PASS"

    def test_run_with_table(self):
        """Test with content containing a table."""
        content = r"""
\begin{table}
\begin{tabular}{|l|r|}
\hline
Name & Value \\
\hline
\end{tabular}
\end{table}
"""
        result = self.orch.run(content, "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert result.detect_result.tables_found >= 1

    def test_skills_executed_tracking(self):
        """Test that skills are tracked."""
        content = "No tables here"
        result = self.orch.run(content, "test.tex")
        assert "qa-table-detect" in result.skills_executed
        assert result.skills_executed["qa-table-detect"] == "DONE"

    def test_to_dict_format(self):
        """Test to_dict returns correct format."""
        content = "No tables"
        result = self.orch.run(content, "test.tex")
        d = self.orch.to_dict(result)
        assert d["family"] == "table"
        assert "detection" in d
        assert "fixes" in d
        assert "skills_executed" in d
