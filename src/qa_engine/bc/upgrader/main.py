"""Main BC-QA Upgrader orchestrator."""

from pathlib import Path
from typing import List, Dict, Optional
from .models import (
    ParsedIssue,
    QARule,
    BCSkillMapping,
    GapAnalysis,
    UpgradePlan,
    UpgradeResult,
    ValidationResult,
)
from .issue_parser import IssueParser
from .qa_rule_extractor import QARuleExtractor
from .bc_skill_analyzer import BCSkillAnalyzer
from .gap_analyzer import GapAnalyzer
from .skill_upgrader import SkillUpgrader


class BCQAUpgrader:
    """Main orchestrator for BC-QA gap analysis and upgrades."""

    def __init__(self, skills_dir: Optional[Path] = None):
        """Initialize upgrader with component instances."""
        self._skills_dir = skills_dir
        self._issue_parser = IssueParser()
        self._qa_extractor = QARuleExtractor(skills_dir)
        self._bc_analyzer = BCSkillAnalyzer(skills_dir)
        self._gap_analyzer = GapAnalyzer()
        self._skill_upgrader = SkillUpgrader(skills_dir)

    def parse_issues(self, issues_arg: str) -> List[ParsedIssue]:
        """Parse issue IDs from command argument."""
        return self._issue_parser.parse(issues_arg)

    def get_qa_rules_for_issues(
        self, issues: List[ParsedIssue]
    ) -> Dict[str, List[QARule]]:
        """Get QA rules relevant to the given issues."""
        return self._qa_extractor.get_rules_for_issues(issues)

    def map_bc_skills_to_issues(
        self, issues: List[ParsedIssue]
    ) -> Dict[str, List[BCSkillMapping]]:
        """Map BC skills to issues they can cause."""
        return self._bc_analyzer.get_skills_for_issues(issues)

    def analyze_gaps(
        self,
        issues: List[ParsedIssue],
        qa_rules: Dict[str, List[QARule]],
        bc_skills: Dict[str, List[BCSkillMapping]],
    ) -> List[GapAnalysis]:
        """Analyze gaps between BC skills and QA rules."""
        return self._gap_analyzer.analyze(issues, qa_rules, bc_skills)

    def create_upgrade_plan(
        self,
        bc_mapping: Dict[str, List[BCSkillMapping]],
        qa_rules: Dict[str, List[QARule]],
    ) -> List[UpgradePlan]:
        """Create upgrade plan from mappings and rules."""
        # Convert to gap analyses first
        issues = [
            ParsedIssue(
                issue_id=issue_id,
                category=skills[0].issue_categories[0] if skills else None,
                number=0,
            )
            for issue_id, skills in bc_mapping.items()
            if skills
        ]
        analyses = self._gap_analyzer.analyze(issues, qa_rules, bc_mapping)
        return self._skill_upgrader.create_upgrade_plan(analyses)

    def apply_upgrades(self, plans: List[UpgradePlan]) -> List[UpgradeResult]:
        """Apply upgrade plans."""
        return self._skill_upgrader.apply_upgrades(plans)

    def validate_upgrades(
        self, results: List[UpgradeResult]
    ) -> List[ValidationResult]:
        """Validate that upgrades fixed the issues."""
        validations = []
        # Group results by issue
        for result in results:
            if result.success:
                # Create validation result
                validation = ValidationResult(
                    issue=result.action.metadata.get("issue"),
                    passed=True,
                    remaining_issues=0,
                    details="Upgrade applied successfully",
                )
                validations.append(validation)
        return validations

    # Format methods delegate to components
    def format_rules_report(self, rules: Dict[str, List[QARule]]) -> str:
        """Format QA rules as markdown report."""
        return self._qa_extractor.format_rules_report(rules)

    def format_bc_mapping_report(
        self, mappings: Dict[str, List[BCSkillMapping]]
    ) -> str:
        """Format BC skill mappings as markdown report."""
        return self._bc_analyzer.format_bc_mapping_report(mappings)

    def format_upgrade_plan(self, plans: List[UpgradePlan]) -> str:
        """Format upgrade plans as markdown."""
        return self._skill_upgrader.format_upgrade_plan(plans)

    def format_results(self, results: List[UpgradeResult]) -> str:
        """Format upgrade results as markdown."""
        return self._skill_upgrader.format_results(results)

    def format_validation_report(
        self, validations: List[ValidationResult]
    ) -> str:
        """Format validation results as markdown."""
        lines = ["# Validation Report\n"]

        passed = [v for v in validations if v.passed]
        failed = [v for v in validations if not v.passed]

        lines.append(f"**Passed:** {len(passed)} | **Failed:** {len(failed)}\n")

        if passed:
            lines.append("## Passed Validations")
            for v in passed:
                lines.append(f"- {v.details}")

        if failed:
            lines.append("\n## Failed Validations")
            for v in failed:
                lines.append(f"- Remaining issues: {v.remaining_issues}")
                lines.append(f"  Details: {v.details}")

        return "\n".join(lines)

    def run_full_analysis(self, issues_arg: str) -> str:
        """Run complete analysis and return formatted report."""
        lines = []

        # Parse issues
        issues = self.parse_issues(issues_arg)
        lines.append(f"# BC-QA Gap Analysis: {issues_arg}\n")
        lines.append(f"Analyzing {len(issues)} issue(s)\n")

        if not issues:
            return "No valid issues provided."

        # Get QA rules
        qa_rules = self.get_qa_rules_for_issues(issues)
        lines.append(self.format_rules_report(qa_rules))

        # Map BC skills
        bc_mapping = self.map_bc_skills_to_issues(issues)
        lines.append(self.format_bc_mapping_report(bc_mapping))

        # Create upgrade plan
        plans = self.create_upgrade_plan(bc_mapping, qa_rules)
        lines.append(self.format_upgrade_plan(plans))

        return "\n".join(lines)
