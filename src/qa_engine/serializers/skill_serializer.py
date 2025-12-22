"""
Skill serializer for writing Skill objects to skill.md files.

Generates YAML frontmatter and markdown content.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..domain.models import (
    Skill,
    OrchestratorSkill,
    DetectorSkill,
    FixerSkill,
)


class SkillSerializer:
    """Serializes Skill objects to skill.md files."""

    def serialize(self, skill: Skill) -> str:
        """Serialize a Skill object to markdown with YAML frontmatter."""
        frontmatter = self._generate_frontmatter(skill)
        markdown = self._generate_markdown(skill)
        return f"---\n{frontmatter}---\n\n{markdown}"

    def write(self, skill: Skill, file_path: Optional[Path] = None) -> Path:
        """Write skill to file. Uses skill.path if file_path not provided."""
        path = file_path or skill.path
        if not path:
            raise ValueError("No file path specified for skill")
        content = self.serialize(skill)
        path.write_text(content, encoding="utf-8")
        return path

    def _generate_frontmatter(self, skill: Skill) -> str:
        """Generate YAML frontmatter from skill metadata."""
        data: Dict[str, Any] = {
            "name": skill.name,
            "description": skill.description,
            "version": skill.version,
            "enabled": skill.enabled,
            "level": skill.level.value,
            "skill_type": skill.skill_type.value,
        }

        if skill.family:
            data["family"] = skill.family
        if skill.parent:
            data["parent"] = skill.parent
        if skill.children:
            data["children"] = skill.children
        if skill.tags:
            data["tags"] = skill.tags
        if skill.tools:
            data["tools"] = skill.tools
        if skill.resources:
            data["resources"] = skill.resources
        if skill.rules:
            data["rules"] = {k: v.to_dict() for k, v in skill.rules.items()}
        if skill.auto_fix:
            data["auto_fix"] = skill.auto_fix
        if skill.metadata:
            data["metadata"] = skill.metadata

        # Add subclass-specific fields
        if isinstance(skill, OrchestratorSkill):
            if skill.managed_families:
                data["managed_families"] = skill.managed_families
            data["coordination_mode"] = skill.coordination_mode
        elif isinstance(skill, DetectorSkill):
            if skill.detection_rules:
                data["detection_rules"] = skill.detection_rules
            data["has_python_tool"] = skill.has_python_tool
        elif isinstance(skill, FixerSkill):
            if skill.fix_patterns:
                data["fix_patterns"] = skill.fix_patterns
            data["has_python_tool"] = skill.has_python_tool

        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    def _generate_markdown(self, skill: Skill) -> str:
        """Generate markdown content from skill."""
        sections: List[str] = []

        # Mission statement
        if skill.mission_statement:
            sections.append(f"## Mission\n\n{skill.mission_statement}")

        # System prompt
        if skill.system_prompt:
            sections.append(f"## System Prompt\n\n{skill.system_prompt}")

        # Description section
        if skill.description and skill.description not in skill.mission_statement:
            sections.append(f"## Description\n\n{skill.description}")

        # Tools section
        if skill.tools:
            tools_list = "\n".join(f"- `{tool}`" for tool in skill.tools)
            sections.append(f"## Tools\n\n{tools_list}")

        # Resources section
        if skill.resources:
            resources_list = "\n".join(f"- `{res}`" for res in skill.resources)
            sections.append(f"## Resources\n\n{resources_list}")

        # Rules section for detector skills
        if isinstance(skill, DetectorSkill) and skill.detection_rules:
            rules_list = "\n".join(f"- `{rule}`" for rule in skill.detection_rules)
            sections.append(f"## Detection Rules\n\n{rules_list}")

        # Patterns section for fixer skills
        if isinstance(skill, FixerSkill) and skill.fix_patterns:
            patterns_list = "\n".join(f"- `{pat}`" for pat in skill.fix_patterns)
            sections.append(f"## Fix Patterns\n\n{patterns_list}")

        return "\n\n".join(sections)

    def serialize_minimal(self, skill: Skill) -> str:
        """Serialize skill with minimal frontmatter for embedding."""
        data = {
            "name": skill.name,
            "description": skill.description,
            "level": skill.level.value,
            "skill_type": skill.skill_type.value,
        }
        frontmatter = yaml.dump(data, default_flow_style=False)
        return f"---\n{frontmatter}---\n\n{skill.system_prompt}"
