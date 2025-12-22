"""
Management layer for QA Engine entities.

Provides CRUD operations and pipeline management for:
- Skills (SkillManager)
- Tools (ToolManager)
- Resources (ResourceManager)
- Pipeline (PipelineManager)
"""

from .base_manager import BaseManager
from .skill_manager import SkillManager
from .tool_manager import ToolManager
from .resource_manager import ResourceManager
from .pipeline_manager import PipelineManager, PipelineStage

__all__ = [
    "BaseManager",
    "SkillManager",
    "ToolManager",
    "ResourceManager",
    "PipelineManager",
    "PipelineStage",
]
