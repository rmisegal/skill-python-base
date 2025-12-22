"""
Python tool for qa-cli-structure-fix.

Creates and fixes .claude folder structure for Claude CLI projects.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


# ============================================================
# TEMPLATES
# ============================================================

CLAUDE_MD_TEMPLATE = '''# {project_name} - Claude Context

## Project Overview
{description}

## Development Environment
- **Languages**: Python
- **Platforms**: Windows 11, Linux
- **IDE**: VS Code

## Project Structure
```
{project_name}/
├── .claude/           # Claude CLI configuration
│   ├── agents/        # Agent definitions
│   ├── skills/        # Skill definitions
│   ├── commands/      # Command templates
│   └── tasks/         # Task management
├── src/               # Source code
├── tests/             # Test files
└── README.md          # Documentation
```

## Commands
- `/help` - Show available commands

## Code Standards
- Follow PEP 8 for Python code
- Write clear docstrings
- Keep files under 150 lines

## Testing Instructions
```bash
pytest tests/
```

## Setup Instructions
```bash
pip install -r requirements.txt
```

## Expectations
- Write clean, maintainable code
- Add tests for new features
- Document public APIs
'''

def get_settings_json_content(project_name: str, description: str) -> str:
    """Generate settings.json content."""
    import json
    data = {
        "project": {
            "name": project_name,
            "version": "1.0.0",
            "description": description
        },
        "environment": {
            "python_version": "3.11"
        },
        "paths": {
            "src": "./src",
            "tests": "./tests"
        },
        "features": {
            "auto_test": True,
            "auto_format": True
        }
    }
    return json.dumps(data, indent=2)

PRD_MD_TEMPLATE = '''# Product Requirements Document

## Project Name
{project_name}

## Overview
{description}

## Goals
1. Define project requirements
2. Track development progress
3. Document decisions

## Requirements

### Functional Requirements
- TBD

### Technical Requirements
- Python 3.11+
- See requirements.txt

## Milestones
- [ ] Initial setup
- [ ] Core implementation
- [ ] Testing
- [ ] Documentation

## Success Criteria
- All tests passing
- Documentation complete
'''

AGENT_MD_TEMPLATE = '''---
name: {agent_name}
version: 1.0.0
description: {description}
role: {role}
---

# {agent_name}

## Purpose
{description}

## Capabilities
- Capability 1
- Capability 2
- Capability 3

## Instructions
Define operational guidelines for this agent.

## Policies
Define rules and constraints.

## Required Skills
- skill-name-1
- skill-name-2

## Example Usage
```
Example of how to use this agent
```
'''

SKILL_MD_TEMPLATE = '''---
name: {skill_name}
version: 1.0.0
description: {description}
author: {author}
tags: [{tags}]
---

# {skill_name}

## Overview
{description}

## Requirements
- Requirement 1
- Requirement 2

## Usage
Instructions on how to use this skill.

## Implementation
Technical details and procedures.

## Examples
Practical examples of the skill in action.
'''

COMMAND_MD_TEMPLATE = '''# {command_name}

## Description
{description}

## Usage
```bash
/{command_name} [arguments]
```

## Parameters
- `param1`: Description

## Example
```bash
/{command_name} example
```

## Implementation
Command logic goes here.
'''


# ============================================================
# FIX FUNCTIONS
# ============================================================

def create_folder_structure(
    project_path: str,
    project_name: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create complete .claude folder structure.

    Args:
        project_path: Path to project root
        project_name: Project name (defaults to folder name)
        description: Project description

    Returns:
        Result dictionary with created files/folders
    """
    path = Path(project_path)
    if not path.exists():
        path.mkdir(parents=True)

    if project_name is None:
        project_name = path.name

    if description is None:
        description = f"{project_name} project"

    result = {
        "success": True,
        "created_folders": [],
        "created_files": [],
        "errors": [],
    }

    # Create folders
    folders = [
        ".claude",
        ".claude/agents",
        ".claude/skills",
        ".claude/commands",
        ".claude/tasks",
    ]

    for folder in folders:
        folder_path = path / folder
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                result["created_folders"].append(str(folder_path))
            except Exception as e:
                result["errors"].append(f"Failed to create {folder}: {e}")

    # Create CLAUDE.md
    claude_md_path = path / ".claude" / "CLAUDE.md"
    if not claude_md_path.exists():
        try:
            content = CLAUDE_MD_TEMPLATE.format(
                project_name=project_name,
                description=description,
            )
            claude_md_path.write_text(content, encoding="utf-8")
            result["created_files"].append(str(claude_md_path))
        except Exception as e:
            result["errors"].append(f"Failed to create CLAUDE.md: {e}")

    # Create settings.json
    settings_path = path / ".claude" / "settings.json"
    if not settings_path.exists():
        try:
            content = get_settings_json_content(project_name, description)
            settings_path.write_text(content, encoding="utf-8")
            result["created_files"].append(str(settings_path))
        except Exception as e:
            result["errors"].append(f"Failed to create settings.json: {e}")

    # Create prd.md
    prd_path = path / ".claude" / "prd.md"
    if not prd_path.exists():
        try:
            content = PRD_MD_TEMPLATE.format(
                project_name=project_name,
                description=description,
            )
            prd_path.write_text(content, encoding="utf-8")
            result["created_files"].append(str(prd_path))
        except Exception as e:
            result["errors"].append(f"Failed to create prd.md: {e}")

    # Create planning.md in tasks
    planning_path = path / ".claude" / "tasks" / "planning.md"
    if not planning_path.exists():
        try:
            content = f"# {project_name} - Planning\n\n## Tasks\n\n- [ ] Initial setup\n"
            planning_path.write_text(content, encoding="utf-8")
            result["created_files"].append(str(planning_path))
        except Exception as e:
            result["errors"].append(f"Failed to create planning.md: {e}")

    if result["errors"]:
        result["success"] = False

    return result


