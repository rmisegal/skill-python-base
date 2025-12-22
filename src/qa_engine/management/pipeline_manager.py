"""
Pipeline manager for managing the QA execution pipeline.

Handles skill ordering, insertion, removal, and execution control.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.models import Skill, SkillType
from ..parsers.config_parser import ConfigParser
from ..serializers.config_serializer import ConfigSerializer
from .skill_manager import SkillManager


@dataclass
class PipelineStage:
    """Represents a stage in the QA pipeline."""

    skill_id: str
    order: int
    enabled: bool = True
    parallel_with: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "skill_id": self.skill_id,
            "order": self.order,
            "enabled": self.enabled,
            "parallel_with": self.parallel_with,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineStage":
        """Create from dictionary."""
        return cls(
            skill_id=data["skill_id"],
            order=data["order"],
            enabled=data.get("enabled", True),
            parallel_with=data.get("parallel_with", []),
        )


class PipelineManager:
    """Manages the QA execution pipeline."""

    TYPE_ORDER = {  # Implicit execution order by skill type
        SkillType.ORCHESTRATOR: 0, SkillType.DETECTION: 1,
        SkillType.FIX: 2, SkillType.VALIDATION: 3,
    }

    def __init__(self, config_path: Path, skill_manager: SkillManager):
        """Initialize pipeline manager."""
        self._config_path = config_path
        self._skill_manager = skill_manager
        self._stages: List[PipelineStage] = []
        self._parser = ConfigParser()
        self._serializer = ConfigSerializer()

    # Pipeline Operations

    def insert_skill(self, skill_id: str, position: Optional[int] = None) -> None:
        """Insert a skill into the pipeline."""
        if self._find_stage(skill_id):
            raise ValueError(f"Skill already in pipeline: {skill_id}")

        skill = self._skill_manager.read(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        if position is None:
            position = self._determine_position(skill)

        stage = PipelineStage(skill_id=skill_id, order=position)
        self._stages.append(stage)
        self._reorder()

    def remove_skill(self, skill_id: str) -> bool:
        """Remove a skill from the pipeline."""
        stage = self._find_stage(skill_id)
        if stage:
            self._stages.remove(stage)
            self._reorder()
            return True
        return False

    def move_skill(self, skill_id: str, new_position: int) -> None:
        """Move a skill to a new position."""
        stage = self._find_stage(skill_id)
        if not stage:
            raise ValueError(f"Skill not in pipeline: {skill_id}")
        stage.order = new_position
        self._reorder()

    def reorder(self, skill_ids: List[str]) -> None:
        """Reorder pipeline based on skill ID list."""
        for i, skill_id in enumerate(skill_ids):
            stage = self._find_stage(skill_id)
            if stage:
                stage.order = i
        self._reorder()

    # Execution Control

    def enable_stage(self, skill_id: str) -> bool:
        """Enable a pipeline stage."""
        stage = self._find_stage(skill_id)
        if stage:
            stage.enabled = True
            return True
        return False

    def disable_stage(self, skill_id: str) -> bool:
        """Disable a pipeline stage."""
        stage = self._find_stage(skill_id)
        if stage:
            stage.enabled = False
            return True
        return False

    def set_parallel(self, skill_ids: List[str]) -> None:
        """Set skills to run in parallel."""
        for skill_id in skill_ids:
            stage = self._find_stage(skill_id)
            if stage:
                stage.parallel_with = [s for s in skill_ids if s != skill_id]

    # Configuration

    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get current pipeline configuration."""
        return {
            "stages": [s.to_dict() for s in self._stages],
            "version": "1.0.0",
        }

    def get_ordered_stages(self) -> List[PipelineStage]:
        """Get stages in execution order."""
        return sorted(self._stages, key=lambda s: s.order)

    def get_enabled_stages(self) -> List[PipelineStage]:
        """Get only enabled stages in order."""
        return [s for s in self.get_ordered_stages() if s.enabled]

    # Persistence

    def save_pipeline(self) -> None:
        """Save pipeline configuration to file."""
        config = self.get_pipeline_config()
        self._serializer.write(config, self._config_path)

    def load_pipeline(self) -> None:
        """Load pipeline configuration from file."""
        if not self._config_path.exists():
            self._stages = []
            return

        config = self._parser.parse(self._config_path)
        self._stages = [
            PipelineStage.from_dict(s) for s in config.get("stages", [])
        ]

    # Internal helpers

    def _find_stage(self, skill_id: str) -> Optional[PipelineStage]:
        """Find a stage by skill ID."""
        for stage in self._stages:
            if stage.skill_id == skill_id:
                return stage
        return None

    def _determine_position(self, skill: Skill) -> int:
        """Determine insertion position based on skill type."""
        type_order = self.TYPE_ORDER.get(skill.skill_type, 99)

        # Find position after all skills of same or lower type order
        position = 0
        for stage in self._stages:
            stage_skill = self._skill_manager.read(stage.skill_id)
            if stage_skill:
                stage_type_order = self.TYPE_ORDER.get(stage_skill.skill_type, 99)
                if stage_type_order <= type_order:
                    position = max(position, stage.order + 1)

        return position

    def _reorder(self) -> None:
        """Reorder stages by their order field."""
        self._stages.sort(key=lambda s: s.order)
        for i, stage in enumerate(self._stages):
            stage.order = i
