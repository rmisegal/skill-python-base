"""
QA Super Report Formatter - matches qa-super skill.md report template.
"""

from __future__ import annotations

from typing import List

from ...domain.models.issue import Issue, Severity
from ...domain.models.status import QAStatus, ExecutionState
from .report_models import CLSCheckResult, FamilyResult, QASuperReport


class QASuperFormatter:
    """Formats QA reports matching qa-super skill.md template."""

    def format(self, report: QASuperReport) -> str:
        """Generate markdown report matching skill.md template."""
        lines = [
            "# QA Super Report", "",
            f"**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", "",
        ]
        lines.extend(self._format_pre_qa_checks(report))
        lines.extend(self._format_summary(report))
        lines.extend(self._format_family_results(report))
        lines.extend(self._format_critical_issues(report))
        lines.extend(self._format_warnings(report))
        lines.extend(self._format_recommendations(report))
        return "\n".join(lines)

    def _format_pre_qa_checks(self, report: QASuperReport) -> List[str]:
        """Format Pre-QA Checks section."""
        lines = ["## Pre-QA Checks (Phase 0)", "",
                 "| Check | Status | Action Taken |", "|-------|--------|--------------|"]
        if report.cls_check:
            icon = "✅" if report.cls_check.status == "CURRENT" else "🔧"
            action = report.cls_check.action_taken or "None required"
            lines.append(f"| CLS Version | {icon} {report.cls_check.status} | {action} |")
        else:
            lines.append("| CLS Version | ⏭️ SKIPPED | Not checked |")
        return lines + [""]

    def _format_summary(self, report: QASuperReport) -> List[str]:
        """Format Summary section."""
        total = sum(f.issues_found for f in report.families)
        fixed = sum(f.issues_fixed for f in report.families)
        return ["## Summary", "", f"- **Document:** {report.document_name}",
                f"- **Families executed:** {len(report.families)}",
                f"- **Total issues:** {total}", f"- **Issues fixed:** {fixed}",
                f"- **Verdict:** {self._calculate_verdict(report)}", ""]

    def _format_family_results(self, report: QASuperReport) -> List[str]:
        """Format Family Results table."""
        lines = ["## Family Results", "",
                 "| Family | Verdict | Issues | Fixed | Detection Verified |",
                 "|--------|---------|--------|-------|-------------------|"]
        for f in report.families:
            icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}.get(f.verdict, "❓")
            v = "✅" if f.detection_verified else "❌"
            lines.append(f"| {f.family} | {icon} {f.verdict} | {f.issues_found} | {f.issues_fixed} | {v} |")
        return lines + [""]

    def _format_critical_issues(self, report: QASuperReport) -> List[str]:
        """Format Critical Issues section."""
        lines = ["## Critical Issues", ""]
        if not report.critical_issues:
            return lines + ["No critical issues found.", ""]
        for i in report.critical_issues[:10]:
            lines.append(f"- **{i.rule}** in `{i.file}:{i.line}`: {i.content[:50]}")
        return lines + [""]

    def _format_warnings(self, report: QASuperReport) -> List[str]:
        """Format Warnings section."""
        lines = ["## Warnings", ""]
        if not report.warnings:
            return lines + ["No warnings.", ""]
        for i in report.warnings[:10]:
            lines.append(f"- {i.rule} in `{i.file}:{i.line}`")
        return lines + [""]

    def _format_recommendations(self, report: QASuperReport) -> List[str]:
        """Format Recommendations section."""
        lines = ["## Recommendations", ""]
        if not report.recommendations:
            return lines + ["No additional recommendations.", ""]
        for r in report.recommendations:
            lines.append(f"- {r}")
        return lines + [""]

    def _calculate_verdict(self, report: QASuperReport) -> str:
        """Calculate overall verdict."""
        if any(f.verdict == "FAIL" for f in report.families):
            return "❌ FAIL"
        if any(f.verdict == "WARNING" for f in report.families):
            return "⚠️ WARNING"
        if report.cls_check and report.cls_check.status not in ("CURRENT", "FIXED"):
            return "❌ FAIL"
        return "✅ PASS"

    def from_status(self, status: QAStatus, issues: List[Issue], doc_name: str) -> QASuperReport:
        """Create report from QAStatus and issues."""
        report = QASuperReport(document_name=doc_name)
        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                report.critical_issues.append(issue)
            elif issue.severity == Severity.WARNING:
                report.warnings.append(issue)

        for skill_name, entry in status.entries.items():
            family_issues = [i for i in issues if skill_name.lower() in i.rule.lower()]
            verdict = "FAIL" if family_issues else "PASS"
            if family_issues and all(i.severity == Severity.WARNING for i in family_issues):
                verdict = "WARNING"
            report.families.append(FamilyResult(
                family=skill_name, verdict=verdict, issues_found=entry.issues_found,
                detection_verified=entry.state == ExecutionState.COMPLETED,
            ))
        return report
