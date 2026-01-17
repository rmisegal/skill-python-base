---
name: qa-ref-detect
description: Detects cross-chapter reference issues in LaTeX documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, ref, reference, cross-chapter, detection, level-2, python-tool]
family: ref
parent: qa-ref
has_python_tool: true
detection_rules:
  - ref-hardcoded-chapter
  - ref-hardcoded-chapters-range
  - ref-hardcoded-chapters-list
  - ref-undefined-label
  - ref-orphan-label
  - ref-standalone-unsafe
---

# Cross-Reference Detection Skill (Level 2)

## Agent Identity
- **Name:** Cross-Reference Detector
- **Role:** Detect cross-chapter reference issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-ref (Level 1)

## Coordination

### Reports To
- qa-ref (Level 1 orchestrator)

### Input
- LaTeX source files from parent

### Output
- Detection report with issue locations

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic detection.

### Functions
- `detect_in_file(file_path)` - Detect reference issues in a file
- `detect_in_content(content, file_path)` - Detect issues in content string
- `detect_in_project(project_path)` - Detect issues across all chapters
- `get_rules()` - Get detection rules

### Usage
```python
from tool import detect_in_file, detect_in_project, get_rules

# Get rules
rules = get_rules()

# Detect in single file
result = detect_in_file("/path/to/chapter.tex")

# Detect in project (cross-file analysis)
result = detect_in_project("/path/to/book")
```

## Detection Rules (Python Implementation)

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `ref-hardcoded-chapter` | HIGH | Hardcoded "ראה פרק \en{X}" instead of `\chapterref{X}` |
| `ref-hardcoded-chapters-range` | HIGH | Hardcoded "פרקים \en{X-Y}" chapter range |
| `ref-hardcoded-chapters-list` | HIGH | Hardcoded "פרקים \en{X, Y}" chapter list |
| `ref-undefined-label` | CRITICAL | `\ref{label}` points to undefined label |
| `ref-orphan-label` | LOW | `\label{name}` never referenced |
| `ref-standalone-unsafe` | MEDIUM | Reference breaks in standalone mode |

## Patterns Detected

### Hardcoded Cross-Chapter References
```latex
% DETECTED - should use \chapterref{}
ראה פרק \en{2}
ראה פרקים \en{2-3}
ראה פרקים \en{6, 9}
(ראה פרק \en{10} לפירוט)
יוסבר בפרק \en{5}
```

### Undefined References
```latex
\ref{sec:nonexistent}  % Label doesn't exist
```

### Orphan Labels
```latex
\label{fig:unused}  % Never referenced
```

## Standalone Mode Detection

When a chapter file is compiled standalone, cross-chapter references fail.
This skill detects references that will break:

1. **Direct chapter numbers:** `ראה פרק \en{5}` - breaks if chapter 5 not included
2. **Cross-file \ref:** `\ref{chap:intro}` - breaks if label in different chapter

## Output Format

```json
{
  "skill": "qa-ref-detect",
  "status": "DONE",
  "verdict": "WARNING",
  "issues": [
    {
      "rule": "ref-hardcoded-chapter",
      "file": "chapter06.tex",
      "line": 77,
      "content": "ראה פרק \\en{2}",
      "severity": "HIGH",
      "fix": "Use \\chapterref{2} instead"
    }
  ],
  "summary": {
    "files_checked": 12,
    "total_references": 45,
    "hardcoded_refs": 30,
    "undefined_refs": 0,
    "orphan_labels": 5
  },
  "triggers": ["qa-ref-fix"]
}
```

## Version History
- **v1.0.0** (2025-12-23): Initial creation with Python backend

---

**Parent:** qa-ref (Level 1)
**Fix skill:** qa-ref-fix
