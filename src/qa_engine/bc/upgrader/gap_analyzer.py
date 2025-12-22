"""Gap analyzer for BC-QA upgrader."""

from typing import List, Dict
from .models import (
    ParsedIssue,
    QARule,
    BCSkillMapping,
    GapAnalysis,
    IssueCategory,
)


class GapAnalyzer:
    """Analyze gaps between BC skills and QA rules."""

    # Root cause templates by category
    ROOT_CAUSE_TEMPLATES: Dict[IssueCategory, str] = {
        IssueCategory.BIDI: (
            "BC skill generates content without proper LTR/RTL wrappers. "
            "Hebrew context requires explicit \\en{{}} for English/numbers."
        ),
        IssueCategory.CODE: (
            "BC skill generates code blocks without english environment wrapper. "
            "pythonbox/tikzpicture in RTL context causes background overflow."
        ),
        IssueCategory.TABLE: (
            "BC skill generates tables using tabular instead of rtltabular. "
            "Missing Hebrew table styling (hebrewtable, row colors)."
        ),
        IssueCategory.BIB: (
            "BC skill generates citations without proper english wrappers. "
            "BibTeX entries missing required fields or using wrong format."
        ),
        IssueCategory.IMG: (
            "BC skill generates figure environments with incorrect paths "
            "or missing alt text for accessibility."
        ),
        IssueCategory.TYPE: (
            "BC skill generates content causing LaTeX warnings. "
            "Overfull/underfull boxes, float positioning issues."
        ),
    }

    IMPACT_TEMPLATES: Dict[IssueCategory, str] = {
        IssueCategory.BIDI: "Text renders incorrectly (reversed or misaligned)",
        IssueCategory.CODE: "Code background overflows page margins",
        IssueCategory.TABLE: "Table columns appear in wrong order",
        IssueCategory.BIB: "Citations display incorrectly or missing",
        IssueCategory.IMG: "Images not found or incorrectly placed",
        IssueCategory.TYPE: "Layout warnings, potential page break issues",
    }

    def analyze(
        self,
        issues: List[ParsedIssue],
        qa_rules: Dict[str, List[QARule]],
        bc_skills: Dict[str, List[BCSkillMapping]],
    ) -> List[GapAnalysis]:
        """Analyze gaps for all issues."""
        analyses = []

        for issue in issues:
            rules = qa_rules.get(issue.issue_id, [])
            skills = bc_skills.get(issue.issue_id, [])

            analysis = GapAnalysis(
                issue=issue,
                qa_rules=rules,
                bc_skills=skills,
                root_cause=self.ROOT_CAUSE_TEMPLATES.get(
                    issue.category, "Unknown root cause"
                ),
                impact=self.IMPACT_TEMPLATES.get(
                    issue.category, "Unknown impact"
                ),
            )
            analyses.append(analysis)

        return analyses

    def format_gap_report(self, analyses: List[GapAnalysis]) -> str:
        """Format gap analysis as markdown report."""
        lines = ["# Gap Analysis Report\n"]

        for analysis in analyses:
            lines.append(f"## {analysis.issue.issue_id}\n")
            lines.append(f"**Category:** {analysis.issue.category.value}\n")
            lines.append(f"**Root Cause:** {analysis.root_cause}\n")
            lines.append(f"**Impact:** {analysis.impact}\n")

            lines.append("\n### Affected QA Rules")
            if analysis.qa_rules:
                for rule in analysis.qa_rules:
                    lines.append(f"- `{rule.rule_id}`: {rule.description}")
            else:
                lines.append("- None identified")

            lines.append("\n### Affected BC Skills")
            if analysis.bc_skills:
                for skill in analysis.bc_skills:
                    lines.append(f"- `{skill.skill_name}`")
            else:
                lines.append("- None identified")

            lines.append("")

        return "\n".join(lines)
