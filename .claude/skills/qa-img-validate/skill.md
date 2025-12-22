---
name: qa-img-validate
description: Validates all images render correctly after fixes (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, img, validate, verify, level-2]
family: img
parent: qa-img
has_python_tool: true
---

# Image Validation Skill (Level 2)

## Agent Identity
- **Name:** Image Validator
- **Role:** Post-Fix Verification
- **Level:** 2 (Skill)
- **Parent:** qa-img (Level 1)

## Purpose
Verify all previously missing images now render correctly after fixes have been applied.

## Python Tool
This skill has a Python implementation in `tool.py` that provides:
- `validate_content(content, before_issues, source_dir)` - Full validation
- `validate_after_fixes(content, source_dir)` - Check current state
- `record_before_state(issues)` - Record initial issues

## Validation Process

### Source-Level (Python)
1. Check image files exist after creation
2. Verify `\includegraphics` paths resolve
3. Compare before/after issue counts

### PDF-Level (LLM Required)
1. Visual verification of rendered images
2. Empty box detection in PDF
3. Verify captions match images

## Output Format
```json
{
  "skill": "qa-img-validate",
  "status": "DONE",
  "verdict": "PASS",
  "figures_verified": 5,
  "all_rendered": true,
  "comparison": [
    {"figure": 1, "before": "MISSING", "after": "RENDERED"}
  ],
  "still_missing": []
}
```

## Verdict Criteria
- **PASS**: All figures verified, no missing images
- **FAIL**: Some images still missing after fixes
