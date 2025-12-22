---
name: qa-heb-math-detect
description: Detects Hebrew text inside math mode that renders LTR instead of RTL (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, bidi, math, hebrew, detection, level-2, hebmath]
family: BiDi
parent: qa-BiDi
has_python_tool: true
detection_rules:
  - heb-math-text
  - heb-math-textbf
  - heb-math-subscript
  - heb-math-superscript
  - heb-math-cases
  - heb-math-definition
---

# Hebrew in Math Detection Agent (Level 2)

## Agent Identity
- **Name:** Hebrew Math Detection Agent
- **Role:** Detect Hebrew text in math mode rendering incorrectly
- **Level:** 2 (Skill)
- **Parent:** qa-BiDi (Level 1)

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic detection.

### Functions
- `detect(content, file_path, offset)` - Run detection, returns list of issues
- `get_rules()` - Get dict of rule names and descriptions

### Usage
```python
from tool import detect, get_rules

# Get supported rules
rules = get_rules()

# Run detection
issues = detect(content, "file.tex")
```

## Detection Rules (Python Implementation)

| Rule ID | Description |
|---------|-------------|
| `heb-math-text` | Hebrew in `\text{}` without `\hebmath{}` |
| `heb-math-textbf` | Hebrew in `\textbf{}/\textit{}` in math |
| `heb-math-subscript` | Hebrew in subscript without wrapper |
| `heb-math-superscript` | Hebrew in superscript without wrapper |
| `heb-math-cases` | Hebrew in cases environment without wrapper |
| `heb-math-definition` | Incorrect `\hebmath{}` definition |

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0** (2025-12-02): Initial LLM-only implementation

---

**Parent:** qa-BiDi (Level 1)
**Sibling:** qa-heb-math-fix
