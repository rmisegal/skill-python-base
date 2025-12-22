---
name: qa-cls-sync-detect
description: Detects CLS file content inconsistencies within a project (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, infra, cls, sync, detection, level-2, python-tool]
---

# CLS Sync Detection Skill (Level 2)

## Agent Identity
- **Name:** CLS Sync Detector
- **Role:** Detect CLS file content differences within project
- **Level:** 2 (Worker Skill)
- **Parent:** qa-infra (Level 1)

## Coordination

### Reports To
- qa-infra (Level 1 orchestrator)

### Input
- Project root directory

### Output
- Detection report with file differences

## Problem Statement

LaTeX projects using subfiles often have multiple copies of the CLS file:
- `master/hebrew-academic-template.cls`
- `shared/hebrew-academic-template.cls`
- `standalone-chapterXX/hebrew-academic-template.cls`

These files may have the **same version number** but **different content** due to:
- Manual edits in one location only
- Incomplete sync after updates
- Merge conflicts resolved differently

This skill detects such **internal inconsistencies**.

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** `qa_engine.infrastructure.detection.cls_sync_detector`
- **Class:** `CLSSyncDetector`
- **Rules:** Content-based comparison

### Detection Rules (Python)

| Rule ID | Description | Severity |
|---------|-------------|----------|
| `cls-sync-content-mismatch` | CLS files have different content | CRITICAL |
| `cls-sync-size-mismatch` | CLS files have different sizes | WARNING |
| `cls-sync-no-master` | No master CLS found for reference | CRITICAL |

## Usage

```python
from qa_engine.infrastructure.detection.cls_sync_detector import CLSSyncDetector

detector = CLSSyncDetector()
issues = detector.detect_project("C:/path/to/project")

for issue in issues:
    print(f"{issue.file}: {issue.content}")
```

## Workflow

1. Find all CLS files in master/, shared/, standalone-chapter*/
2. Use master/hebrew-academic-template.cls as reference
3. Compare each CLS file content against reference
4. Report files with differences (line-by-line diff)

## Mission Statement

Detect CLS file content inconsistencies within a project to ensure
all compilation units use identical class definitions.

## Version History
- **v1.0.0** (2025-12-21): Initial creation for internal CLS sync detection
