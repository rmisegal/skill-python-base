---
name: qa-section-orphan-detect
description: Detect orphan sections with <5 lines content before page break (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, typeset, orphan, section, detection, level-2]
family: typeset
parent: qa-typeset
has_python_tool: true
detection_rules:
  - missing-needspace-section
  - missing-needspace-subsection
  - short-content-after-section
  - section-near-end
---

# Section Orphan Detection Skill (Level 2)

## Agent Identity
- **Name:** Section Orphan Detector
- **Role:** Detect orphan sections in LaTeX documents
- **Level:** 2 (Skill)
- **Parent:** qa-typeset (Level 1)

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic detection.

### Functions
- `detect_in_file(file_path)` - Detect orphan issues in a file
- `detect_in_content(content)` - Detect orphan issues in content string
- `get_rules()` - Get detection rules

### Usage
```python
from tool import detect_in_file, detect_in_content, get_rules

# Get rules
rules = get_rules()

# Detect in file
result = detect_in_file("/path/to/chapter.tex")

# Detect in content
result = detect_in_content(latex_content)
```

## Detection Rules (Python Implementation)

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `missing-needspace-section` | HIGH | Section without `\needspace` protection |
| `missing-needspace-subsection` | MEDIUM | Subsection without protection |
| `short-content-after-section` | LOW | Section with <5 lines before next |

## Orphan Thresholds

| Section Type | Min Lines Required |
|--------------|-------------------|
| `section`, `hebrewsection` | 5 |
| `subsection`, `hebrewsubsection` | 4 |
| `subsubsection` | 3 |

## Output Format

```json
{
  "skill": "qa-section-orphan-detect",
  "status": "DONE",
  "verdict": "WARNING",
  "issues": [
    {
      "rule": "missing-needspace-section",
      "file": "chapter01.tex",
      "line": 45,
      "section_type": "hebrewsection",
      "section_title": "מבנה הפרוטוקול",
      "severity": "HIGH",
      "fix": "Add \\par\\needspace{5\\baselineskip} before line 45"
    }
  ],
  "summary": {
    "sections_checked": 12,
    "sections_protected": 8,
    "sections_unprotected": 4
  },
  "triggers": ["qa-section-orphan-fix"]
}
```

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0**: Initial LLM-only implementation

---

**Parent:** qa-typeset (Level 1)
**Fix skill:** qa-section-orphan-fix
