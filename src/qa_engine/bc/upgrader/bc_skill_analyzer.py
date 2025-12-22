"""BC skill analyzer for BC-QA upgrader."""

from pathlib import Path
from typing import List, Dict
from .models import ParsedIssue, BCSkillMapping, IssueCategory


class BCSkillAnalyzer:
    """Analyze BC skills and map them to issue categories."""

    # Mapping of issue categories to BC skills that can cause them
    CATEGORY_TO_BC_SKILLS: Dict[IssueCategory, List[str]] = {
        IssueCategory.BIDI: ["bc-content", "bc-math", "bc-code", "bc-hebrew"],
        IssueCategory.CODE: ["bc-code"],
        IssueCategory.TABLE: ["bc-academic-source"],
        IssueCategory.BIB: ["bc-source-research", "bc-academic-source"],
        IssueCategory.IMG: ["bc-content"],
        IssueCategory.TYPE: [
            "bc-content",
            "bc-code",
            "bc-math",
            "bc-academic-source",
        ],
    }

    # Content types each BC skill generates
    SKILL_CONTENT_TYPES: Dict[str, List[str]] = {
        "bc-code": ["pythonbox", "tikzpicture", "tcolorbox"],
        "bc-math": ["equation", "align", "math", "hebmath"],
        "bc-academic-source": ["table", "tabular", "rtltabular", "cite"],
        "bc-content": ["figure", "section", "text"],
        "bc-hebrew": ["hebrew", "english", "he", "en"],
        "bc-source-research": ["bibliography", "bibentry"],
    }

    # Validators used by each BC skill
    SKILL_VALIDATORS: Dict[str, List[str]] = {
        "bc-code": ["BCBiDiValidator", "BCCodeValidator"],
        "bc-math": ["BCBiDiValidator"],
        "bc-academic-source": [
            "BCBiDiValidator",
            "BCTableValidator",
            "BCBibValidator",
        ],
        "bc-content": ["BCBiDiValidator", "BCImageValidator"],
        "bc-hebrew": ["BCBiDiValidator"],
        "bc-source-research": ["BCBibValidator"],
    }

    def __init__(self, skills_dir: Path | None = None):
        """Initialize with skills directory."""
        self._skills_dir = skills_dir or self._find_skills_dir()

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

    def get_skills_for_issues(
        self, issues: List[ParsedIssue]
    ) -> Dict[str, List[BCSkillMapping]]:
        """Get BC skills that can cause the given issues."""
        result: Dict[str, List[BCSkillMapping]] = {}

        for issue in issues:
            skill_names = self.CATEGORY_TO_BC_SKILLS.get(issue.category, [])
            mappings = []

            for skill_name in skill_names:
                skill_path = self._skills_dir / skill_name / "skill.md"
                mapping = BCSkillMapping(
                    skill_name=skill_name,
                    skill_path=str(skill_path),
                    issue_categories=[issue.category],
                    content_types=self.SKILL_CONTENT_TYPES.get(skill_name, []),
                    validators=self.SKILL_VALIDATORS.get(skill_name, []),
                )
                mappings.append(mapping)

            result[issue.issue_id] = mappings

        return result

    def get_skill_details(self, skill_name: str) -> Dict:
        """Get detailed information about a BC skill."""
        skill_path = self._skills_dir / skill_name / "skill.md"
        if not skill_path.exists():
            return {"error": f"Skill not found: {skill_name}"}

        content = skill_path.read_text(encoding="utf-8")
        return {
            "name": skill_name,
            "path": str(skill_path),
            "content_types": self.SKILL_CONTENT_TYPES.get(skill_name, []),
            "validators": self.SKILL_VALIDATORS.get(skill_name, []),
            "has_validation_rules": "Validation" in content,
        }

    def format_bc_mapping_report(
        self, mappings: Dict[str, List[BCSkillMapping]]
    ) -> str:
        """Format BC skill mappings as markdown report."""
        lines = ["# BC Skills Responsible for Issues\n"]

        for issue_id, skills in mappings.items():
            lines.append(f"## {issue_id}\n")
            if not skills:
                lines.append("No BC skills found.\n")
                continue

            lines.append("| Skill | Content Types | Validators |")
            lines.append("|-------|---------------|------------|")
            for skill in skills:
                content = ", ".join(skill.content_types[:3])
                validators = ", ".join(skill.validators)
                lines.append(f"| {skill.skill_name} | {content} | {validators} |")
            lines.append("")

        return "\n".join(lines)
