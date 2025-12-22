---
name: qa-img-detect
description: Detects image issues at source level (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, img, detection, figures, images, level-2, python-tool]
---

# qa-img-detect (Level 2)

## Agent Identity
- **Name:** Image Detector
- **Role:** Source-level image issue detection
- **Level:** 2 (Worker Skill)
- **Parent:** qa-img (Level 1)

## Coordination

### Reports To
- qa-img (Level 1 orchestrator)

### Input
- LaTeX source files
- Project root path (for file existence checks)

### Output
- Detection report with issue locations

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** `src/qa_engine/infrastructure/detection/image_detector.py`
- **Rules:** 8 rules defined in `image_rules.py`

```python
from qa_engine.infrastructure.detection.image_detector import ImageDetector

detector = ImageDetector(project_root=Path("."))
issues = detector.detect(content, file_path)
```

## Detection Rules

| Rule ID | Description | Python |
|---------|-------------|:------:|
| `img-file-not-found` | Image file not found on disk | Yes |
| `img-no-graphicspath` | No graphicspath configuration | Yes |
| `img-wrong-extension` | File extension mismatch | Yes |
| `img-case-mismatch` | Filename case mismatch | Yes |
| `img-placeholder-box` | Placeholder instead of image | Yes |
| `img-empty-figure` | Empty figure environment | Yes |
| `img-hebrew-figure-empty` | hebrewfigure without image | Yes |
| `img-no-size-spec` | Missing width/height spec | Yes |

## What Python CAN Do (Source Level)

- Detect `\includegraphics` commands
- Check if image files exist on disk
- Validate file extensions
- Detect placeholder boxes
- Check graphicspath configuration

## What Requires LLM (PDF Level)

- Verify image renders in compiled PDF
- Detect empty boxes visually
- Compare List of Figures with pages
- Visual layout validation

## Mission Statement

Detect image-related issues at the LaTeX source level before compilation.
This enables early detection of missing files and path problems.

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend
