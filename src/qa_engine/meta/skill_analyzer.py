"""
Skill analyzer for QA mechanism improvement.

Parses skill.md files and extracts detection rules, patterns, version info.
Aligned with qa-mechanism-improver Phase 2: Skill Analysis.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from .skill_models import DetectionRule, SkillAnalysis


class SkillAnalyzer:
    """
    Analyzes skill.md files for QA mechanism improvement.

    Extracts:
    - YAML frontmatter (metadata)
    - Detection rules and patterns
    - Version history
    - Skill relationships (parent/children)
    """

    SKILLS_PATH = Path(r"C:\Users\gal-t\.claude\skills")
    RULE_PATTERN = r"###\s*Rule\s*(\d+):\s*([^\n]+)"
    REGEX_BLOCK = r"```regex\n(.+?)```"

    def __init__(self, skills_path: Optional[Path] = None):
        """Initialize analyzer with skills directory path."""
        self.skills_path = skills_path or self.SKILLS_PATH

    def analyze_skill(self, skill_id: str) -> Optional[SkillAnalysis]:
        """Analyze a skill by its ID."""
        skill_path = self.skills_path / skill_id / "skill.md"
        if not skill_path.exists():
            return None
        return self._parse_skill_file(skill_path, skill_id)

    def _parse_skill_file(self, path: Path, skill_id: str) -> SkillAnalysis:
        """Parse skill.md file and extract analysis."""
        content = path.read_text(encoding="utf-8")
        fm = self._parse_frontmatter(content)

        return SkillAnalysis(
            skill_id=skill_id,
            name=fm.get("name", skill_id),
            description=fm.get("description", ""),
            version=fm.get("version", "1.0.0"),
            level=self._determine_level(fm, content),
            skill_type=self._determine_type(skill_id, fm),
            parent=self._extract_parent(content),
            family=skill_id.replace("qa-", "").split("-")[0],
            tags=fm.get("tags", []),
            tools=fm.get("tools", []),
            rules=self._extract_rules(content),
            patterns=self._extract_patterns(content),
            has_python_tool=(self.skills_path / skill_id / "tool.py").exists(),
        )

    def _parse_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter from skill.md."""
        match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                pass
        return {}

    def _extract_rules(self, content: str) -> List[DetectionRule]:
        """Extract detection rules from skill.md."""
        rules = []
        matches = list(re.finditer(self.RULE_PATTERN, content))

        for i, match in enumerate(matches):
            start, end = match.end(), matches[i + 1].start() if i + 1 < len(matches) else len(content)
            rule_content = content[start:end]
            regex_match = re.search(self.REGEX_BLOCK, rule_content, re.DOTALL)

            rules.append(DetectionRule(
                name=f"rule-{match.group(1)}",
                description=match.group(2).strip(),
                regex=regex_match.group(1).strip() if regex_match else "",
            ))
        return rules

    def _extract_patterns(self, content: str) -> List[str]:
        """Extract regex patterns from skill.md."""
        patterns = []
        for match in re.finditer(self.REGEX_BLOCK, content, re.DOTALL):
            for line in match.group(1).strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
        return patterns

    def _determine_level(self, fm: Dict, content: str) -> int:
        """Determine skill level from tags or content."""
        tags = fm.get("tags", [])
        if any(t in tags for t in ["level-0", "meta-skill"]) or "Level 0" in content:
            return 0
        if any(t in tags for t in ["level-1", "orchestrator"]) or "Level 1" in content:
            return 1
        return 2

    def _determine_type(self, skill_id: str, fm: Dict) -> str:
        """Determine skill type from ID or frontmatter."""
        for keyword, stype in [("detect", "detection"), ("fix", "fix"), ("validate", "validation")]:
            if keyword in skill_id:
                return stype
        return "orchestrator"

    def _extract_parent(self, content: str) -> str:
        """Extract parent skill from content."""
        match = re.search(r"\*\*Parent:\*\*\s*(\S+)", content)
        return match.group(1) if match else ""

    def list_skills(self) -> List[str]:
        """List all available skill IDs."""
        if not self.skills_path.exists():
            return []
        return [d.name for d in self.skills_path.iterdir()
                if d.is_dir() and (d / "skill.md").exists()]

    def get_skill_hierarchy(self) -> Dict[str, List[str]]:
        """Get skill hierarchy as parent -> children mapping."""
        hierarchy: Dict[str, List[str]] = {}
        for skill_id in self.list_skills():
            analysis = self.analyze_skill(skill_id)
            if analysis and analysis.parent:
                hierarchy.setdefault(analysis.parent, []).append(skill_id)
        return hierarchy