def create_agent(
    project_path: str,
    agent_name: str,
    description: str = "Agent description",
    role: str = "General purpose",
) -> Dict[str, Any]:
    """
    Create a new agent.

    Args:
        project_path: Path to project root
        agent_name: Agent name (e.g., code-reviewer)
        description: Agent description
        role: Agent role

    Returns:
        Result dictionary
    """
    path = Path(project_path)
    agent_path = path / ".claude" / "agents" / agent_name
    result = {"success": True, "created_files": [], "errors": []}

    try:
        agent_path.mkdir(parents=True, exist_ok=True)

        agent_md = agent_path / "AGENT.md"
        content = AGENT_MD_TEMPLATE.format(
            agent_name=agent_name,
            description=description,
            role=role,
        )
        agent_md.write_text(content, encoding="utf-8")
        result["created_files"].append(str(agent_md))
    except Exception as e:
        result["success"] = False
        result["errors"].append(str(e))

    return result


def create_skill(
    project_path: str,
    skill_name: str,
    description: str = "Skill description",
    author: str = "Author",
    tags: str = "skill",
) -> Dict[str, Any]:
    """
    Create a new skill.

    Args:
        project_path: Path to project root
        skill_name: Skill name
        description: Skill description
        author: Author name
        tags: Comma-separated tags

    Returns:
        Result dictionary
    """
    path = Path(project_path)
    skill_path = path / ".claude" / "skills" / skill_name
    result = {"success": True, "created_files": [], "errors": []}

    try:
        skill_path.mkdir(parents=True, exist_ok=True)

        skill_md = skill_path / "skill.md"
        content = SKILL_MD_TEMPLATE.format(
            skill_name=skill_name,
            description=description,
            author=author,
            tags=tags,
        )
        skill_md.write_text(content, encoding="utf-8")
        result["created_files"].append(str(skill_md))
    except Exception as e:
        result["success"] = False
        result["errors"].append(str(e))

    return result


def create_command(
    project_path: str,
    command_name: str,
    description: str = "Command description",
) -> Dict[str, Any]:
    """
    Create a new command.

    Args:
        project_path: Path to project root
        command_name: Command name (without .md)
        description: Command description

    Returns:
        Result dictionary
    """
    path = Path(project_path)
    commands_path = path / ".claude" / "commands"
    result = {"success": True, "created_files": [], "errors": []}

    try:
        commands_path.mkdir(parents=True, exist_ok=True)

        command_md = commands_path / f"{command_name}.md"
        content = COMMAND_MD_TEMPLATE.format(
            command_name=command_name,
            description=description,
        )
        command_md.write_text(content, encoding="utf-8")
        result["created_files"].append(str(command_md))
    except Exception as e:
        result["success"] = False
        result["errors"].append(str(e))

    return result


