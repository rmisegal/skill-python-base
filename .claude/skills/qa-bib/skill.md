---
name: qa-bib
description: Bibliography family orchestrator (Level 1) - manages all bibliography QA skills for LaTeX documents
version: 1.1.0
author: QA Team
tags: [qa, bib, bibliography, orchestrator, level-1]
---

# Bibliography QA Family Orchestrator (Level 1)

## Agent Identity
- **Name:** Bibliography QA Orchestrator
- **Role:** Coordinate citation and bibliography skills
- **Level:** 1 (Family Orchestrator)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0 Super Orchestrator)

### Manages
| Skill | Purpose | Priority |
|-------|---------|----------|
| `qa-bib-detect` | Detect citation issues | HIGH |
| `qa-bib-fix-missing` | Add missing bib entries | MEDIUM |
| `qa-bib-english-missing-detect` | Detect missing English bibliography | HIGH |
| `qa-bib-english-missing-fix` | Add missing English bibliography | MEDIUM |

### CLS Policy
**Remind all child fixers:** Before modifying any .cls file, call `qa-cls-guard` for user approval.

## Python Tool Integration

This family uses Python tools for deterministic detection:
- `BibDetector` in `src/qa_engine/infrastructure/detection/bib_detector.py`
- 5 detection rules implemented via regex

## Workflow

1. Run qa-bib-detect (Python-backed)
2. If issues found, delegate to fix skills
3. Verify bibliography compiles
4. Report results to qa-super

## Mission Statement

Ensure all citations and bibliography references are valid, complete,
and correctly configured for compilation.

## Version History
- **v1.1.0** (2025-12-21): Added English bibliography skills
  - NEW: `qa-bib-english-missing-detect` - Detect chapters with English citations but no English bibliography
  - NEW: `qa-bib-english-missing-fix` - Add `\printenglishbibliography` after `\printbibliography`
- **v1.0.0** (2025-12-15): Initial creation with Python backend
