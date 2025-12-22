"""
Skill creator for insert_qa_skill meta-skill.

Automates creation and integration of new QA skills.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from .skill_config import SkillConfig, CreationResult
from .skill_templates import generate_skill_md, generate_tool_py


class SkillCreator:
    """Creates new QA skills from configuration."""

    def __init__(self, skills_root: Path) -> None:
        self._skills_root = skills_root

    def create_skill(self, config: SkillConfig) -> CreationResult:
        """Create a new skill from configuration."""
        result = CreationResult(success=True)

        # Validate config
        errors = self._validate_config(config)
        if errors:
            result.success = False
            result.errors = errors
            return result

        # Create skill directory
        skill_dir = self._skills_root / config.name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Generate skill.md
        skill_md = generate_skill_md(config)
        skill_path = skill_dir / "skill.md"
        skill_path.write_text(skill_md, encoding="utf-8")
        result.created_files.append(str(skill_path))

        # Generate tool.py if requested
        if config.generate_python and config.level == 2:
            tool_py = generate_tool_py(config)
            tool_path = skill_dir / "tool.py"
            tool_path.write_text(tool_py, encoding="utf-8")
            result.created_files.append(str(tool_path))

        return result

    def _validate_config(self, config: SkillConfig) -> List[str]:
        """Validate skill configuration."""
        errors = []

        if not config.name.startswith("qa-"):
            errors.append("Skill name must start with 'qa-'")

        if config.level not in (1, 2):
            errors.append("Level must be 1 or 2")

        if config.skill_type not in ("detection", "fix", "orchestrator"):
            errors.append("Type must be: detection, fix, or orchestrator")

        if not config.family:
            errors.append("Family is required")

        return errors
