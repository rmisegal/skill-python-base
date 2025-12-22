---
name: qa-coverpage-detect
description: Detects cover page metadata issues at source level (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, coverpage, detection, bidi, level-2, python-tool]
---

# qa-coverpage-detect (Level 2)

## Agent Identity
- **Name:** Coverpage Detector
- **Role:** Source-level cover page metadata detection
- **Level:** 2 (Worker Skill)
- **Parent:** qa-coverpage (Level 1)

## Coordination

### Reports To
- qa-coverpage (Level 1 orchestrator)

### Input
- LaTeX source files (preamble and first 100 lines)

### Output
- Detection report with issue locations

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** `src/qa_engine/infrastructure/detection/coverpage_detector.py`
- **Rules:** 8 rules defined in `coverpage_rules.py`

```python
from qa_engine.infrastructure.detection.coverpage_detector import CoverpageDetector

detector = CoverpageDetector()
issues = detector.detect(content, file_path)
```

## Detection Rules

| Rule ID | Description | Python |
|---------|-------------|:------:|
| `cover-hebrew-title` | Hebrew title without RTL wrapper | Yes |
| `cover-hebrew-subtitle` | Hebrew subtitle BiDi issues | Yes |
| `cover-hebrew-author` | Hebrew author BiDi issues | Yes |
| `cover-english-in-hebrew` | English in Hebrew metadata without \en{} | Yes |
| `cover-numbers-unwrapped` | Numbers in Hebrew metadata unwrapped | Yes |
| `cover-acronym-unwrapped` | Acronyms in Hebrew metadata unwrapped | Yes |
| `cover-date-format` | Date not in DD-MM-YYYY format | Yes |
| `cover-copyright-bidi` | Copyright line BiDi issues | Yes |

## Mission Statement

Detect cover page metadata issues at the LaTeX source level before compilation.
This is the first step in the coverpage QA workflow - source-level detection
catches issues early, before PDF compilation.

## Workflow Position

```
┌─────────────────────────────────────────────────────┐
│  1. qa-coverpage-detect (THIS SKILL)                │
│     - Scans LaTeX source                            │
│     - Detects BiDi issues in metadata commands      │
│     - Python-based (deterministic)                  │
│     - Runs BEFORE compilation                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  2. qa-coverpage (PDF Validation)                   │
│     - Validates rendered PDF output                 │
│     - Checks visual layout                          │
│     - LLM-based (requires PDF parsing)              │
│     - Runs AFTER compilation                        │
└─────────────────────────────────────────────────────┘
```

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend
