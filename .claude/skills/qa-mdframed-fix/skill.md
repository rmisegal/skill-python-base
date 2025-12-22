---
name: qa-mdframed-fix
description: Fix patterns for mdframed page break issues - adds spacing and page break control (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, typeset, mdframed, pagebreak, fix, level-2]
family: typeset
parent: qa-typeset
has_python_tool: true
fix_strategies:
  - vspace
  - nopagebreak
  - combined
  - clearpage
---

# mdframed Page Break Fix Skill (Level 2)

## Agent Identity
- **Name:** mdframed Page Break Fixer
- **Role:** Fix bad page breaks in mdframed environments
- **Level:** 2 (Skill)
- **Parent:** qa-typeset (Level 1)

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic fixes.

### Functions
- `fix_file(file_path, line_numbers)` - Fix mdframed issues in file
- `fix_content(content, line_numbers)` - Fix mdframed issues in content string
- `get_strategies()` - Get available fix strategies

### Usage
```python
from tool import fix_file, fix_content, get_strategies

# Get available strategies
strategies = get_strategies()

# Fix specific lines in file
result = fix_file("/path/to/chapter.tex", [227, 315])

# Fix content string (for testing)
fixed_content, result = fix_content(latex_content)
```

## Fix Strategies (Python Implementation)

| Strategy | Command | When to Use |
|----------|---------|-------------|
| `vspace` | `\vspace{1em}` | Default, first box in section |
| `vspace_long` | `\vspace{1.5em}` | After long paragraph |
| `nopagebreak` | `\nopagebreak` | Box immediately after heading |
| `combined` | Both vspace + nopagebreak | Stubborn breaks |
| `clearpage` | `\clearpage` | Last resort, new section |

## Output Format

```json
{
  "skill": "qa-mdframed-fix",
  "status": "DONE",
  "fixes_applied": [
    {
      "file": "chapters/chapter02.tex",
      "line": 227,
      "before": "\\begin{dobox}[...",
      "after": "\\vspace{1em}\\n\\begin{dobox}[...",
      "strategy": "vspace",
      "verified": true
    }
  ],
  "summary": {
    "files_modified": 1,
    "fixes_applied": 1,
    "warnings_eliminated": 1
  },
  "qa_report_updated": true
}
```

## Version History
- **v1.1.0** (2025-12-15): Python tool implementation
- **v1.0.0** (2025-12-02): Initial LLM-only implementation

---

**Parent:** qa-typeset (Level 1)
**Sibling:** qa-mdframed-detect
