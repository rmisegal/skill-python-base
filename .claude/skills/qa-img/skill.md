---
name: qa-img
description: Image family orchestrator - source detection and PDF validation (Level 1)
version: 2.1.0
author: QA Team
tags: [qa, img, orchestrator, figures, images, level-1, python-tool]
has_python_tool: true
---

# qa-img (Level 1)

## Agent Identity
- **Name:** Image Family Orchestrator
- **Role:** Image QA pipeline coordination
- **Level:** 1 (Family Orchestrator)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0 orchestrator)

### Manages
- qa-img-detect (Level 2 - source detection, Python)
- qa-img-fix-paths (Level 2 - path fixing, Python)
- qa-img-validate (Level 2 - PDF validation, LLM)

### Reads
- qa_setup.json (img family config)
- LaTeX source files

### Writes
- Detection reports
- Fix reports

### CLS Policy
**Remind all child fixers:** Before modifying any .cls file, call `qa-cls-guard` for user approval.

## Python Tool Integration

Source-level operations use Python backend:

```python
from qa_engine.infrastructure.detection.image_detector import ImageDetector
from qa_engine.infrastructure.fixing.image_fixer import ImageFixer

# Detection
detector = ImageDetector(project_root)
issues = detector.detect(content, file_path)

# Fixing
fixer = ImageFixer()
fixed = fixer.fix(content, issues)
```

## Workflow

### Phase 1: Source Detection (Python - ALWAYS)
```
qa-img-detect
├── Check \includegraphics commands
├── Verify image files exist
├── Detect path/extension issues
└── Report source-level issues
```

### Phase 2: Source Fixing (Python - IF NEEDED)
```
qa-img-fix-paths (parallel capable)
├── Add graphicspath config
├── Fix relative paths
└── Fix extensions/case
```

### Phase 3: PDF Validation (LLM - OPTIONAL)
```
qa-img-validate
├── Extract List of Figures
├── Verify images render
└── Generate PASS/FAIL
```

## Family Configuration (qa_setup.json)

```json
{
  "img": {
    "enabled": true,
    "detectors": ["qa-img-detect"],
    "fixers": ["qa-img-fix-paths"],
    "validators": ["qa-img-validate"],
    "workflow": {
      "order": ["qa-img-detect", "qa-img-fix-paths", "qa-img-validate"]
    }
  }
}
```

## Detection Rules

| Rule | Description | Python | LLM |
|------|-------------|:------:|:---:|
| img-file-not-found | File not on disk | Yes | - |
| img-no-graphicspath | Missing config | Yes | - |
| img-wrong-extension | Extension mismatch | Yes | - |
| img-case-mismatch | Case mismatch | Yes | - |
| img-placeholder-box | Placeholder box | Yes | - |
| img-empty-figure | Empty figure | Yes | - |
| Image renders in PDF | Visual check | - | Yes |
| Empty box in PDF | Visual check | - | Yes |

## Implementation Status

| Component | Python | Status |
|-----------|:------:|--------|
| ImageDetector | Yes | Implemented |
| ImageFixer | Yes | Implemented |
| image_rules.py | Yes | 8 rules |
| image_patterns.py | Yes | 6 patterns |
| PDF Validation | No | LLM only |

## Output Format

```json
{
  "family": "img",
  "status": "completed",
  "phases": {
    "source_detection": {
      "tool": "ImageDetector",
      "issues": 3
    },
    "source_fixing": {
      "tool": "ImageFixer",
      "fixes_applied": 2
    },
    "pdf_validation": {
      "tool": "LLM",
      "status": "skipped"
    }
  }
}
```

## Version History
- **v2.0.0** (2025-12-15): Added Python backend for source-level operations
- **v1.0.0** (2025-11-28): Initial creation (LLM only)

---

**Parent:** qa-super
**Children:** qa-img-detect, qa-img-fix-paths, qa-img-validate
**Coordination:** .claude/QA-CLAUDE.md
