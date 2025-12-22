"""
Skill registry service.

Discovers and manages QA skills. Implements FR-103 from PRD.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from ..models.skill import SkillLevel, SkillMetadata, SkillType


class SkillRegistry:
    """
    Service for discovering and managing QA skills.

    Scans skill directories, parses frontmatter, and builds
    skill hierarchy as per FR-103 acceptance criteria.
    """

    def __init__(self) -> None:
        self._skills: Dict[str, SkillMetadata] = {}
        self._by_level: Dict[SkillLevel, List[str]] = {
            SkillLevel.L0_SUPER: [],
            SkillLevel.L1_FAMILY: [],
            SkillLevel.L2_LEAF: [],
        }

    def discover(self, skills_dir: str | Path) -> int:
        """
        Discover all QA skills in directory.

        Args:
            skills_dir: Path to skills directory

        Returns:
            Number of skills discovered
        """
        path = Path(skills_dir)
        if not path.exists():
            return 0

        count = 0
        for skill_dir in path.iterdir():
            if skill_dir.is_dir() and skill_dir.name.startswith("qa-"):
                skill_md = skill_dir / "skill.md"
                if skill_md.exists():
                    metadata = self._parse_skill(skill_md)
                    if metadata:
                        self._register(metadata)
                        count += 1

        return count

    def _parse_skill(self, skill_md: Path) -> Optional[SkillMetadata]:
        """Parse skill.md frontmatter into SkillMetadata."""
        try:
            content = skill_md.read_text(encoding="utf-8")
            frontmatter = self._extract_frontmatter(content)
            if not frontmatter:
                return None

            name = frontmatter.get("name", skill_md.parent.name)
            level = self._determine_level(name, frontmatter)
            skill_type = self._determine_type(name, frontmatter)

            return SkillMetadata(
                name=name,
                description=frontmatter.get("description", ""),
                version=frontmatter.get("version", "1.0.0"),
                level=level,
                skill_type=skill_type,
                family=self._extract_family(name),
                parent=frontmatter.get("parent"),
                children=frontmatter.get("children", []),
                has_python_tool=(skill_md.parent / "tool.py").exists(),
                path=skill_md.parent,
                tags=frontmatter.get("tags", []),
            )
        except Exception:
            return None

    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, str]]:
        """Extract YAML frontmatter from skill.md content."""
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None

        frontmatter: Dict[str, str] = {}
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value.startswith("[") and value.endswith("]"):
                    frontmatter[key] = [
                        v.strip().strip('"').strip("'")
                        for v in value[1:-1].split(",")
                    ]
                else:
                    frontmatter[key] = value

        return frontmatter

    def _determine_level(
        self,
        name: str,
        frontmatter: Dict[str, str],
    ) -> SkillLevel:
        """Determine skill level from name and frontmatter."""
        if name == "qa-super":
            return SkillLevel.L0_SUPER
        if "-detect" in name or "-fix-" in name:
            return SkillLevel.L2_LEAF
        return SkillLevel.L1_FAMILY

    def _determine_type(
        self,
        name: str,
        frontmatter: Dict[str, str],
    ) -> SkillType:
        """Determine skill type from name and frontmatter."""
        if "-detect" in name:
            return SkillType.DETECTION
        if "-fix-" in name:
            return SkillType.FIX
        if "-validate" in name:
            return SkillType.VALIDATION
        return SkillType.ORCHESTRATOR

    def _extract_family(self, name: str) -> Optional[str]:
        """Extract family name from skill name."""
        parts = name.split("-")
        if len(parts) >= 2 and parts[0] == "qa":
            return parts[1]
        return None

    def _register(self, metadata: SkillMetadata) -> None:
        """Register skill in registry."""
        self._skills[metadata.name] = metadata
        self._by_level[metadata.level].append(metadata.name)

    def get(self, name: str) -> Optional[SkillMetadata]:
        """Get skill metadata by name."""
        return self._skills.get(name)

    def get_by_level(self, level: SkillLevel) -> List[SkillMetadata]:
        """Get all skills at a specific level."""
        return [self._skills[n] for n in self._by_level[level]]

    def get_detectors(self) -> List[SkillMetadata]:
        """Get all detector skills."""
        return [s for s in self._skills.values() if s.is_detector()]

    def get_fixers(self) -> List[SkillMetadata]:
        """Get all fixer skills."""
        return [s for s in self._skills.values() if s.is_fixer()]

    def get_family_skills(self, family: str) -> List[SkillMetadata]:
        """Get all skills in a family."""
        return [s for s in self._skills.values() if s.family == family]

    @property
    def all_skills(self) -> List[SkillMetadata]:
        """Get all registered skills."""
        return list(self._skills.values())

    @property
    def skill_count(self) -> int:
        """Get total number of registered skills."""
        return len(self._skills)
