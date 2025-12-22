"""Unit tests for QASuperFormatter."""

from datetime import datetime

import pytest
from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.domain.models.status import QAStatus, ExecutionState
from qa_engine.infrastructure.reporting.report_models import (
    QASuperReport, FamilyResult, CLSCheckResult,
)
from qa_engine.infrastructure.reporting.qa_super_formatter import QASuperFormatter


class TestQASuperFormatter:
    """Test cases for QASuperFormatter."""

    def test_format_basic_report(self):
        """Test basic report formatting."""
        report = QASuperReport(document_name="test-project")
        report.families.append(FamilyResult(
            family="BiDi", verdict="PASS", issues_found=0,
        ))

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "# QA Super Report" in markdown
        assert "test-project" in markdown
        assert "BiDi" in markdown
        assert "PASS" in markdown

    def test_format_with_cls_check(self):
        """Test report with CLS check result."""
        report = QASuperReport(document_name="test")
        report.cls_check = CLSCheckResult(
            status="FIXED",
            version="2.0.0",
            action_taken="Updated CLS and 5 .tex files",
        )

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "Pre-QA Checks" in markdown
        assert "CLS Version" in markdown
        assert "FIXED" in markdown

    def test_format_family_results_table(self):
        """Test family results table formatting."""
        report = QASuperReport(document_name="test")
        report.families = [
            FamilyResult("BiDi", "PASS", 0, 0, True),
            FamilyResult("code", "FAIL", 5, 3, True),
            FamilyResult("table", "WARNING", 2, 1, False),
        ]

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "| BiDi |" in markdown
        assert "| code |" in markdown
        assert "| table |" in markdown
        assert "Detection Verified" in markdown

    def test_format_critical_issues(self):
        """Test critical issues section."""
        report = QASuperReport(document_name="test")
        report.critical_issues.append(Issue(
            rule="test-rule",
            file="test.tex",
            line=10,
            content="Critical bug here",
            severity=Severity.CRITICAL,
        ))

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "Critical Issues" in markdown
        assert "test-rule" in markdown
        assert "test.tex" in markdown

    def test_format_warnings(self):
        """Test warnings section."""
        report = QASuperReport(document_name="test")
        report.warnings.append(Issue(
            rule="warning-rule",
            file="chapter.tex",
            line=50,
            content="Minor issue",
            severity=Severity.WARNING,
        ))

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "Warnings" in markdown
        assert "warning-rule" in markdown

    def test_format_recommendations(self):
        """Test recommendations section."""
        report = QASuperReport(document_name="test")
        report.recommendations = [
            "Review all BiDi issues",
            "Run compilation again",
        ]

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "Recommendations" in markdown
        assert "Review all BiDi issues" in markdown

    def test_calculate_verdict_pass(self):
        """Test verdict calculation - PASS."""
        report = QASuperReport(document_name="test")
        report.families = [
            FamilyResult("BiDi", "PASS", 0, 0),
            FamilyResult("code", "PASS", 0, 0),
        ]
        report.cls_check = CLSCheckResult(status="CURRENT")

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "PASS" in markdown

    def test_calculate_verdict_fail(self):
        """Test verdict calculation - FAIL."""
        report = QASuperReport(document_name="test")
        report.families = [
            FamilyResult("BiDi", "FAIL", 5, 0),
        ]

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "FAIL" in markdown

    def test_calculate_verdict_warning(self):
        """Test verdict calculation - WARNING."""
        report = QASuperReport(document_name="test")
        report.families = [
            FamilyResult("BiDi", "PASS", 0, 0),
            FamilyResult("typeset", "WARNING", 3, 0),
        ]

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "WARNING" in markdown

    def test_from_status(self):
        """Test creating report from QAStatus."""
        status = QAStatus(
            run_id="test-run",
            project_path="/test/path",
            started_at=datetime.now(),
        )
        status.mark_started("BiDi", "agent-1")
        status.mark_completed("BiDi", 3)

        issues = [
            Issue("bidi-rule", "test.tex", 10, "test", Severity.WARNING),
        ]

        formatter = QASuperFormatter()
        report = formatter.from_status(status, issues, "test-doc")

        assert report.document_name == "test-doc"
        assert len(report.families) == 1
        assert len(report.warnings) == 1

    def test_empty_sections_handled(self):
        """Test empty sections don't break formatting."""
        report = QASuperReport(document_name="empty-test")

        formatter = QASuperFormatter()
        markdown = formatter.format(report)

        assert "No critical issues found" in markdown
        assert "No warnings" in markdown
        assert "No additional recommendations" in markdown
