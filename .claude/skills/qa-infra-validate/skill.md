---
name: qa-infra-validate
description: Validates project structure after reorganization (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, infra, validate, verify, level-2]
family: infra
parent: qa-infra
has_python_tool: true
operations:
  - directory-check
  - readme-check
  - file-location-check
  - file-count-check
---

# Infrastructure Validate Skill (Level 2)

## Agent Identity
- **Name:** Structure Validator
- **Role:** Post-Reorganization Verification
- **Level:** 2 (Skill)
- **Parent:** qa-infra (Level 1)

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic validation.

### Functions
- `validate(project_path, expected_file_count)` - Validate project structure
- `get_required_dirs()` - Get list of required directories
- `get_valid_extensions()` - Get valid file extensions per directory

### Usage
```python
from tool import validate, get_required_dirs

# Get configuration
dirs = get_required_dirs()

# Run validation
result = validate("/path/to/project", expected_file_count=45)
```

## Operations (Python Implementation)

| Operation ID | Description |
|--------------|-------------|
| `directory-check` | Verify all required directories exist |
| `readme-check` | Verify README.md is in project root |
| `file-location-check` | Verify files are in correct directories |
| `file-count-check` | Compare file count before/after |

## Validation Criteria

### PASS Requirements
- All required directories exist
- README.md in root
- All files in correct directories
- No files lost

### FAIL Triggers
- Required directories missing
- README.md not in root
- Files in wrong directories
- Files lost during reorganization

## Output Format

```json
{
  "skill": "qa-infra-validate",
  "status": "DONE",
  "verdict": "PASS",
  "checks": {
    "directories": "11/11 present",
    "readme_in_root": true,
    "files_correct": true,
    "no_files_lost": true
  },
  "issues": []
}
```

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0** (2025-11-28): Initial LLM-only implementation

---

**Parent:** qa-infra (Level 1)
**Sibling:** qa-infra-scan, qa-infra-backup, qa-infra-reorganize
