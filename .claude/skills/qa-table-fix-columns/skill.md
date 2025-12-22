---
name: qa-table-fix-columns
description: Fixes column order issues in Hebrew RTL tables (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, table, fix, columns, rtl, hebrew, level-2]
family: table
parent: qa-table
has_python_tool: true
---

# Table Column Fix Skill (Level 2)

## Agent Identity
- **Name:** Table Column Order Fixer
- **Role:** RTL Column Order Correction
- **Level:** 2 (Skill)
- **Parent:** qa-table (Level 1)

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic fixes.

### Functions
- `fix_content(content, file_path)` - Fix column order in content string
- `fix_file(file_path)` - Fix column order in a file

### Usage
```python
from tool import fix_content, fix_file

# Fix in content
fixed_content, result = fix_content(latex_content)

# Fix specific file
result = fix_file("/path/to/chapter.tex")
```

## Fix Logic (Python Implementation)

1. **Detect table environments** - Match `\begin{tabular}` or `\begin{rtltabular}`
2. **Parse rows** - Split by `&` delimiter
3. **Reverse column order** - `reversed(parts)`
4. **Preserve structure** - Keep `\\`, `\hline`, whitespace

## Key Rules

- LaTeX processes columns left-to-right in source
- For RTL display, columns must be in REVERSE order
- Visual rightmost column = First column in LaTeX
- Do NOT change column spec (|c|c|c|), only content order

## Output Format

```json
{
  "skill": "qa-table-fix-columns",
  "status": "DONE",
  "tables_fixed": 2,
  "changes": [
    {
      "table": 1,
      "file": "chapter02.tex",
      "line": 145,
      "action": "reversed column order"
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
