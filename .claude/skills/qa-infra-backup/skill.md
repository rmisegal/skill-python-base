---
name: qa-infra-backup
description: Creates complete project backups before reorganization (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, infra, backup, safety, level-2]
family: infra
parent: qa-infra
has_python_tool: true
operations:
  - create-timestamped-backup
  - preserve-permissions
  - preserve-timestamps
  - include-hidden-files
  - verify-file-count
---

# Infrastructure Backup Skill (Level 2)

## Agent Identity
- **Name:** Project Backup Creator
- **Role:** Backup Management
- **Level:** 2 (Skill)
- **Parent:** qa-infra (Level 1)

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic backup operations.

### Functions
- `create_backup(project_path)` - Create timestamped project backup
- `get_operations()` - Get dict of operation names and descriptions

### Usage
```python
from tool import create_backup, get_operations

# Get supported operations
ops = get_operations()

# Create backup
result = create_backup("/path/to/project")
```

## Operations (Python Implementation)

| Operation ID | Description |
|--------------|-------------|
| `create-timestamped-backup` | Generate `backup_YYYYMMDD_HHMMSS` folder |
| `preserve-permissions` | Copy with `shutil.copy2` preserving perms |
| `preserve-timestamps` | Preserve file modification times |
| `include-hidden-files` | Copy all files including .claude/, etc. |
| `verify-file-count` | Compare file counts for integrity |

## Output Format

```json
{
  "skill": "qa-infra-backup",
  "status": "DONE",
  "backup": {
    "name": "backup_20251128_143022",
    "path": "../backup_20251128_143022/",
    "size": "45.00 MB",
    "files": 234,
    "verified": true
  }
}
```

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0** (2025-11-28): Initial LLM-only implementation

---

**Parent:** qa-infra (Level 1)
**Sibling:** qa-infra-scan, qa-infra-reorganize
