---
name: qa-infra
description: Infrastructure family orchestrator (Level 1) - manages all project structure QA skills in parallel
version: 1.0.0
author: QA Team
tags: [qa, infra, orchestrator, level-1, project-structure]
---

# Infrastructure QA Family Orchestrator (Level 1)

## Agent Identity
- **Name:** Infrastructure QA Orchestrator
- **Role:** Coordinate project structure and setup skills
- **Level:** 1 (Family Orchestrator)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0 Super Orchestrator)

### Manages
| Skill | Purpose | Priority |
|-------|---------|----------|
| `qa-infra-scan` | Analyze project structure | HIGH |
| `qa-infra-subfiles-detect` | Detect subfiles issues | HIGH |
| `qa-infra-subfiles-fix` | Fix subfiles preamble | MEDIUM |
| `qa-cls-sync-detect` | Detect CLS content inconsistencies | HIGH |
| `qa-cls-sync-fix` | Sync all CLS files to master | MEDIUM |
| `qa-infra-backup` | Create project backup | LOW |
| `qa-infra-reorganize` | Move files to correct dirs | LOW |
| `qa-infra-validate` | Verify structure | MEDIUM |

### CLS Policy
**Remind all child fixers:** Before modifying any .cls file, call `qa-cls-guard` for user approval.

## Python Tool Integration

This family uses Python tools for deterministic detection:
- `SubfilesDetector` in `src/qa_engine/infrastructure/detection/subfiles_detector.py`
- `CLSSyncDetector` in `src/qa_engine/infrastructure/detection/cls_sync_detector.py`
- `CLSSyncFixer` in `src/qa_engine/infrastructure/fixing/cls_sync_fixer.py`
- 6 detection rules implemented via Python

## Workflow

1. Run qa-cls-sync-detect (Python-backed) - Check CLS file consistency
2. Run qa-infra-subfiles-detect (Python-backed) - Check subfiles setup
3. If CLS sync issues found, run qa-cls-sync-fix
4. If subfiles issues found, run qa-infra-subfiles-fix
5. Verify project structure
6. Report results to qa-super

## Mission Statement

Ensure LaTeX project structure is correct with proper subfiles setup,
directory organization, and standalone compilation support.

## Version History
- **v1.1.0** (2025-12-21): Added CLS sync detection and fixing skills
- **v1.0.0** (2025-12-15): Initial creation with Python backend