def fix_issues(
    project_path: str,
    issues: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Fix detected issues.

    Args:
        project_path: Path to project root
        issues: List of issues from detection

    Returns:
        Fix result dictionary
    """
    result = {
        "success": True,
        "fixed": [],
        "errors": [],
    }

    path = Path(project_path)

    for issue in issues:
        rule = issue.get("rule", "")
        missing_path = issue.get("context", {}).get("missing_path", "")

        try:
            if "folder" in rule:
                # Create missing folder
                folder_path = Path(missing_path)
                folder_path.mkdir(parents=True, exist_ok=True)
                result["fixed"].append(f"Created folder: {missing_path}")

            elif rule == "cli-missing-claude-md":
                # Create CLAUDE.md
                file_path = Path(missing_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                content = CLAUDE_MD_TEMPLATE.format(
                    project_name=path.name,
                    description=f"{path.name} project",
                )
                file_path.write_text(content, encoding="utf-8")
                result["fixed"].append(f"Created file: {missing_path}")

            elif rule == "cli-missing-settings-json":
                # Create settings.json
                file_path = Path(missing_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                content = get_settings_json_content(path.name, f"{path.name} project")
                file_path.write_text(content, encoding="utf-8")
                result["fixed"].append(f"Created file: {missing_path}")

            elif rule == "cli-missing-prd-md":
                # Create prd.md
                file_path = Path(missing_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                content = PRD_MD_TEMPLATE.format(
                    project_name=path.name,
                    description=f"{path.name} project",
                )
                file_path.write_text(content, encoding="utf-8")
                result["fixed"].append(f"Created file: {missing_path}")

        except Exception as e:
            result["errors"].append(f"Failed to fix {rule}: {e}")

    if result["errors"]:
        result["success"] = False

    return result


# For API compatibility with detection tools
def run_detection(file_path: str, content: str = None) -> List[Dict[str, Any]]:
    """Run detection (delegates to detect tool)."""
    # Import detection tool
    import sys
    detect_path = Path(__file__).parent.parent / "qa-cli-structure-detect"
    sys.path.insert(0, str(detect_path))
    try:
        from tool import run_detection as detect
        return detect(file_path, content)
    except ImportError:
        return [{"error": "Detection tool not found"}]


def get_rules() -> Dict[str, str]:
    """Get available fix rules."""
    return {
        "cli-create-folder-structure": "Create complete .claude folder structure",
        "cli-create-claude-md": "Create CLAUDE.md file with template",
        "cli-create-settings-json": "Create settings.json file",
        "cli-create-prd-md": "Create prd.md file",
        "cli-create-agent": "Create new agent with AGENT.md",
        "cli-create-skill": "Create new skill with skill.md",
        "cli-create-command": "Create new command file",
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tool.py <project_path> [command]")
        print("\nCommands:")
        print("  init              - Create full structure")
        print("  agent <name>      - Create agent")
        print("  skill <name>      - Create skill")
        print("  command <name>    - Create command")
        print("  fix               - Fix detected issues")
        sys.exit(1)

    project = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "init"

    if command == "init":
        print(f"Initializing .claude structure in: {project}")
        result = create_folder_structure(project)
        print(f"\nCreated folders: {len(result['created_folders'])}")
        for f in result["created_folders"]:
            print(f"  + {f}")
        print(f"\nCreated files: {len(result['created_files'])}")
        for f in result["created_files"]:
            print(f"  + {f}")
        if result["errors"]:
            print(f"\nErrors: {result['errors']}")

    elif command == "agent" and len(sys.argv) > 3:
        name = sys.argv[3]
        result = create_agent(project, name)
        print(f"Created agent: {name}")
        for f in result["created_files"]:
            print(f"  + {f}")

    elif command == "skill" and len(sys.argv) > 3:
        name = sys.argv[3]
        result = create_skill(project, name)
        print(f"Created skill: {name}")
        for f in result["created_files"]:
            print(f"  + {f}")

    elif command == "command" and len(sys.argv) > 3:
        name = sys.argv[3]
        result = create_command(project, name)
        print(f"Created command: {name}")
        for f in result["created_files"]:
            print(f"  + {f}")

    elif command == "fix":
        issues = run_detection(project)
        if issues:
            print(f"Found {len(issues)} issues, fixing...")
            result = fix_issues(project, issues)
            for f in result["fixed"]:
                print(f"  + {f}")
        else:
            print("No issues to fix")
