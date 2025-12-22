---
name: qa-table-fix-alignment
description: Fixes cell alignment issues in Hebrew RTL tables (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, table, fix, alignment, rtl, hebrew, level-2]
family: table
parent: qa-table
has_python_tool: true
fix_commands:
  - hebcell
  - encell
  - hebheader
  - enheader
---

# Table Cell Alignment Fix Skill (Level 2)

## Agent Identity
- **Name:** Table Cell Alignment Fixer
- **Role:** Cell Content Alignment Correction
- **Level:** 2 (Skill)
- **Parent:** qa-table (Level 1)

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic fixes.

### Functions
- `fix_content(content, issues)` - Fix alignment issues in content string
- `fix_file(file_path, issues)` - Fix alignment issues in a file

### Usage
```python
from tool import fix_content, fix_file

# Fix in content
fixed_content, result = fix_content(latex_content)

# Fix specific file
result = fix_file("/path/to/chapter.tex")
```

## Fix Commands (Python Implementation)

| Command | Purpose | When Applied |
|---------|---------|--------------|
| `\hebcell{}` | Hebrew cell content | Hebrew text in data cell |
| `\encell{}` | English cell content | English text in data cell |
| `\hebheader{}` | Hebrew header cell | Hebrew text in header row |
| `\enheader{}` | English header cell | English text in header row |

## Fix Logic

1. **Hebrew Content Detection**: Uses Unicode range `\u0590-\u05FF`
2. **Header Row Detection**: First row or row after `\hline`
3. **Mixed Content**: Hebrew cells with English parts get `\hebcell{...\en{English}...}`

## Output Format

```json
{
  "skill": "qa-table-fix-alignment",
  "status": "DONE",
  "cells_fixed": 5,
  "changes": [
    {
      "table": 1,
      "cell": "row2-col1",
      "old": "plain text",
      "new": "\\hebcell{plain text}",
      "fix_type": "hebcell"
    }
  ]
}
```

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0**: Initial LLM-only implementation

---

**Parent:** qa-table (Level 1)
**Detection skill:** qa-table-detect
