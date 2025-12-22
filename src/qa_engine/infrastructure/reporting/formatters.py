"""
Report formatters for different output formats.

Handles JSON, Markdown, and Summary formatting.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...domain.models.issue import Issue, Severity
from ...domain.models.status import QAStatus


def format_json(
    issues: List[Issue],
    status: Optional[QAStatus],
    by_severity: Dict[str, int],
    by_rule: Dict[str, int],
) -> str:
    """Generate JSON report."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_issues": len(issues),
        "by_severity": by_severity,
        "by_rule": by_rule,
        "issues": [issue_to_dict(i) for i in issues],
    }

    if status:
        report["run_id"] = status.run_id
        report["project"] = status.project_path

    return json.dumps(report, indent=2, ensure_ascii=False)


def format_markdown(
    issues: List[Issue],
    status: Optional[QAStatus],
    by_severity: Dict[str, int],
    by_file: Dict[str, List[Issue]],
) -> str:
    """Generate Markdown report."""
    lines = ["# QA Report\n"]

    if status:
        lines.append(f"**Run ID:** {status.run_id}")
        lines.append(f"**Project:** {status.project_path}\n")

    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Total Issues:** {len(issues)}\n")

    lines.append("## Summary by Severity\n")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev, count in by_severity.items():
        lines.append(f"| {sev} | {count} |")
    lines.append("")

    lines.append("## Issues by File\n")
    for file_path, file_issues in by_file.items():
        lines.append(f"### {Path(file_path).name}\n")
        for issue in file_issues:
            icon = severity_icon(issue.severity)
            lines.append(f"- {icon} **Line {issue.line}** [{issue.rule}]")
            lines.append(f"  - {issue.content[:80]}")
            if issue.fix:
                lines.append(f"  - Fix: {issue.fix}")
        lines.append("")

    return "\n".join(lines)


def format_summary(
    issues: List[Issue],
    status: Optional[QAStatus],
    by_severity: Dict[str, int],
    by_rule: Dict[str, int],
) -> str:
    """Generate brief summary report."""
    lines = ["QA Summary"]
    lines.append("=" * 40)

    if status:
        lines.append(f"Run: {status.run_id}")

    lines.append(f"Total: {len(issues)} issues")

    for sev, count in by_severity.items():
        lines.append(f"  {sev}: {count}")

    lines.append("\nTop Rules:")
    for rule, count in sorted(by_rule.items(), key=lambda x: -x[1])[:5]:
        lines.append(f"  {rule}: {count}")

    return "\n".join(lines)


def issue_to_dict(issue: Issue) -> Dict[str, Any]:
    """Convert issue to dictionary."""
    return {
        "rule": issue.rule,
        "file": issue.file,
        "line": issue.line,
        "content": issue.content,
        "severity": issue.severity.value,
        "fix": issue.fix,
    }


def severity_icon(severity: Severity) -> str:
    """Get icon for severity level."""
    icons = {
        Severity.CRITICAL: "🔴",
        Severity.WARNING: "🟡",
        Severity.INFO: "🔵",
    }
    return icons.get(severity, "⚪")
