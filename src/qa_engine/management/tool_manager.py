"""
Tool manager for managing Python tools.

Provides CRUD operations and code generation for tools.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.models import (
    Tool,
    ToolType,
    DetectorTool,
    FixerTool,
    RuleDefinition,
    PatternDefinition,
)
from ..parsers.tool_parser import ToolParser
from ..serializers.tool_serializer import ToolSerializer
from .base_manager import BaseManager


class ToolManager(BaseManager[Tool]):
    """Manages Python tools with CRUD and code generation."""

    def __init__(self, storage_path: Path):
        """Initialize tool manager."""
        super().__init__(storage_path)
        self._parser = ToolParser()
        self._serializer = ToolSerializer()

    # Code Generation

    def generate_detector(
        self,
        name: str,
        description: str,
        rules: Dict[str, RuleDefinition],
        detector_class: str = "Detector",
    ) -> DetectorTool:
        """Generate a new detector tool."""
        tool = DetectorTool(
            id=name,
            name=name,
            description=description,
            tool_type=ToolType.DETECTOR,
            module_path=f"{name}.py",
            entry_function="run_detection",
            rules=rules,
            detector_class=detector_class,
        )
        return self.create(tool)

    def generate_fixer(
        self,
        name: str,
        description: str,
        patterns: Dict[str, PatternDefinition],
        fixer_class: str = "Fixer",
    ) -> FixerTool:
        """Generate a new fixer tool."""
        tool = FixerTool(
            id=name,
            name=name,
            description=description,
            tool_type=ToolType.FIXER,
            module_path=f"{name}.py",
            entry_function="fix",
            patterns=patterns,
            fixer_class=fixer_class,
        )
        return self.create(tool)

    # Rule/Pattern Management

    def add_rule(self, tool_id: str, rule: RuleDefinition) -> None:
        """Add a rule to a detector tool."""
        tool = self.read(tool_id)
        if not isinstance(tool, DetectorTool):
            raise ValueError(f"Tool {tool_id} is not a detector")
        tool.rules[rule.id] = rule
        self._persist(tool)

    def remove_rule(self, tool_id: str, rule_id: str) -> None:
        """Remove a rule from a detector tool."""
        tool = self.read(tool_id)
        if not isinstance(tool, DetectorTool):
            raise ValueError(f"Tool {tool_id} is not a detector")
        if rule_id in tool.rules:
            del tool.rules[rule_id]
            self._persist(tool)

    def add_pattern(self, tool_id: str, pattern: PatternDefinition) -> None:
        """Add a pattern to a fixer tool."""
        tool = self.read(tool_id)
        if not isinstance(tool, FixerTool):
            raise ValueError(f"Tool {tool_id} is not a fixer")
        tool.patterns[pattern.id] = pattern
        self._persist(tool)

    def remove_pattern(self, tool_id: str, pattern_id: str) -> None:
        """Remove a pattern from a fixer tool."""
        tool = self.read(tool_id)
        if not isinstance(tool, FixerTool):
            raise ValueError(f"Tool {tool_id} is not a fixer")
        if pattern_id in tool.patterns:
            del tool.patterns[pattern_id]
            self._persist(tool)

    # Tool Queries

    def get_detectors(self) -> List[DetectorTool]:
        """Get all detector tools."""
        return [t for t in self.list_all() if isinstance(t, DetectorTool)]

    def get_fixers(self) -> List[FixerTool]:
        """Get all fixer tools."""
        return [t for t in self.list_all() if isinstance(t, FixerTool)]

    def validate_tool(self, tool_id: str) -> List[str]:
        """Validate a tool's configuration."""
        tool = self.read(tool_id)
        if not tool:
            return [f"Tool not found: {tool_id}"]
        return tool.validate()

    # Implementation of abstract methods

    def _load_from_storage(self) -> List[Tool]:
        """Load all tools from storage."""
        tools: List[Tool] = []
        if not self._storage_path.exists():
            return tools

        for tool_file in self._storage_path.glob("**/tool.py"):
            tools.append(self._parser.parse(tool_file))
        return tools

    def _load_single(self, entity_id: str) -> Optional[Tool]:
        """Load a single tool from storage."""
        tool_file = self._storage_path / entity_id / "tool.py"
        if tool_file.exists():
            return self._parser.parse(tool_file)
        return None

    def _persist(self, entity: Tool) -> None:
        """Persist tool to storage."""
        tool_dir = self._storage_path / entity.id
        tool_dir.mkdir(parents=True, exist_ok=True)
        tool_file = tool_dir / "tool.py"
        self._serializer.write(entity, tool_file)

    def _remove_persisted(self, entity: Tool) -> None:
        """Remove tool file from storage."""
        tool_dir = self._storage_path / entity.id
        if tool_dir.exists():
            import shutil
            shutil.rmtree(tool_dir)

    def _from_dict(self, data: Dict[str, Any]) -> Tool:
        """Create tool from dictionary."""
        return Tool.from_dict(data)
