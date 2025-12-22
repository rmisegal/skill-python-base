"""
Domain models for QA Engine.

Contains core data structures for issues, severity, skills, tools, and resources.
"""

from .issue import Issue, Severity
from .skill import SkillMetadata, SkillLevel as LegacySkillLevel, SkillType as LegacySkillType
from .status import QAStatus, StatusEntry

# New modular architecture models
from .base import BaseEntity
from .definitions import RuleDefinition, PatternDefinition, RuleConfig
from .skill_model import Skill, SkillLevel, SkillType, OrchestratorSkill, DetectorSkill, FixerSkill
from .tool_model import Tool, ToolType, DetectorTool, FixerTool
from .resource_model import Resource, ResourceType, FileFormat, ConfigResource, RulesResource, PatternsResource

__all__ = [
    # Legacy models (for backward compatibility)
    "Issue",
    "Severity",
    "SkillMetadata",
    "QAStatus",
    "StatusEntry",
    # Base classes
    "BaseEntity",
    # Definitions
    "RuleDefinition",
    "PatternDefinition",
    "RuleConfig",
    # Skill hierarchy
    "Skill",
    "SkillLevel",
    "SkillType",
    "OrchestratorSkill",
    "DetectorSkill",
    "FixerSkill",
    # Tool hierarchy
    "Tool",
    "ToolType",
    "DetectorTool",
    "FixerTool",
    # Resource hierarchy
    "Resource",
    "ResourceType",
    "FileFormat",
    "ConfigResource",
    "RulesResource",
    "PatternsResource",
]
