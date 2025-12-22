"""
Skill metadata model.

Represents metadata for a QA skill parsed from skill.md frontmatter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SkillLevel(Enum):
    """Skill hierarchy levels."""

    L0_SUPER = 0
    L1_FAMILY = 1
    L2_LEAF = 2


class SkillType(Enum):
    """Types of QA skills."""

    ORCHESTRATOR = "orchestrator"
    DETECTION = "detection"
    FIX = "fix"
    VALIDATION = "validation"


@dataclass
class SkillMetadata:
    """
    Skill metadata parsed from skill.md frontmatter.

    Attributes:
        name: Skill identifier (e.g., 'qa-BiDi-detect')
        description: Brief skill description
        version: Semantic version string
        level: Skill hierarchy level
        skill_type: Type of skill
        family: Parent family name (e.g., 'BiDi')
        parent: Parent skill name
        children: Child skill names
        has_python_tool: Whether skill has tool.py
        path: Path to skill directory
        tags: Metadata tags
    """

    name: str
    description: str
    version: str
    level: SkillLevel
    skill_type: SkillType
    family: Optional[str] = None
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    has_python_tool: bool = False
    path: Optional[Path] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "level": self.level.value,
            "skill_type": self.skill_type.value,
            "family": self.family,
            "parent": self.parent,
            "children": self.children,
            "has_python_tool": self.has_python_tool,
            "path": str(self.path) if self.path else None,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillMetadata:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            version=data["version"],
            level=SkillLevel(data["level"]),
            skill_type=SkillType(data["skill_type"]),
            family=data.get("family"),
            parent=data.get("parent"),
            children=data.get("children", []),
            has_python_tool=data.get("has_python_tool", False),
            path=Path(data["path"]) if data.get("path") else None,
            tags=data.get("tags", []),
        )

    def is_detector(self) -> bool:
        """Check if skill is a detector."""
        return self.skill_type == SkillType.DETECTION

    def is_fixer(self) -> bool:
        """Check if skill is a fixer."""
        return self.skill_type == SkillType.FIX
