---
name: qa-cls-sync-fix
description: Fixes CLS file inconsistencies by syncing all copies to master version (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, infra, cls, sync, fix, level-2, python-tool]
---

# CLS Sync Fixer Skill (Level 2)

## Agent Identity
- **Name:** CLS Sync Fixer
- **Role:** Synchronize all CLS files to master version
- **Level:** 2 (Worker Skill)
- **Parent:** qa-infra (Level 1)

## Coordination

### Reports To
- qa-infra (Level 1 orchestrator)

### Input
- Issues from qa-cls-sync-detect
- Project root directory

### Output
- Fixed CLS files synced to master
- Backup files created (.cls.backup)

## Fix Operations

### Operation: sync-to-master
Copy master CLS to all other locations, creating backups.

**Before:**
```
project/
  master/hebrew-academic-template.cls         (61848 bytes - reference)
  shared/hebrew-academic-template.cls         (61848 bytes - OK)
  standalone-chapter01/hebrew-academic-template.cls  (61831 bytes - DIFFERS)
  standalone-chapter02/hebrew-academic-template.cls  (61831 bytes - DIFFERS)
```

**After:**
```
project/
  master/hebrew-academic-template.cls         (61848 bytes - reference)
  shared/hebrew-academic-template.cls         (61848 bytes - OK)
  standalone-chapter01/hebrew-academic-template.cls         (61848 bytes - SYNCED)
  standalone-chapter01/hebrew-academic-template.cls.backup  (61831 bytes - backup)
  standalone-chapter02/hebrew-academic-template.cls         (61848 bytes - SYNCED)
  standalone-chapter02/hebrew-academic-template.cls.backup  (61831 bytes - backup)
```

## Python Tool Integration

This skill is backed by Python for file operations:
- **Module:** `qa_engine.infrastructure.fixing.cls_sync_fixer`
- **Class:** `CLSSyncFixer`

### Usage

```python
from qa_engine.infrastructure.fixing.cls_sync_fixer import CLSSyncFixer

fixer = CLSSyncFixer()
result = fixer.fix_project(
    project_root="C:/path/to/project",
    create_backup=True
)

print(f"Fixed {result.files_fixed} files")
for backup in result.backups_created:
    print(f"  Backup: {backup}")
```

## Workflow

1. Read master/hebrew-academic-template.cls
2. For each mismatched CLS file:
   a. Create backup (original.cls.backup)
   b. Copy master content to file
3. Verify all files now match
4. Report results to parent

## Mission Statement

Synchronize all CLS file copies within a project to the master version,
ensuring consistent class definitions across all compilation units.

## CLS Guard
**MANDATORY:** Call `qa-cls-guard` before any CLS modification.

## Version History
- **v1.0.0** (2025-12-21): Initial creation for CLS sync fixing
