"""
QA Engine Public API.

Provides convenient access to all public classes and managers.

Usage:
    from qa_engine.api import SkillManager, ToolManager

    skill_mgr = SkillManager(Path(".claude/skills"))
    skills = skill_mgr.list_all()
"""

from pathlib import Path

# Domain models
from .domain.models import (
    # Base
    BaseEntity,
    # Definitions
    RuleDefinition,
    PatternDefinition,
    RuleConfig,
    # Skills
    Skill,
    SkillLevel,
    SkillType,
    OrchestratorSkill,
    DetectorSkill,
    FixerSkill,
    # Tools
    Tool,
    ToolType,
    DetectorTool,
    FixerTool,
    # Resources
    Resource,
    ResourceType,
    FileFormat,
    ConfigResource,
    RulesResource,
    PatternsResource,
    # Legacy
    Issue,
    Severity,
)

# Managers
from .management import (
    BaseManager,
    SkillManager,
    ToolManager,
    ResourceManager,
    PipelineManager,
    PipelineStage,
)

# Parsers
from .parsers import (
    SkillParser,
    ToolParser,
    ConfigParser,
)

# Serializers
from .serializers import (
    SkillSerializer,
    ToolSerializer,
    ConfigSerializer,
)

__all__ = [
    # Base
    "BaseEntity",
    # Definitions
    "RuleDefinition",
    "PatternDefinition",
    "RuleConfig",
    # Skills
    "Skill",
    "SkillLevel",
    "SkillType",
    "OrchestratorSkill",
    "DetectorSkill",
    "FixerSkill",
    # Tools
    "Tool",
    "ToolType",
    "DetectorTool",
    "FixerTool",
    # Resources
    "Resource",
    "ResourceType",
    "FileFormat",
    "ConfigResource",
    "RulesResource",
    "PatternsResource",
    # Legacy
    "Issue",
    "Severity",
    # Managers
    "BaseManager",
    "SkillManager",
    "ToolManager",
    "ResourceManager",
    "PipelineManager",
    "PipelineStage",
    # Parsers
    "SkillParser",
    "ToolParser",
    "ConfigParser",
    # Serializers
    "SkillSerializer",
    "ToolSerializer",
    "ConfigSerializer",
]
