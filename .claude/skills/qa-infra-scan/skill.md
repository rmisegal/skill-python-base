---
name: qa-infra-scan
description: Scans and analyzes project structure (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, infra, scan, structure, analysis, level-2]
family: infra
parent: qa-infra
has_python_tool: true
operations:
  - directory-inventory
  - file-categorization
  - misplaced-detection
  - structure-report
---

# Infrastructure Scan Skill (Level 2)

## Agent Identity
- **Name:** Project Structure Scanner
- **Role:** Structure Analysis
- **Level:** 2 (Skill)
- **Parent:** qa-infra (Level 1)

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic scanning.

### Functions
- `scan(project_path)` - Scan project structure, return analysis
- `get_required_dirs()` - Get list of required directories
- `get_file_rules()` - Get file categorization rules

### Usage
```python
from tool import scan, get_required_dirs, get_file_rules

# Get configuration
dirs = get_required_dirs()
rules = get_file_rules()

# Run scan
result = scan("/path/to/project")
```

## Operations (Python Implementation)

| Operation ID | Description |
|--------------|-------------|
| `directory-inventory` | Check required directories exist |
| `file-categorization` | Determine target directory for files |
| `misplaced-detection` | Identify files in wrong locations |
| `structure-report` | Generate JSON report |

## Required Directories

```
project-root/
├── .claude/commands/
├── .claude/skills/
├── .claude/agents/
├── .claude/tasks/
├── chapters/
├── images/
├── src/
├── reviews/
├── doc/
└── examples/
```

## File Categorization Rules

| File Type | Pattern | Target Directory |
|-----------|---------|------------------|
| README | README.md | ROOT (stay) |
| Documentation | *.md, *.txt | doc/ |
| Python code | *.py | src/ |
| Images | *.png, *.jpg, *.svg | images/ |
| LaTeX chapters | chapter*.tex | chapters/ |
| Examples | example*.tex | examples/ |

## Output Format

```json
{
  "skill": "qa-infra-scan",
  "status": "DONE",
  "directories": {
    "required": 10,
    "present": 8,
    "missing": ["chapters/", "reviews/"]
  },
  "files": {
    "total": 45,
    "correctly_placed": 38,
    "misplaced": 7
  },
  "misplaced_files": [
    {"file": "diagram.png", "current": "./", "target": "images/"}
  ],
  "triggers": ["qa-infra-reorganize"]
}
```

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0** (2025-11-28): Initial LLM-only implementation

---

**Parent:** qa-infra (Level 1)
**Sibling:** qa-infra-backup, qa-infra-reorganize
