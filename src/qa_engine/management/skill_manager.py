"""
Skill manager for managing QA skills.

Provides CRUD operations and hierarchy management for skills.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.models import (
    Skill,
    SkillLevel,
    SkillType,
    RuleConfig,
)
from ..parsers.skill_parser import SkillParser
from ..serializers.skill_serializer import SkillSerializer
from .base_manager import BaseManager


class SkillManager(BaseManager[Skill]):
    """Manages QA skills with full CRUD and hierarchy support."""

    def __init__(self, storage_path: Path):
        """Initialize skill manager."""
        super().__init__(storage_path)
        self._parser = SkillParser()
        self._serializer = SkillSerializer()

    # Hierarchy Operations

    def get_children(self, skill_id: str) -> List[Skill]:
        """Get all child skills of a skill."""
        skill = self.read(skill_id)
        if not skill or not skill.children:
            return []
        return [s for s in self.list_all() if s.id in skill.children]

    def get_parent(self, skill_id: str) -> Optional[Skill]:
        """Get parent skill of a skill."""
        skill = self.read(skill_id)
        if not skill or not skill.parent:
            return None
        return self.read(skill.parent)

    def get_family(self, family_name: str) -> List[Skill]:
        """Get all skills in a family."""
        return self.find(family=family_name)

    def get_by_level(self, level: SkillLevel) -> List[Skill]:
        """Get all skills at a specific level."""
        return self.find(level=level)

    def get_by_type(self, skill_type: SkillType) -> List[Skill]:
        """Get all skills of a specific type."""
        return self.find(skill_type=skill_type)

    # Configuration

    def get_system_prompt(self, skill_id: str) -> str:
        """Get skill's system prompt."""
        skill = self.read(skill_id)
        return skill.system_prompt if skill else ""

    def set_system_prompt(self, skill_id: str, prompt: str) -> None:
        """Set skill's system prompt."""
        self.update(skill_id, {"system_prompt": prompt})

    def get_rules(self, skill_id: str) -> Dict[str, RuleConfig]:
        """Get skill's rule configurations."""
        skill = self.read(skill_id)
        return skill.rules if skill else {}

    def set_rule(self, skill_id: str, rule_id: str, config: RuleConfig) -> None:
        """Set a rule configuration for a skill."""
        skill = self.read(skill_id)
        if skill:
            skill.rules[rule_id] = config
            self._persist(skill)

    # Tool/Resource Relations

    def add_tool(self, skill_id: str, tool_id: str) -> None:
        """Add a tool to a skill."""
        skill = self.read(skill_id)
        if skill and tool_id not in skill.tools:
            skill.tools.append(tool_id)
            self._persist(skill)

    def remove_tool(self, skill_id: str, tool_id: str) -> None:
        """Remove a tool from a skill."""
        skill = self.read(skill_id)
        if skill and tool_id in skill.tools:
            skill.tools.remove(tool_id)
            self._persist(skill)

    def add_resource(self, skill_id: str, resource_id: str) -> None:
        """Add a resource to a skill."""
        skill = self.read(skill_id)
        if skill and resource_id not in skill.resources:
            skill.resources.append(resource_id)
            self._persist(skill)

    def remove_resource(self, skill_id: str, resource_id: str) -> None:
        """Remove a resource from a skill."""
        skill = self.read(skill_id)
        if skill and resource_id in skill.resources:
            skill.resources.remove(resource_id)
            self._persist(skill)

    # Implementation of abstract methods

    def _load_from_storage(self) -> List[Skill]:
        """Load all skills from storage."""
        skills: List[Skill] = []
        if not self._storage_path.exists():
            return skills

        for skill_dir in self._storage_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "skill.md"
                if skill_file.exists():
                    skills.append(self._parser.parse(skill_file))
        return skills

    def _load_single(self, entity_id: str) -> Optional[Skill]:
        """Load a single skill from storage."""
        skill_file = self._storage_path / entity_id / "skill.md"
        if skill_file.exists():
            return self._parser.parse(skill_file)
        return None

    def _persist(self, entity: Skill) -> None:
        """Persist skill to storage."""
        skill_dir = self._storage_path / entity.id
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "skill.md"
        self._serializer.write(entity, skill_file)

    def _remove_persisted(self, entity: Skill) -> None:
        """Remove skill directory from storage."""
        skill_dir = self._storage_path / entity.id
        if skill_dir.exists():
            shutil.rmtree(skill_dir)

    def _from_dict(self, data: Dict[str, Any]) -> Skill:
        """Create skill from dictionary."""
        return Skill.from_dict(data)
