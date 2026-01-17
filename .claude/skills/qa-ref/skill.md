---
name: qa-ref
description: Cross-reference family orchestrator (Level 1) - manages all reference QA skills for LaTeX documents
version: 1.0.0
author: QA Team
tags: [qa, ref, reference, cross-reference, orchestrator, level-1]
---

# Cross-Reference QA Family Orchestrator (Level 1)

## Agent Identity
- **Name:** Cross-Reference QA Orchestrator
- **Role:** Coordinate cross-reference detection and fixing
- **Level:** 1 (Family Orchestrator)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0 Super Orchestrator)

### Manages
| Skill | Purpose | Priority |
|-------|---------|----------|
| `qa-ref-detect` | Detect cross-chapter reference issues | HIGH |
| `qa-ref-fix` | Fix cross-chapter references | MEDIUM |

### CLS Policy
**Remind all child fixers:** Before modifying any .cls file, call `qa-cls-guard` for user approval.

## Python Tool Integration

This family uses Python tools for deterministic detection:
- `RefDetector` in `src/qa_engine/reference/detection/ref_detector.py`
- Detection rules for cross-chapter references

## Detection Categories

### 1. Hardcoded Cross-Chapter References
Detects patterns like:
- `ראה פרק \en{2}` (see chapter 2)
- `ראה פרקים \en{2-3}` (see chapters 2-3)
- `יוסבר בפרק \en{5}` (explained in chapter 5)

**Issue:** These break in standalone compilation.

### 2. Undefined References
Detects `\ref{label}` pointing to undefined labels.

### 3. Orphan Labels
Detects `\label{name}` never referenced by `\ref{}`.

## Standalone Compilation Handling

The CLS provides `\chapterref{}` command for smart cross-chapter references:
- **In master book:** Shows "ראה פרק X"
- **In standalone:** Shows "ראה פרק X בספר המלא" or omits reference

## Workflow

1. Run qa-ref-detect (Python-backed)
2. If issues found, delegate to qa-ref-fix
3. Verify references compile
4. Report results to qa-super

## Mission Statement

Ensure all cross-chapter references are valid, properly formatted,
and work correctly in both master and standalone compilation modes.

## Version History
- **v1.0.0** (2025-12-23): Initial creation for cross-chapter reference handling

---

**Parent:** qa-super
**Children:** qa-ref-detect, qa-ref-fix
