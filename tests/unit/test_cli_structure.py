"""
Tests for CLI structure detection and fixing tools.

Tests the qa-cli-structure-detect and qa-cli-structure-fix skills.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import importlib

# Add skills to path
skills_path = Path(__file__).parent.parent.parent / ".claude" / "skills"

# Import detect tool
detect_tool_path = skills_path / "qa-cli-structure-detect"
sys.path.insert(0, str(detect_tool_path))
import tool as detect_tool
run_detection = detect_tool.run_detection
detect_project_structure = detect_tool.detect_project_structure
get_rules = detect_tool.get_rules


class TestCLIStructureDetect:
    """Tests for CLI structure detection."""

    def setup_method(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_missing_claude_folder(self):
        """Test detection of missing .claude folder."""
        issues = run_detection(str(self.project_path))
        rules = [i["rule"] for i in issues]
        assert "cli-missing-claude-folder" in rules

    def test_detect_all_missing_folders(self):
        """Test detection of all missing folders."""
        issues = run_detection(str(self.project_path))
        rules = [i["rule"] for i in issues]

        expected = [
            "cli-missing-claude-folder",
            "cli-missing-agents-folder",
            "cli-missing-skills-folder",
            "cli-missing-commands-folder",
            "cli-missing-tasks-folder",
        ]
        for rule in expected:
            assert rule in rules, f"Missing rule: {rule}"

    def test_detect_missing_files(self):
        """Test detection of missing files."""
        # Create .claude folder but no files
        (self.project_path / ".claude").mkdir()

        issues = run_detection(str(self.project_path))
        rules = [i["rule"] for i in issues]

        assert "cli-missing-claude-md" in rules
        assert "cli-missing-settings-json" in rules

    def test_no_issues_when_complete(self):
        """Test no issues when structure is complete."""
        # Create complete structure
        claude_path = self.project_path / ".claude"
        (claude_path / "agents").mkdir(parents=True)
        (claude_path / "skills").mkdir(parents=True)
        (claude_path / "commands").mkdir(parents=True)
        (claude_path / "tasks").mkdir(parents=True)
        (claude_path / "CLAUDE.md").write_text("# Test")
        (claude_path / "settings.json").write_text("{}")
        (claude_path / "prd.md").write_text("# PRD")

        issues = run_detection(str(self.project_path))
        assert len(issues) == 0

    def test_detect_project_structure_analysis(self):
        """Test comprehensive project structure analysis."""
        # Create partial structure
        claude_path = self.project_path / ".claude"
        (claude_path / "agents" / "test-agent").mkdir(parents=True)
        (claude_path / "skills" / "test-skill").mkdir(parents=True)
        (claude_path / "commands").mkdir(parents=True)
        (claude_path / "commands" / "test-cmd.md").write_text("# Test")

        result = detect_project_structure(str(self.project_path))

        assert result["has_claude_folder"] is True
        assert "test-agent" in result["agents"]
        assert "test-skill" in result["skills"]
        assert "test-cmd" in result["commands"]

    def test_get_rules_returns_all_rules(self):
        """Test get_rules returns all expected rules."""
        rules = get_rules()
        assert len(rules) == 8
        assert "cli-missing-claude-folder" in rules
        assert "cli-missing-claude-md" in rules


class TestCLIStructureFix:
    """Tests for CLI structure fixing."""

    def setup_method(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()

        # Import fix tool with unique name
        fix_path = skills_path / "qa-cli-structure-fix"
        import importlib.util
        spec = importlib.util.spec_from_file_location("fix_tool", fix_path / "tool.py")
        self.fix_tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.fix_tool)

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_folder_structure(self):
        """Test creating complete folder structure."""
        result = self.fix_tool.create_folder_structure(str(self.project_path))

        assert result["success"] is True
        assert (self.project_path / ".claude").exists()
        assert (self.project_path / ".claude" / "agents").exists()
        assert (self.project_path / ".claude" / "skills").exists()
        assert (self.project_path / ".claude" / "commands").exists()
        assert (self.project_path / ".claude" / "tasks").exists()
        assert (self.project_path / ".claude" / "CLAUDE.md").exists()
        assert (self.project_path / ".claude" / "settings.json").exists()

    def test_create_agent(self):
        """Test creating an agent."""
        # First create structure
        (self.project_path / ".claude" / "agents").mkdir(parents=True)

        result = self.fix_tool.create_agent(
            str(self.project_path),
            "test-agent",
            "Test agent description",
            "Tester",
        )

        assert result["success"] is True
        agent_md = self.project_path / ".claude" / "agents" / "test-agent" / "AGENT.md"
        assert agent_md.exists()
        content = agent_md.read_text()
        assert "test-agent" in content
        assert "Test agent description" in content

    def test_create_skill(self):
        """Test creating a skill."""
        # First create structure
        (self.project_path / ".claude" / "skills").mkdir(parents=True)

        result = self.fix_tool.create_skill(
            str(self.project_path),
            "test-skill",
            "Test skill description",
            "Test Author",
            "test, skill",
        )

        assert result["success"] is True
        skill_md = self.project_path / ".claude" / "skills" / "test-skill" / "skill.md"
        assert skill_md.exists()
        content = skill_md.read_text()
        assert "test-skill" in content
        assert "Test skill description" in content

    def test_create_command(self):
        """Test creating a command."""
        # First create structure
        (self.project_path / ".claude" / "commands").mkdir(parents=True)

        result = self.fix_tool.create_command(
            str(self.project_path),
            "test-command",
            "Test command description",
        )

        assert result["success"] is True
        cmd_md = self.project_path / ".claude" / "commands" / "test-command.md"
        assert cmd_md.exists()
        content = cmd_md.read_text()
        assert "test-command" in content
        assert "Test command description" in content

    def test_fix_issues(self):
        """Test fixing detected issues."""
        # Detect issues first
        issues = run_detection(str(self.project_path))
        assert len(issues) > 0

        # Fix issues
        result = self.fix_tool.fix_issues(str(self.project_path), issues)

        assert result["success"] is True
        assert len(result["fixed"]) > 0

        # Verify fixes
        assert (self.project_path / ".claude").exists()
        assert (self.project_path / ".claude" / "CLAUDE.md").exists()

    def test_idempotent_creation(self):
        """Test that creation is idempotent."""
        # Create twice
        result1 = self.fix_tool.create_folder_structure(str(self.project_path))
        result2 = self.fix_tool.create_folder_structure(str(self.project_path))

        assert result1["success"] is True
        assert result2["success"] is True
        # Second run should create nothing new
        assert len(result2["created_folders"]) == 0
        assert len(result2["created_files"]) == 0


class TestCLIStructureIntegration:
    """Integration tests for detect + fix workflow."""

    def setup_method(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()

        # Import fix tool
        fix_path = skills_path / "qa-cli-structure-fix"
        import importlib.util
        spec = importlib.util.spec_from_file_location("fix_tool_int", fix_path / "tool.py")
        self.fix_tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.fix_tool)

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_fix_verify_workflow(self):
        """Test complete detect -> fix -> verify workflow."""
        # 1. Detect issues in empty project
        issues_before = run_detection(str(self.project_path))
        assert len(issues_before) > 0

        # 2. Fix by creating structure
        self.fix_tool.create_folder_structure(str(self.project_path))

        # 3. Verify no issues remain
        issues_after = run_detection(str(self.project_path))
        assert len(issues_after) == 0

    def test_partial_structure_detection(self):
        """Test detection with partial structure."""
        # Create only some folders
        (self.project_path / ".claude" / "agents").mkdir(parents=True)
        (self.project_path / ".claude" / "skills").mkdir(parents=True)

        issues = run_detection(str(self.project_path))

        # Should detect missing commands, tasks folders and files
        rules = [i["rule"] for i in issues]
        assert "cli-missing-commands-folder" in rules
        assert "cli-missing-tasks-folder" in rules
        assert "cli-missing-claude-md" in rules
