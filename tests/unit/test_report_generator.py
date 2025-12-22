"""
Tests for Report Generator.

Tests for QA report generation in various formats.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path

from qa_engine.infrastructure.reporting.report_generator import (
    ReportGenerator,
    ReportFormat,
)
from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.domain.models.status import QAStatus


class TestReportGenerator:
    """Tests for ReportGenerator."""

    def setup_method(self):
        """Create generator and sample issues."""
        self.generator = ReportGenerator()
        self.issues = [
            Issue("bidi-numbers", "test.tex", 10, "123", Severity.WARNING, "\\en{123}"),
            Issue("bidi-english", "test.tex", 20, "hello", Severity.WARNING, "\\en{hello}"),
            Issue("bib-empty-cite", "main.tex", 5, "\\cite{}", Severity.CRITICAL, "Add key"),
        ]

    def test_generate_json_format(self):
        """Test JSON report generation."""
        report = self.generator.generate(self.issues, format=ReportFormat.JSON)
        data = json.loads(report)
        assert data["total_issues"] == 3
        assert "issues" in data
        assert len(data["issues"]) == 3

    def test_generate_json_by_severity(self):
        """Test JSON includes severity counts."""
        report = self.generator.generate(self.issues, format=ReportFormat.JSON)
        data = json.loads(report)
        assert "by_severity" in data
        assert data["by_severity"]["WARNING"] == 2
        assert data["by_severity"]["CRITICAL"] == 1

    def test_generate_json_by_rule(self):
        """Test JSON includes rule counts."""
        report = self.generator.generate(self.issues, format=ReportFormat.JSON)
        data = json.loads(report)
        assert "by_rule" in data
        assert data["by_rule"]["bidi-numbers"] == 1

    def test_generate_markdown_format(self):
        """Test Markdown report generation."""
        report = self.generator.generate(self.issues, format=ReportFormat.MARKDOWN)
        assert "# QA Report" in report
        assert "## Summary by Severity" in report
        assert "## Issues by File" in report

    def test_generate_markdown_includes_issues(self):
        """Test Markdown includes issue details."""
        report = self.generator.generate(self.issues, format=ReportFormat.MARKDOWN)
        assert "bidi-numbers" in report
        assert "Line 10" in report
        assert "123" in report

    def test_generate_markdown_with_status(self):
        """Test Markdown includes status info."""
        status = QAStatus(
            run_id="test-run",
            project_path="/test/project",
            started_at=datetime.now(),
        )
        report = self.generator.generate(self.issues, status, ReportFormat.MARKDOWN)
        assert "test-run" in report
        assert "/test/project" in report

    def test_generate_summary_format(self):
        """Test summary report generation."""
        report = self.generator.generate(self.issues, format=ReportFormat.SUMMARY)
        assert "QA Summary" in report
        assert "Total: 3 issues" in report

    def test_generate_summary_top_rules(self):
        """Test summary includes top rules."""
        report = self.generator.generate(self.issues, format=ReportFormat.SUMMARY)
        assert "Top Rules:" in report
        assert "bidi-numbers" in report

    def test_empty_issues_list(self):
        """Test report with no issues."""
        report = self.generator.generate([], format=ReportFormat.JSON)
        data = json.loads(report)
        assert data["total_issues"] == 0
        assert len(data["issues"]) == 0

    def test_save_to_file(self, tmp_path):
        """Test saving report to file."""
        output_file = tmp_path / "report.md"
        self.generator.save(self.issues, output_file, ReportFormat.MARKDOWN)
        assert output_file.exists()
        content = output_file.read_text()
        assert "# QA Report" in content

    def test_severity_icons(self):
        """Test severity icons in markdown."""
        report = self.generator.generate(self.issues, format=ReportFormat.MARKDOWN)
        # Warning and Critical icons should be present
        assert "🟡" in report or "🔴" in report

    def test_json_includes_generated_at(self):
        """Test JSON includes timestamp."""
        report = self.generator.generate(self.issues, format=ReportFormat.JSON)
        data = json.loads(report)
        assert "generated_at" in data

    def test_group_by_file(self):
        """Test issues grouped by file in markdown."""
        report = self.generator.generate(self.issues, format=ReportFormat.MARKDOWN)
        assert "### test.tex" in report
        assert "### main.tex" in report
