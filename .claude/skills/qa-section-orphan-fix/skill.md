---
name: qa-section-orphan-fix
description: Fixes section orphan issues by adding needspace protection (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, typeset, orphan, section, fix, level-2]
family: typeset
parent: qa-typeset
has_python_tool: true
fix_strategies:
  - needspace
  - clearpage
---

# Section Orphan Fix Skill (Level 2)

## Agent Identity
- **Name:** Section Orphan Fixer
- **Role:** Fix orphan sections in LaTeX documents
- **Level:** 2 (Skill)
- **Parent:** qa-typeset (Level 1)

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic fixes.

### Functions
- `fix_file(file_path, line_numbers)` - Fix orphan issues in a file
- `fix_content(content, line_numbers)` - Fix orphan issues in content string

### Usage
```python
from tool import fix_file, fix_content

# Fix specific file
result = fix_file("/path/to/chapter.tex")

# Fix in content
fixed_content, result = fix_content(latex_content)

# Fix specific lines only
result = fix_file("/path/to/chapter.tex", line_numbers=[45, 72, 103])
```

## Fix Strategies (Python Implementation)

| Strategy | Description | When Used |
|----------|-------------|-----------|
| `needspace` | Add `\par\needspace{X\baselineskip}` | Default for all sections |
| `clearpage` | Force page break | Last resort for persistent issues |

## Threshold Values

| Section Type | Baselineskip Value |
|--------------|-------------------|
| `section`, `hebrewsection` | 5 |
| `subsection`, `hebrewsubsection` | 4 |
| `subsubsection` | 3 |

## Output Format

```json
{
  "skill": "qa-section-orphan-fix",
  "status": "DONE",
  "fixes_applied": [
    {
      "file": "chapter01.tex",
      "line": 45,
      "section_type": "hebrewsection",
      "section_title": "מבנה הפרוטוקול",
      "fix_type": "needspace",
      "threshold": 5,
      "before": "\\hebrewsection{מבנה הפרוטוקול}",
      "after": "\\par\\needspace{5\\baselineskip}\\n\\hebrewsection..."
    }
  ],
  "summary": {
    "files_modified": 1,
    "fixes_applied": 3,
    "sections_protected": 3
  }
}
```

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0**: Initial LLM-only implementation

---

**Parent:** qa-typeset (Level 1)
**Detection skill:** qa-section-orphan-detect
