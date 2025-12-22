"""
Tests for Skill Creator.

Tests for insert_qa_skill skill creation functionality.
"""

import pytest
from pathlib import Path

from qa_engine.sdk import SkillCreator, SkillConfig, CreationResult


class TestSkillCreator:
    """Tests for SkillCreator."""

    def setup_method(self):
        """Create temporary skills root."""
        self.skills_root = Path(__file__).parent / "temp_skills"
        self.skills_root.mkdir(exist_ok=True)
        self.creator = SkillCreator(self.skills_root)

    def teardown_method(self):
        """Clean up temporary files."""
        import shutil
        if self.skills_root.exists():
            shutil.rmtree(self.skills_root)

    def test_create_basic_skill(self):
        """Test creating a basic Level 2 skill."""
        config = SkillConfig(
            name="qa-test-detect",
            family="test",
            level=2,
            skill_type="detection",
            description="Test detection skill",
        )

        result = self.creator.create_skill(config)
        assert result.success
        assert len(result.created_files) == 1
        assert "skill.md" in result.created_files[0]

    def test_create_skill_with_python(self):
        """Test creating skill with Python tool."""
        config = SkillConfig(
            name="qa-test-detect-py",
            family="test",
            level=2,
            skill_type="detection",
            description="Test with Python",
            generate_python=True,
        )

        result = self.creator.create_skill(config)
        assert result.success
        assert len(result.created_files) == 2
        assert any("tool.py" in f for f in result.created_files)

    def test_create_skill_with_rules(self):
        """Test creating skill with detection rules."""
        config = SkillConfig(
            name="qa-test-detect-rules",
            family="test",
            level=2,
            skill_type="detection",
            description="Test with rules",
            rules=["rule-1", "rule-2", "rule-3"],
            generate_python=True,
        )

        result = self.creator.create_skill(config)
        assert result.success

        skill_path = self.skills_root / "qa-test-detect-rules" / "skill.md"
        content = skill_path.read_text()
        assert "rule-1" in content
        assert "rule-2" in content

    def test_validate_missing_qa_prefix(self):
        """Test validation fails without qa- prefix."""
        config = SkillConfig(
            name="test-detect",
            family="test",
            level=2,
            skill_type="detection",
            description="Invalid name",
        )

        result = self.creator.create_skill(config)
        assert not result.success
        assert any("qa-" in e for e in result.errors)

    def test_validate_invalid_level(self):
        """Test validation fails with invalid level."""
        config = SkillConfig(
            name="qa-test-detect",
            family="test",
            level=5,
            skill_type="detection",
            description="Invalid level",
        )

        result = self.creator.create_skill(config)
        assert not result.success
        assert any("Level" in e for e in result.errors)

    def test_validate_invalid_type(self):
        """Test validation fails with invalid type."""
        config = SkillConfig(
            name="qa-test-detect",
            family="test",
            level=2,
            skill_type="invalid",
            description="Invalid type",
        )

        result = self.creator.create_skill(config)
        assert not result.success
        assert any("Type" in e for e in result.errors)

    def test_validate_missing_family(self):
        """Test validation fails without family."""
        config = SkillConfig(
            name="qa-test-detect",
            family="",
            level=2,
            skill_type="detection",
            description="No family",
        )

        result = self.creator.create_skill(config)
        assert not result.success
        assert any("Family" in e for e in result.errors)

    def test_skill_md_has_frontmatter(self):
        """Test generated skill.md has proper frontmatter."""
        config = SkillConfig(
            name="qa-test-frontmatter",
            family="test",
            level=2,
            skill_type="detection",
            description="Test frontmatter",
        )

        result = self.creator.create_skill(config)
        skill_path = self.skills_root / "qa-test-frontmatter" / "skill.md"
        content = skill_path.read_text()

        assert content.startswith("---")
        assert "name: qa-test-frontmatter" in content
        assert "version: 1.0.0" in content

    def test_skill_md_has_required_sections(self):
        """Test generated skill.md has required sections."""
        config = SkillConfig(
            name="qa-test-sections",
            family="test",
            level=2,
            skill_type="detection",
            description="Test sections",
        )

        result = self.creator.create_skill(config)
        skill_path = self.skills_root / "qa-test-sections" / "skill.md"
        content = skill_path.read_text()

        assert "## Agent Identity" in content
        assert "## Coordination" in content
        assert "## Mission Statement" in content
        assert "## Version History" in content

    def test_level_1_orchestrator(self):
        """Test creating Level 1 orchestrator."""
        config = SkillConfig(
            name="qa-new-family",
            family="new",
            level=1,
            skill_type="orchestrator",
            description="New family orchestrator",
        )

        result = self.creator.create_skill(config)
        assert result.success

        skill_path = self.skills_root / "qa-new-family" / "skill.md"
        content = skill_path.read_text()
        assert "Level 1" in content
        assert "qa-super" in content

    def test_python_not_generated_for_level_1(self):
        """Test Python tool not generated for Level 1."""
        config = SkillConfig(
            name="qa-no-python",
            family="test",
            level=1,
            skill_type="orchestrator",
            description="No Python for L1",
            generate_python=True,
        )

        result = self.creator.create_skill(config)
        assert result.success
        assert len(result.created_files) == 1
