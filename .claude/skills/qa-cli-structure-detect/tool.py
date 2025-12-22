"""
Python tool for qa-cli-structure-detect.

Detects missing or improper .claude folder structure for Claude CLI projects.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional


# Required structure definition
REQUIRED_FOLDERS = [
    ".claude",
    ".claude/agents",
    ".claude/skills",
    ".claude/commands",
    ".claude/tasks",
]

REQUIRED_FILES = [
    ".claude/CLAUDE.md",
    ".claude/settings.json",
]

OPTIONAL_FILES = [
    ".claude/prd.md",
]


def run_detection(
    project_path: str,
    content: str = None,
) -> List[Dict[str, Any]]:
    """
    Detect missing .claude folder structure.

    Args:
        project_path: Path to project root directory
        content: Ignored (for API compatibility)

    Returns:
        List of issue dictionaries
    """
    path = Path(project_path)

    # If given a file, use its parent directory
    if path.is_file():
        path = path.parent

    if not path.exists():
        return [{"error": f"Path not found: {project_path}"}]

    issues = []

    # Check required folders
    for folder in REQUIRED_FOLDERS:
        folder_path = path / folder
        if not folder_path.exists():
            rule = _get_rule_for_folder(folder)
            issues.append({
                "rule": rule,
                "file": str(path),
                "line": 0,
                "content": folder,
                "severity": "WARNING",
                "fix": f"Create folder: {folder}",
                "context": {"missing_path": str(folder_path)},
            })

    # Check required files
    for file in REQUIRED_FILES:
        file_path = path / file
        if not file_path.exists():
            rule = _get_rule_for_file(file)
            issues.append({
                "rule": rule,
                "file": str(path),
                "line": 0,
                "content": file,
                "severity": "WARNING",
                "fix": f"Create file: {file}",
                "context": {"missing_path": str(file_path)},
            })

    # Check optional files (INFO level)
    for file in OPTIONAL_FILES:
        file_path = path / file
        if not file_path.exists():
            rule = _get_rule_for_file(file)
            issues.append({
                "rule": rule,
                "file": str(path),
                "line": 0,
                "content": file,
                "severity": "INFO",
                "fix": f"Consider creating: {file}",
                "context": {"missing_path": str(file_path)},
            })

    return issues


def detect_project_structure(project_path: str) -> Dict[str, Any]:
    """
    Comprehensive project structure analysis.

    Args:
        project_path: Path to project root

    Returns:
        Structure analysis dictionary
    """
    path = Path(project_path)
    if path.is_file():
        path = path.parent

    result = {
        "project_path": str(path),
        "has_claude_folder": (path / ".claude").exists(),
        "folders": {},
        "files": {},
        "agents": [],
        "skills": [],
        "commands": [],
        "issues": [],
    }

    # Check folders
    for folder in REQUIRED_FOLDERS:
        folder_path = path / folder
        result["folders"][folder] = folder_path.exists()

    # Check files
    for file in REQUIRED_FILES + OPTIONAL_FILES:
        file_path = path / file
        result["files"][file] = file_path.exists()

    # List agents
    agents_path = path / ".claude" / "agents"
    if agents_path.exists():
        result["agents"] = [
            d.name for d in agents_path.iterdir() if d.is_dir()
        ]

    # List skills
    skills_path = path / ".claude" / "skills"
    if skills_path.exists():
        result["skills"] = [
            d.name for d in skills_path.iterdir() if d.is_dir()
        ]

    # List commands
    commands_path = path / ".claude" / "commands"
    if commands_path.exists():
        result["commands"] = [
            f.stem for f in commands_path.glob("*.md")
        ]

    # Get issues
    result["issues"] = run_detection(project_path)

    return result


def _get_rule_for_folder(folder: str) -> str:
    """Get rule ID for missing folder."""
    folder_rules = {
        ".claude": "cli-missing-claude-folder",
        ".claude/agents": "cli-missing-agents-folder",
        ".claude/skills": "cli-missing-skills-folder",
        ".claude/commands": "cli-missing-commands-folder",
        ".claude/tasks": "cli-missing-tasks-folder",
    }
    return folder_rules.get(folder, "cli-missing-folder")


def _get_rule_for_file(file: str) -> str:
    """Get rule ID for missing file."""
    file_rules = {
        ".claude/CLAUDE.md": "cli-missing-claude-md",
        ".claude/settings.json": "cli-missing-settings-json",
        ".claude/prd.md": "cli-missing-prd-md",
    }
    return file_rules.get(file, "cli-missing-file")


def get_rules() -> Dict[str, str]:
    """Get available detection rules."""
    return {
        "cli-missing-claude-folder": "Missing .claude folder in project root",
        "cli-missing-agents-folder": "Missing .claude/agents folder",
        "cli-missing-skills-folder": "Missing .claude/skills folder",
        "cli-missing-commands-folder": "Missing .claude/commands folder",
        "cli-missing-tasks-folder": "Missing .claude/tasks folder",
        "cli-missing-claude-md": "Missing .claude/CLAUDE.md file",
        "cli-missing-settings-json": "Missing .claude/settings.json file",
        "cli-missing-prd-md": "Missing .claude/prd.md file",
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        project = sys.argv[1]
    else:
        project = "."

    print(f"Analyzing project: {project}")
    print("=" * 60)

    result = detect_project_structure(project)

    print(f"\nProject: {result['project_path']}")
    print(f"Has .claude folder: {result['has_claude_folder']}")

    print("\nFolders:")
    for folder, exists in result["folders"].items():
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {folder}")

    print("\nFiles:")
    for file, exists in result["files"].items():
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {file}")

    if result["agents"]:
        print(f"\nAgents: {', '.join(result['agents'])}")
    if result["skills"]:
        print(f"Skills: {', '.join(result['skills'])}")
    if result["commands"]:
        print(f"Commands: {', '.join(result['commands'])}")

    if result["issues"]:
        print(f"\nIssues ({len(result['issues'])}):")
        for issue in result["issues"]:
            print(f"  [{issue['severity']}] {issue['rule']}: {issue['fix']}")
