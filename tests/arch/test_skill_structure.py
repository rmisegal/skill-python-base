"""
Skill structure validation tests.

Validates:
1. All required skill directories exist
2. Each skill has a skill.md file
3. skill.md files have proper YAML frontmatter
4. Level 2 skills have tool.py files

NOTE: Currently tests LOCAL skill structure at .claude/skills/
Future migration (Phase 5) will update SKILLS_ROOT to global path:
    C:\\Users\\{user}\\.claude\\skills\\
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

import pytest


# Configuration for skill location
# LOCAL: Project-local skills for development
# GLOBAL: User-wide skills after migration (Phase 5)
PROJECT_ROOT = Path(__file__).parent.parent.parent
SKILLS_ROOT = PROJECT_ROOT / ".claude" / "skills"

# Future global path (uncomment after migration):
# SKILLS_ROOT = Path.home() / ".claude" / "skills"


# Expected skill structure
REQUIRED_SKILLS = {
    # Level 0 - Super Orchestrator and Meta-Skills
    "qa-super": {"level": 0, "has_tool": False},
    "insert_qa_skill": {"level": 0, "has_tool": True},
    # Level 1 - Family Orchestrators
    "qa-BiDi": {"level": 1, "has_tool": False},
    "qa-code": {"level": 1, "has_tool": False},
    "qa-typeset": {"level": 1, "has_tool": False},
    "qa-cls-version": {"level": 1, "has_tool": False},
    "qa-table": {"level": 1, "has_tool": False},
    "qa-infra": {"level": 1, "has_tool": False},
    "qa-bib": {"level": 1, "has_tool": False},
    # Level 2 - Worker Skills (Detection)
    "qa-BiDi-detect": {"level": 2, "has_tool": True},
    "qa-code-detect": {"level": 2, "has_tool": True},
    "qa-typeset-detect": {"level": 2, "has_tool": True},
    "qa-cls-version-detect": {"level": 2, "has_tool": True},
    "qa-table-detect": {"level": 2, "has_tool": True},
    "qa-infra-subfiles-detect": {"level": 2, "has_tool": True},
    "qa-bib-detect": {"level": 2, "has_tool": True},
    # Level 2 - Worker Skills (Fixing)
    "qa-BiDi-fix-text": {"level": 2, "has_tool": True},
    "qa-code-fix-background": {"level": 2, "has_tool": True},
    "qa-code-fix-encoding": {"level": 2, "has_tool": True},
    "qa-cls-version-fix": {"level": 2, "has_tool": True},
}

# Required YAML frontmatter fields
REQUIRED_FRONTMATTER_FIELDS = ["name", "description", "version", "tags"]

# Optional but recommended fields
RECOMMENDED_FRONTMATTER_FIELDS = ["author", "tools"]


def parse_yaml_frontmatter(content: str) -> Optional[Dict[str, str]]:
    """Parse YAML frontmatter from skill.md content."""
    pattern = r"^---\s*\n(.*?)\n---"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return None

    frontmatter = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    return frontmatter


class TestSkillDirectoryStructure:
    """Tests for skill directory existence."""

    def test_skills_root_exists(self):
        """Test that .claude/skills directory exists."""
        assert SKILLS_ROOT.exists(), f"Skills root not found: {SKILLS_ROOT}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_directory_exists(self, skill_name: str):
        """Test each required skill directory exists."""
        skill_dir = SKILLS_ROOT / skill_name
        assert skill_dir.exists(), f"Skill directory not found: {skill_dir}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_md_exists(self, skill_name: str):
        """Test each skill has a skill.md file."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        assert skill_md.exists(), f"skill.md not found: {skill_md}"


class TestSkillToolFiles:
    """Tests for tool.py files in Level 2 skills."""

    def get_skills_requiring_tools(self) -> List[str]:
        """Get list of skills that require tool.py."""
        return [name for name, info in REQUIRED_SKILLS.items() if info["has_tool"]]

    @pytest.mark.parametrize(
        "skill_name",
        [name for name, info in REQUIRED_SKILLS.items() if info["has_tool"]],
    )
    def test_tool_py_exists(self, skill_name: str):
        """Test Level 2 skills have tool.py file."""
        tool_py = SKILLS_ROOT / skill_name / "tool.py"
        assert tool_py.exists(), f"tool.py not found for Level 2 skill: {skill_name}"


class TestSkillFrontmatter:
    """Tests for YAML frontmatter in skill.md files."""

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_has_frontmatter(self, skill_name: str):
        """Test each skill.md has YAML frontmatter."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        frontmatter = parse_yaml_frontmatter(content)
        assert frontmatter is not None, f"No YAML frontmatter in: {skill_name}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_frontmatter_has_required_fields(self, skill_name: str):
        """Test frontmatter contains required fields."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        frontmatter = parse_yaml_frontmatter(content)
        assert frontmatter is not None

        missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if f not in frontmatter]
        assert not missing, f"Missing required fields in {skill_name}: {missing}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_frontmatter_name_matches_directory(self, skill_name: str):
        """Test frontmatter name matches skill directory name."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        frontmatter = parse_yaml_frontmatter(content)
        assert frontmatter is not None
        assert frontmatter.get("name") == skill_name, (
            f"Frontmatter name '{frontmatter.get('name')}' "
            f"doesn't match directory '{skill_name}'"
        )


class TestSkillLevels:
    """Tests for skill level hierarchy."""

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_level_in_description(self, skill_name: str):
        """Test skill description includes level indicator."""
        expected_level = REQUIRED_SKILLS[skill_name]["level"]
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        frontmatter = parse_yaml_frontmatter(content)
        assert frontmatter is not None

        description = frontmatter.get("description", "")
        assert f"Level {expected_level}" in description, (
            f"Skill {skill_name} description should include 'Level {expected_level}'"
        )


class TestSkillContent:
    """Tests for skill.md content requirements."""

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_has_agent_identity(self, skill_name: str):
        """Test skill.md has Agent Identity section."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        assert "## Agent Identity" in content, (
            f"Missing '## Agent Identity' section in {skill_name}"
        )

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_has_coordination(self, skill_name: str):
        """Test skill.md has Coordination section."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        assert "## Coordination" in content, (
            f"Missing '## Coordination' section in {skill_name}"
        )

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_has_mission_statement(self, skill_name: str):
        """Test skill.md has Mission Statement section."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        assert "## Mission Statement" in content, (
            f"Missing '## Mission Statement' section in {skill_name}"
        )

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS.keys())
    def test_skill_has_version_history(self, skill_name: str):
        """Test skill.md has Version History section."""
        skill_md = SKILLS_ROOT / skill_name / "skill.md"
        content = skill_md.read_text(encoding="utf-8")

        assert "## Version History" in content, (
            f"Missing '## Version History' section in {skill_name}"
        )
