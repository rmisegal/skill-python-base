"""QA rule extractor for BC-QA upgrader."""

import json
from pathlib import Path
from typing import List, Dict, Any
from .models import ParsedIssue, QARule, IssueCategory, Severity


class QARuleExtractor:
    """Extract QA rules from skill definitions."""

    CATEGORY_TO_QA_FAMILY: Dict[IssueCategory, str] = {
        IssueCategory.BIDI: "qa-BiDi",
        IssueCategory.CODE: "qa-code",
        IssueCategory.TABLE: "qa-table",
        IssueCategory.BIB: "qa-bib",
        IssueCategory.IMG: "qa-img",
        IssueCategory.TYPE: "qa-typeset",
    }

    def __init__(self, skills_dir: Path | None = None):
        """Initialize with skills directory."""
        self._skills_dir = skills_dir or self._find_skills_dir()
        self._rules_cache: Dict[str, List[QARule]] = {}

    def _find_skills_dir(self) -> Path:
        """Find the .claude/skills directory."""
        candidates = [
            Path(".claude/skills"),
            Path(__file__).parent.parent.parent.parent.parent.parent
            / ".claude/skills",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return Path(".claude/skills")

    def get_rules_for_issues(
        self, issues: List[ParsedIssue]
    ) -> Dict[str, List[QARule]]:
        """Get QA rules relevant to the given issues."""
        result: Dict[str, List[QARule]] = {}

        for issue in issues:
            qa_family = self.CATEGORY_TO_QA_FAMILY.get(issue.category)
            if not qa_family:
                continue

            rules = self._load_family_rules(qa_family)
            result[issue.issue_id] = rules

        return result

    def _load_family_rules(self, qa_family: str) -> List[QARule]:
        """Load rules from a QA family's detect skill."""
        if qa_family in self._rules_cache:
            return self._rules_cache[qa_family]

        rules = []
        detect_skill = self._skills_dir / f"{qa_family}-detect" / "skill.md"

        if detect_skill.exists():
            rules = self._parse_skill_rules(detect_skill, qa_family)

        self._rules_cache[qa_family] = rules
        return rules

    def _parse_skill_rules(self, skill_path: Path, family: str) -> List[QARule]:
        """Parse rules from skill.md file."""
        rules = []
        content = skill_path.read_text(encoding="utf-8")
        import re

        # Method 1: Extract rules from ### Rule: sections
        rule_pattern = r"### Rule: (\w+[-\w]*)"
        for match in re.finditer(rule_pattern, content):
            rule_id = match.group(1)
            rules.append(
                QARule(
                    rule_id=rule_id,
                    family=family,
                    description=self._extract_rule_desc(content, rule_id),
                    pattern=self._extract_pattern(content, rule_id),
                    fix_pattern=self._extract_fix(content, rule_id),
                    severity=Severity.WARNING,
                    auto_fixable=True,
                )
            )

        # Method 2: Extract rules from markdown tables
        # Pattern: | `rule-id` | Description | SEVERITY |
        table_pattern = r"\|\s*`([a-z]+-[a-z-]+)`\s*\|\s*([^|]+)\|\s*(\w+)\s*\|"
        for match in re.finditer(table_pattern, content):
            rule_id = match.group(1)
            description = match.group(2).strip()
            severity_str = match.group(3).strip().upper()
            severity = Severity.WARNING
            if severity_str == "CRITICAL":
                severity = Severity.CRITICAL
            elif severity_str == "INFO":
                severity = Severity.INFO

            # Avoid duplicates
            if not any(r.rule_id == rule_id for r in rules):
                rules.append(
                    QARule(
                        rule_id=rule_id,
                        family=family,
                        description=description,
                        pattern="",
                        fix_pattern="",
                        severity=severity,
                        auto_fixable=True,
                    )
                )

        return rules

    def _extract_rule_desc(self, content: str, rule_id: str) -> str:
        """Extract rule description from content."""
        import re

        pattern = rf"### Rule: {rule_id}\s*\n([^\n#]+)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    def _extract_pattern(self, content: str, rule_id: str) -> str:
        """Extract BAD pattern example from content."""
        import re

        pattern = rf"### Rule: {rule_id}.*?\*\*BAD:\*\*\s*```latex\s*(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_fix(self, content: str, rule_id: str) -> str:
        """Extract GOOD pattern example from content."""
        import re

        pattern = rf"### Rule: {rule_id}.*?\*\*GOOD:\*\*\s*```latex\s*(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def format_rules_report(
        self, rules: Dict[str, List[QARule]]
    ) -> str:
        """Format rules as markdown report."""
        lines = ["# QA Rules Relevant to Issues\n"]

        for issue_id, issue_rules in rules.items():
            lines.append(f"## {issue_id}\n")
            if not issue_rules:
                lines.append("No rules found.\n")
                continue

            lines.append("| Rule | Family | Description |")
            lines.append("|------|--------|-------------|")
            for rule in issue_rules:
                lines.append(
                    f"| {rule.rule_id} | {rule.family} | {rule.description} |"
                )
            lines.append("")

        return "\n".join(lines)
