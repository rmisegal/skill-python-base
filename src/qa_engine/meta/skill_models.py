"""
Data models for skill analysis.

Contains dataclasses used by SkillAnalyzer and other meta components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class DetectionRule:
    """Represents a detection rule from skill.md."""
    name: str
    description: str
    pattern: str = ""
    regex: str = ""
    severity: str = "WARNING"


@dataclass
class SkillAnalysis:
    """Result of analyzing a skill.md file."""
    skill_id: str
    name: str
    description: str
    version: str
    level: int
    skill_type: str
    parent: str
    family: str
    tags: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    rules: List[DetectionRule] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    has_python_tool: bool = False
