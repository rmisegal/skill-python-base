---
name: qa-typeset-detect
description: Detects LaTeX compilation warnings by parsing .log files (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, typeset, detect, level-2, latex, warnings, log]
tools: [Read, Grep, Glob]
---

# Typeset Detector (Level 2)

## Agent Identity
- **Name:** Typeset Warning Detector
- **Role:** Detect LaTeX compilation warnings
- **Level:** 2 (Worker Skill)
- **Parent:** qa-typeset (Level 1)

## Coordination

### Reports To
- qa-typeset (Level 1)

### Manages
- None (worker skill)

### Reads
- .log files from LaTeX compilation

### Writes
- Issue list (in-memory, passed to parent)

## Mission Statement

Parse LaTeX .log files to detect compilation warnings. This skill MUST NOT modify any files - detection only.

## Detection Rules

### Rule: typeset-overfull-hbox
Overfull hbox warnings indicating content too wide.

**Log Pattern:**
```
Overfull \hbox (12.34567pt too wide) in paragraph at lines 42--45
```

### Rule: typeset-underfull-hbox
Underfull hbox warnings indicating loose spacing.

**Log Pattern:**
```
Underfull \hbox (badness 10000) in paragraph at lines 42--45
```

### Rule: typeset-overfull-vbox
Overfull vbox warnings indicating content too tall.

**Log Pattern:**
```
Overfull \vbox (12.34567pt too high) has occurred while \output is active
```

### Rule: typeset-undefined-ref
Undefined reference or citation warnings.

**Log Pattern:**
```
LaTeX Warning: Reference `fig:example' on page 5 undefined
LaTeX Warning: Citation `smith2020' on page 10 undefined
```

### Rule: typeset-float-large
Float too large for page warnings.

**Log Pattern:**
```
LaTeX Warning: Float too large for page by 12.34567pt
```

## Python Tool Integration

```python
from qa_engine.infrastructure.detection.typeset_detector import TypesetDetector

detector = TypesetDetector()
issues = detector.detect(log_content, log_file_path)

# Returns List[Issue]
```

## Input/Output Format

### Input
```json
{
  "content": "... .log file content ...",
  "file_path": "main.log"
}
```

### Output
```json
{
  "issues": [
    {
      "rule": "typeset-overfull-hbox",
      "file_path": "main.log",
      "line": 42,
      "content": "12.34567pt too wide",
      "severity": "WARNING"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation

---

**Parent:** qa-typeset
**Children:** None
**Coordination:** qa-orchestration/QA-CLAUDE.md
