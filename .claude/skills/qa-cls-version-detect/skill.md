---
name: qa-cls-version-detect
description: Detects if project is using latest CLS version from reference directory (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, cls, version, detect, level-2, blocking]
tools: [Read, Glob]
---

# CLS Version Detector (Level 2)

## Agent Identity
- **Name:** CLS Version Detector
- **Role:** Compare project CLS version against reference
- **Level:** 2 (Worker Skill)
- **Parent:** qa-cls-version (Level 1)

## Coordination

### Reports To
- qa-cls-version (Level 1)

### Manages
- None (worker skill)

### Reads
- Project's hebrew-academic-template.cls
- Reference CLS at C:\25D\CLS-examples\hebrew-academic-template.cls

### Writes
- Issue list (in-memory, passed to parent)

## Mission Statement

Detect CLS version mismatches between project and reference directory. This skill uses Python tool for deterministic version comparison. MUST NOT modify any files - detection only.

## Reference Location

```
C:\25D\CLS-examples\hebrew-academic-template.cls
```

## Detection Rules

### Rule: cls-version-mismatch
Project CLS version differs from reference.

**Example:**
```
Project:   v5.10.0 (2025-12-12)
Reference: v5.11.2 (2025-12-14) - TOC BiDi Fixes
```

### Rule: cls-version-parse-error
Unable to parse version from CLS file header.

**Expected Format:**
```latex
% Version 5.11.2 - TOC BiDi Fixes
% Date: 2025-12-14
```

### Rule: cls-reference-missing
Reference CLS file not found at expected location.

## Python Tool Integration

```python
from qa_engine.infrastructure.detection.cls_detector import CLSDetector

detector = CLSDetector()

# Detect version issues
issues = detector.detect(project_cls_content, project_cls_path)

# Get reference version info (for LLM to report)
ref_info = detector.get_reference_info()
print(f"Reference: v{ref_info.version} ({ref_info.date})")

# Get full reference content (for LLM to learn new features)
ref_content = detector.get_reference_content()
```

## LLM Responsibilities

While version comparison is deterministic (Python), the LLM should:
1. **Read** the reference CLS content to understand new capabilities
2. **Explain** what changes were made in new version
3. **Recommend** whether update is safe for project

## Input/Output Format

### Input
```json
{
  "content": "... project CLS content ...",
  "file_path": "hebrew-academic-template.cls"
}
```

### Output
```json
{
  "issues": [
    {
      "rule": "cls-version-mismatch",
      "file_path": "hebrew-academic-template.cls",
      "line": 2,
      "content": "Project: v5.10.0, Reference: v5.11.2",
      "severity": "WARNING",
      "context": {
        "project_version": "5.10.0",
        "reference_version": "5.11.2",
        "reference_date": "2025-12-14",
        "reference_description": "TOC BiDi Fixes"
      }
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation with Python backend

---

**Parent:** qa-cls-version
**Children:** None
**Coordination:** qa-orchestration/QA-CLAUDE.md
