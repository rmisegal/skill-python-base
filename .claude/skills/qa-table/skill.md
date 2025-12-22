---
name: qa-table
description: Table family orchestrator (Level 1) - manages all table QA skills in parallel for Hebrew RTL documents (user)
version: 1.0.0
author: QA Team
tags: [qa, table, orchestrator, level-1, rtl]
---

# Table QA Family Orchestrator (Level 1)

## Agent Identity
- **Name:** Table QA Orchestrator
- **Role:** Coordinate table detection and fix skills
- **Level:** 1 (Family Orchestrator)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0 Super Orchestrator)

### Manages
| Skill | Purpose | Priority |
|-------|---------|----------|
| `qa-table-detect` | Detect table layout issues | HIGH |
| `qa-table-fix-columns` | Fix column order | MEDIUM |
| `qa-table-fix-captions` | Fix caption alignment | MEDIUM |
| `qa-table-fix-alignment` | Fix cell alignment | MEDIUM |
| `qa-table-fancy-fix` | Convert to styled tables | LOW |
| `qa-table-overflow-fix` | Add resizebox wrapper | MEDIUM |

### CLS Policy
**Remind all child fixers:** Before modifying any .cls file, call `qa-cls-guard` for user approval.

## Python Tool Integration

This family uses Python tools for deterministic detection:
- `TableDetector` in `src/qa_engine/infrastructure/detection/table_detector.py`
- 5 detection rules implemented via regex

## Workflow

1. Run qa-table-detect (Python-backed)
2. If issues found, delegate to appropriate fix skills
3. Verify fixes applied correctly
4. Report results to qa-super

## Mission Statement

Ensure all tables in Hebrew RTL documents render correctly with proper
column order, caption placement, cell alignment, and styling.

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend
