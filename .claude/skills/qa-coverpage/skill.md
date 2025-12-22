---
name: qa-coverpage
description: Cover page family orchestrator - source detection then PDF validation (Level 1)
version: 1.1.0
author: QA Team
tags: [qa, coverpage, orchestrator, bidi, pdf, level-1]
---

# qa-coverpage (Level 1)

## Agent Identity
- **Name:** Coverpage Orchestrator
- **Role:** Cover page QA coordination
- **Level:** 1 (Family Orchestrator)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0 orchestrator)

### Manages
- qa-coverpage-detect (Level 2 - source detection)
- PDF validation (LLM - rendered output)

### Reads
- qa_setup.json (coverpage family config)
- LaTeX source files
- Compiled PDF (if available)

### Writes
- Detection reports
- Validation results

## Mission Statement

Orchestrate cover page quality assurance through a two-phase workflow:
1. **Source Detection (Python):** Scan LaTeX source for BiDi issues
2. **PDF Validation (LLM):** Validate rendered output (optional)

## Workflow

### Phase 1: Source Detection (ALWAYS)
```python
from qa_engine.infrastructure.detection.coverpage_detector import CoverpageDetector

detector = CoverpageDetector()
issues = detector.detect(content, file_path)
```

Detects:
- Hebrew metadata BiDi issues
- Unwrapped English/numbers/acronyms
- Date format problems
- Mixed content issues

### Phase 2: PDF Validation (IF PDF EXISTS)

If a compiled PDF is available, validate rendered output:
- Page size (A4)
- Text direction (RTL/LTR)
- Visual layout
- Element positioning

**Note:** PDF validation requires LLM - cannot be automated with Python.

## Family Configuration (qa_setup.json)

```json
{
  "coverpage": {
    "enabled": true,
    "detectors": ["qa-coverpage-detect"],
    "validators": ["qa-coverpage"],
    "workflow": {
      "order": ["qa-coverpage-detect", "qa-coverpage"],
      "note": "Run source detection first, then PDF validation"
    }
  }
}
```

## Detection Rules (Source Level)

| Rule | Description | Auto-Fix |
|------|-------------|:--------:|
| cover-hebrew-title | Hebrew title BiDi | No |
| cover-hebrew-subtitle | Hebrew subtitle BiDi | No |
| cover-hebrew-author | Hebrew author BiDi | No |
| cover-english-in-hebrew | English in Hebrew | Yes |
| cover-numbers-unwrapped | Numbers unwrapped | Yes |
| cover-acronym-unwrapped | Acronyms unwrapped | Yes |
| cover-date-format | Date format check | No |
| cover-copyright-bidi | Copyright BiDi | No |

## PDF Validation Checks (LLM Only)

| Check | Description | Python |
|-------|-------------|:------:|
| Page size | A4 (210mm x 297mm) | No |
| No page number | Cover has no page number | No |
| Image centered | Cover image positioning | No |
| RTL rendering | Hebrew renders RTL | No |
| LTR rendering | English renders LTR | No |
| Element positions | Visual layout | No |

## Output Format

```json
{
  "family": "coverpage",
  "status": "completed",
  "phases": {
    "source_detection": {
      "tool": "CoverpageDetector",
      "issues": 3,
      "rules_triggered": ["cover-english-in-hebrew", "cover-date-format"]
    },
    "pdf_validation": {
      "tool": "LLM",
      "status": "skipped",
      "reason": "No PDF available"
    }
  }
}
```

## Version History
- **v1.1.0** (2025-12-15): Added Python backend integration, workflow definition
- **v1.0.0** (2025-11-28): Initial creation

---

**Parent:** qa-super
**Children:** qa-coverpage-detect
**Coordination:** .claude/QA-CLAUDE.md
