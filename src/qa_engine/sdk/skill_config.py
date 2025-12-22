"""
Skill configuration dataclasses.

Configuration and result types for skill creation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SkillConfig:
    """Configuration for a new skill."""

    name: str
    family: str
    level: int
    skill_type: str
    description: str
    rules: List[str] = field(default_factory=list)
    generate_python: bool = False


@dataclass
class CreationResult:
    """Result of skill creation."""

    success: bool
    created_files: List[str] = field(default_factory=list)
    updated_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
