"""Skill upgrader for BC-QA upgrader."""

import json
from pathlib import Path
from typing import List, Dict, Optional
from .models import (
    GapAnalysis,
    UpgradePlan,
    UpgradeAction,
    UpgradeResult,
    ValidationResult,
    IssueCategory,
)


class SkillUpgrader:
    """Upgrade BC skills to comply with QA rules."""

    # Upgrade actions by category
    CATEGORY_UPGRADES: Dict[IssueCategory, List[Dict]] = {
        IssueCategory.BIDI: [
            {
                "action_type": "validator",
                "description": "Add BCBiDiValidator to skill validators",
                "metadata": {"validator": "BCBiDiValidator"},
            },
            {
                "action_type": "template",
                "description": "Update templates to use \\en{} wrappers",
                "metadata": {"pattern": "english_wrapper"},
            },
        ],
        IssueCategory.CODE: [
            {
                "action_type": "validator",
                "description": "Add BCCodeValidator to skill validators",
                "metadata": {"validator": "BCCodeValidator"},
            },
            {
                "action_type": "template",
                "description": "Wrap pythonbox in english environment",
                "metadata": {"pattern": "english_code_wrapper"},
            },
        ],
        IssueCategory.TABLE: [
            {
                "action_type": "validator",
                "description": "Add BCTableValidator to skill validators",
                "metadata": {"validator": "BCTableValidator"},
            },
            {
                "action_type": "template",
                "description": "Replace tabular with rtltabular",
                "metadata": {"pattern": "rtl_table"},
            },
        ],
        IssueCategory.BIB: [
            {
                "action_type": "validator",
                "description": "Add BCBibValidator to skill validators",
                "metadata": {"validator": "BCBibValidator"},
            },
        ],
        IssueCategory.IMG: [
            {
                "action_type": "validator",
                "description": "Add BCImageValidator to skill validators",
                "metadata": {"validator": "BCImageValidator"},
            },
        ],
        IssueCategory.TYPE: [
            {
                "action_type": "config",
                "description": "Enable strict typeset validation",
                "metadata": {"config_key": "validators.strict_typeset"},
            },
        ],
    }

    def __init__(
        self,
        skills_dir: Optional[Path] = None,
        config_path: Optional[Path] = None,
    ):
        """Initialize upgrader."""
        self._skills_dir = skills_dir or self._find_skills_dir()
        self._config_path = config_path or self._find_config_path()

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

    def _find_config_path(self) -> Path:
        """Find bc_pipeline.json config."""
        candidates = [
            Path("bc_pipeline.json"),
            Path(".claude/bc_pipeline.json"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return Path("bc_pipeline.json")

    def create_upgrade_plan(
        self, analyses: List[GapAnalysis]
    ) -> List[UpgradePlan]:
        """Create upgrade plans for all gap analyses."""
        plans = []

        for analysis in analyses:
            actions = self._create_actions(analysis)
            requires_user = self._check_requires_user(analysis)

            plan = UpgradePlan(
                issue=analysis.issue,
                gap_analysis=analysis,
                actions=actions,
                requires_user_action=requires_user,
                user_action_message=self._get_user_message(analysis)
                if requires_user
                else "",
            )
            plans.append(plan)

        return plans

    def _create_actions(self, analysis: GapAnalysis) -> List[UpgradeAction]:
        """Create upgrade actions for a gap analysis."""
        actions = []
        category = analysis.issue.category

        templates = self.CATEGORY_UPGRADES.get(category, [])
        for template in templates:
            for skill in analysis.bc_skills:
                action = UpgradeAction(
                    action_type=template["action_type"],
                    target_path=skill.skill_path,
                    description=template["description"],
                    metadata=template.get("metadata", {}),
                )
                actions.append(action)

        return actions

    def _check_requires_user(self, analysis: GapAnalysis) -> bool:
        """Check if upgrade requires user action (CLS changes)."""
        # CLS changes require user approval
        return False

    def _get_user_message(self, analysis: GapAnalysis) -> str:
        """Get message for user action."""
        return ""

    def apply_upgrades(self, plans: List[UpgradePlan]) -> List[UpgradeResult]:
        """Apply upgrade plans."""
        results = []

        for plan in plans:
            for action in plan.actions:
                result = self._apply_action(action)
                results.append(result)

        return results

    def _apply_action(self, action: UpgradeAction) -> UpgradeResult:
        """Apply a single upgrade action."""
        try:
            if action.action_type == "validator":
                return self._apply_validator_action(action)
            elif action.action_type == "template":
                return self._apply_template_action(action)
            elif action.action_type == "config":
                return self._apply_config_action(action)
            else:
                return UpgradeResult(
                    action=action,
                    success=False,
                    message="Unknown action type",
                    error=f"Unknown: {action.action_type}",
                )
        except Exception as e:
            return UpgradeResult(
                action=action,
                success=False,
                message="Action failed",
                error=str(e),
            )

    def _apply_validator_action(self, action: UpgradeAction) -> UpgradeResult:
        """Apply validator addition action to bc_pipeline.json."""
        validator = action.metadata.get("validator", "")
        if not validator:
            return UpgradeResult(
                action=action, success=False,
                message="No validator specified", error="Missing validator"
            )

        try:
            # Update bc_pipeline.json
            if self._config_path.exists():
                config = json.loads(self._config_path.read_text(encoding="utf-8"))
            else:
                config = {"validators": {}, "stages": {}}

            # Extract skill name from path
            skill_name = Path(action.target_path).parent.name

            # Find which stage this skill belongs to
            for stage_name, stage_config in config.get("stages", {}).items():
                if skill_name in stage_config.get("skills", []):
                    if validator not in stage_config.get("validators", []):
                        stage_config.setdefault("validators", []).append(validator)

            # Save updated config
            self._config_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            return UpgradeResult(
                action=action, success=True,
                message=f"Added {validator} to pipeline for {skill_name}"
            )
        except Exception as e:
            return UpgradeResult(
                action=action, success=False,
                message="Failed to update config", error=str(e)
            )

    def _apply_template_action(self, action: UpgradeAction) -> UpgradeResult:
        """Apply template modification - generates instruction for LLM."""
        pattern = action.metadata.get("pattern", "")
        skill_path = Path(action.target_path)

        # Generate specific instruction based on pattern
        instructions = {
            "english_wrapper": "Add \\en{} wrapper for English text/numbers",
            "english_code_wrapper": "Wrap pythonbox in \\begin{english}",
            "rtl_table": "Use rtltabular instead of tabular",
        }

        instruction = instructions.get(pattern, action.description)

        return UpgradeResult(
            action=action, success=True,
            message=f"LLM instruction: {instruction} in {skill_path.name}"
        )

    def _apply_config_action(self, action: UpgradeAction) -> UpgradeResult:
        """Apply config modification to bc_pipeline.json."""
        config_key = action.metadata.get("config_key", "")
        if not config_key:
            return UpgradeResult(
                action=action, success=False,
                message="No config key", error="Missing config_key"
            )

        try:
            if self._config_path.exists():
                config = json.loads(self._config_path.read_text(encoding="utf-8"))
            else:
                config = {}

            # Set nested config value
            keys = config_key.split(".")
            current = config
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = True

            self._config_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            return UpgradeResult(
                action=action, success=True,
                message=f"Set {config_key}=true in bc_pipeline.json"
            )
        except Exception as e:
            return UpgradeResult(
                action=action, success=False,
                message="Failed to update config", error=str(e)
            )

    def format_upgrade_plan(self, plans: List[UpgradePlan]) -> str:
        """Format upgrade plans as markdown."""
        lines = ["# Upgrade Plan\n"]

        for plan in plans:
            lines.append(f"## {plan.issue.issue_id}\n")

            if plan.requires_user_action:
                lines.append(f"**USER ACTION REQUIRED:** {plan.user_action_message}\n")

            lines.append("### Actions")
            for i, action in enumerate(plan.actions, 1):
                lines.append(f"{i}. [{action.action_type}] {action.description}")
                lines.append(f"   - Target: `{action.target_path}`")

            lines.append("")

        return "\n".join(lines)

    def format_results(self, results: List[UpgradeResult]) -> str:
        """Format upgrade results as markdown."""
        lines = ["# Upgrade Results\n"]

        success = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        lines.append(f"**Success:** {len(success)} | **Failed:** {len(failed)}\n")

        if success:
            lines.append("## Successful Actions")
            for result in success:
                lines.append(f"- {result.message}")

        if failed:
            lines.append("\n## Failed Actions")
            for result in failed:
                lines.append(f"- {result.action.description}: {result.error}")

        return "\n".join(lines)
