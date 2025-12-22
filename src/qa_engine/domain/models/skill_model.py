"""
Skill class hierarchy for QA system.

Defines the three-level skill structure:
- L0: Meta-skills (insert_qa_skill)
- L1: Family orchestrators (qa-BiDi, qa-code)
- L2: Worker skills (qa-BiDi-detect, qa-BiDi-fix-text)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseEntity
from .definitions import RuleConfig


class SkillLevel(Enum):
    """Skill hierarchy levels."""

    L0_META = 0       # Meta-skills (insert_qa_skill)
    L1_FAMILY = 1     # Family orchestrators (qa-BiDi)
    L2_WORKER = 2     # Worker skills (qa-BiDi-detect)


class SkillType(Enum):
    """Types of skills based on function."""

    ORCHESTRATOR = "orchestrator"
    DETECTION = "detection"
    FIX = "fix"
    VALIDATION = "validation"


@dataclass
class Skill(BaseEntity):
    """
    Base skill class.

    Attributes:
        level: Skill hierarchy level (0, 1, or 2)
        skill_type: Type of skill (orchestrator, detection, fix, validation)
        family: Parent family name (e.g., 'BiDi', 'code')
        parent: Parent skill ID
        children: List of child skill IDs
        tags: Classification tags
        system_prompt: Full markdown content from skill.md
        mission_statement: Brief mission description
        tools: List of tool IDs used by this skill
        resources: List of resource IDs used
        rules: Rule configurations for this skill
        auto_fix: Global auto-fix setting for this skill
    """

    level: SkillLevel = SkillLevel.L2_WORKER
    skill_type: SkillType = SkillType.DETECTION
    family: Optional[str] = None
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    system_prompt: str = ""
    mission_statement: str = ""
    tools: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    rules: Dict[str, RuleConfig] = field(default_factory=dict)
    auto_fix: bool = False

    def validate(self) -> List[str]:
        """Validate skill configuration."""
        errors = self._base_validate()
        if not self.id.startswith("qa-"):
            errors.append("Skill ID must start with 'qa-'")
        if self.level == SkillLevel.L2_WORKER and not self.family:
            errors.append("Worker skills must have a family")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "level": self.level.value,
            "skill_type": self.skill_type.value,
            "family": self.family,
            "parent": self.parent,
            "children": self.children,
            "tags": self.tags,
            "system_prompt": self.system_prompt,
            "mission_statement": self.mission_statement,
            "tools": self.tools,
            "resources": self.resources,
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
            "auto_fix": self.auto_fix,
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """Create from dictionary."""
        rules = {}
        for rule_id, config in data.get("rules", {}).items():
            rules[rule_id] = RuleConfig.from_dict(rule_id, config)
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {}),
            path=Path(data["path"]) if data.get("path") else None,
            level=SkillLevel(data.get("level", 2)),
            skill_type=SkillType(data.get("skill_type", "detection")),
            family=data.get("family"),
            parent=data.get("parent"),
            children=data.get("children", []),
            tags=data.get("tags", []),
            system_prompt=data.get("system_prompt", ""),
            mission_statement=data.get("mission_statement", ""),
            tools=data.get("tools", []),
            resources=data.get("resources", []),
            rules=rules,
            auto_fix=data.get("auto_fix", False),
        )


@dataclass
class OrchestratorSkill(Skill):
    """Level 0-1 orchestrator skills."""

    managed_families: List[str] = field(default_factory=list)
    coordination_mode: str = "parallel"  # or "sequential"

    def __post_init__(self) -> None:
        super().__post_init__()
        self.skill_type = SkillType.ORCHESTRATOR


@dataclass
class DetectorSkill(Skill):
    """Level 2 detection skills."""

    detection_rules: List[str] = field(default_factory=list)
    has_python_tool: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        self.skill_type = SkillType.DETECTION


@dataclass
class FixerSkill(Skill):
    """Level 2 fix skills."""

    fix_patterns: List[str] = field(default_factory=list)
    has_python_tool: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        self.skill_type = SkillType.FIX
