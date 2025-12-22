"""
Skill parser for parsing skill.md files into Skill objects.

Handles YAML frontmatter extraction and markdown section parsing.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..domain.models import (
    Skill,
    SkillLevel,
    SkillType,
    OrchestratorSkill,
    DetectorSkill,
    FixerSkill,
    RuleConfig,
)


class SkillParser:
    """Parses skill.md files into Skill objects."""

    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    SECTION_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)

    def parse(self, file_path: Path) -> Skill:
        """Parse a skill.md file into a Skill object."""
        content = file_path.read_text(encoding="utf-8")
        frontmatter, markdown = self._split_frontmatter(content)
        metadata = self._parse_frontmatter(frontmatter)
        sections = self._parse_sections(markdown)

        return self._create_skill(metadata, sections, file_path)

    def _split_frontmatter(self, content: str) -> Tuple[str, str]:
        """Split content into frontmatter and markdown body."""
        match = self.FRONTMATTER_PATTERN.match(content)
        if match:
            frontmatter = match.group(1)
            markdown = content[match.end():]
            return frontmatter, markdown
        return "", content

    def _parse_frontmatter(self, frontmatter: str) -> Dict[str, Any]:
        """Parse YAML frontmatter into dictionary."""
        if not frontmatter:
            return {}
        try:
            return yaml.safe_load(frontmatter) or {}
        except yaml.YAMLError:
            return {}

    def _parse_sections(self, markdown: str) -> Dict[str, str]:
        """Parse markdown into named sections."""
        sections: Dict[str, str] = {}
        matches = list(self.SECTION_PATTERN.finditer(markdown))

        for i, match in enumerate(matches):
            section_name = match.group(1).strip().lower()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            sections[section_name] = markdown[start:end].strip()

        return sections

    def _create_skill(
        self, metadata: Dict[str, Any], sections: Dict[str, str], path: Path
    ) -> Skill:
        """Create appropriate Skill subclass from parsed data."""
        skill_type = self._determine_skill_type(metadata, path)
        level = self._determine_skill_level(metadata, path)
        rules = self._parse_rules(metadata.get("rules", {}))

        base_kwargs = {
            "id": metadata.get("name", path.parent.name),
            "name": metadata.get("name", path.parent.name),
            "description": metadata.get("description", ""),
            "version": metadata.get("version", "1.0.0"),
            "enabled": metadata.get("enabled", True),
            "metadata": metadata.get("metadata", {}),
            "path": path,
            "level": level,
            "skill_type": skill_type,
            "family": metadata.get("family"),
            "parent": metadata.get("parent"),
            "children": metadata.get("children", []),
            "tags": metadata.get("tags", []),
            "system_prompt": sections.get("system prompt", ""),
            "mission_statement": sections.get("mission", ""),
            "tools": metadata.get("tools", []),
            "resources": metadata.get("resources", []),
            "rules": rules,
            "auto_fix": metadata.get("auto_fix", False),
        }

        if skill_type == SkillType.ORCHESTRATOR:
            return OrchestratorSkill(
                **base_kwargs,
                managed_families=metadata.get("managed_families", []),
                coordination_mode=metadata.get("coordination_mode", "parallel"),
            )
        elif skill_type == SkillType.DETECTION:
            return DetectorSkill(
                **base_kwargs,
                detection_rules=metadata.get("detection_rules", []),
                has_python_tool=metadata.get("has_python_tool", False),
            )
        elif skill_type == SkillType.FIX:
            return FixerSkill(
                **base_kwargs,
                fix_patterns=metadata.get("fix_patterns", []),
                has_python_tool=metadata.get("has_python_tool", False),
            )
        return Skill(**base_kwargs)

    def _determine_skill_type(
        self, metadata: Dict[str, Any], path: Path
    ) -> SkillType:
        """Determine skill type from metadata or naming convention."""
        if "skill_type" in metadata:
            return SkillType(metadata["skill_type"])
        name = path.parent.name.lower()
        if "detect" in name:
            return SkillType.DETECTION
        if "fix" in name:
            return SkillType.FIX
        if "orchestrator" in name or name.count("-") == 1:
            return SkillType.ORCHESTRATOR
        return SkillType.DETECTION

    def _determine_skill_level(
        self, metadata: Dict[str, Any], path: Path
    ) -> SkillLevel:
        """Determine skill level from metadata or naming convention."""
        if "level" in metadata:
            return SkillLevel(metadata["level"])
        name = path.parent.name
        if name == "qa-super" or name == "insert_qa_skill":
            return SkillLevel.L0_META
        if name.count("-") == 1:
            return SkillLevel.L1_FAMILY
        return SkillLevel.L2_WORKER

    def _parse_rules(self, rules_data: Dict[str, Any]) -> Dict[str, RuleConfig]:
        """Parse rules configuration."""
        rules: Dict[str, RuleConfig] = {}
        for rule_id, config in rules_data.items():
            if isinstance(config, dict):
                rules[rule_id] = RuleConfig.from_dict(rule_id, config)
            else:
                rules[rule_id] = RuleConfig(rule_id=rule_id, enabled=bool(config))
        return rules
