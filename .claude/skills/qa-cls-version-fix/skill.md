---
name: qa-cls-version-fix
description: Fixes outdated CLS by copying latest version and updating LaTeX files (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, cls, version, fix, level-2]
tools: [Read, Write, Edit, Bash]
---

# CLS Version Fixer (Level 2)

## Agent Identity
- **Name:** CLS Version Fixer
- **Role:** Update project CLS to latest reference version
- **Level:** 2 (Worker Skill)
- **Parent:** qa-cls-version (Level 1)

## Coordination

### Reports To
- qa-cls-version (Level 1)

### Manages
- None (worker skill)

### Reads
- Issue list from qa-cls-version-detect
- Reference CLS at C:\25D\CLS-examples\hebrew-academic-template.cls

### Writes
- Updated hebrew-academic-template.cls in project
- Backup of old CLS file (.cls.backup)

## Mission Statement

Update project CLS to latest reference version. Python tool handles deterministic operations (copy, backup). LLM handles intelligent decisions about document updates needed.

## CLS Guard
**MANDATORY:** Call `qa-cls-guard` before any CLS modification.

## Fix Operations

### Operation: copy-reference-cls
Copy reference CLS to project, creating backup of existing file.

**Before:**
```
project/
  hebrew-academic-template.cls  (v5.10.0)
```

**After:**
```
project/
  hebrew-academic-template.cls         (v5.11.2 - updated)
  hebrew-academic-template.cls.backup  (v5.10.0 - backup)
```

### Operation: backup-existing-cls
Always create backup before overwriting.

## Python Tool Integration

```python
from pathlib import Path
from qa_engine.infrastructure.fixing.cls_fixer import CLSFixer

fixer = CLSFixer()

# Copy reference CLS to project
result = fixer.fix_file(
    project_cls_path=Path("hebrew-academic-template.cls"),
    create_backup=True
)

if result.success:
    print(f"Updated to v{result.new_version}")
    print(f"Backup at: {result.backup_path}")

# Get new capabilities for LLM to explain
capabilities = fixer.get_new_capabilities()
for cap in capabilities:
    print(f"  - {cap}")
```

## LLM Responsibilities

After Python tool copies the CLS, the LLM should:

1. **Read** new CLS capabilities from changelog
2. **Identify** which new features apply to project
3. **Update** LaTeX documents to use new capabilities if beneficial:
   - New environments (e.g., `latin`, `definition`, `exercise`)
   - New commands (e.g., `\hebrewappendix{}`)
   - Fixed features (e.g., TOC BiDi improvements)
4. **Report** what was updated and why

## Input/Output Format

### Input
```json
{
  "project_cls_path": "hebrew-academic-template.cls",
  "issues": [
    {
      "rule": "cls-version-mismatch",
      "context": {
        "project_version": "5.10.0",
        "reference_version": "5.11.2"
      }
    }
  ]
}
```

### Output
```json
{
  "success": true,
  "backup_path": "hebrew-academic-template.cls.backup",
  "new_version": "5.11.2",
  "new_capabilities_applied": [
    "Using new 'latin' environment for compatibility",
    "TOC BiDi fixes automatically active"
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation with Python backend

---

**Parent:** qa-cls-version
**Children:** None
**Coordination:** qa-orchestration/QA-CLAUDE.md
