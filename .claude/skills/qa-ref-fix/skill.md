---
name: qa-ref-fix
description: Fixes cross-chapter reference issues in LaTeX documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, ref, reference, cross-chapter, fix, level-2, python-tool]
family: ref
parent: qa-ref
has_python_tool: true
fix_rules:
  - ref-hardcoded-chapter
  - ref-hardcoded-chapters-range
  - ref-hardcoded-chapters-list
---

# Cross-Reference Fix Skill (Level 2)

## Agent Identity
- **Name:** Cross-Reference Fixer
- **Role:** Fix cross-chapter reference issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-ref (Level 1)

## Coordination

### Reports To
- qa-ref (Level 1 orchestrator)

### Input
- Detection report from qa-ref-detect
- LaTeX source files

### Output
- Fixed content with proper cross-reference commands

## CLS Guard
**IMPORTANT:** Before modifying any .cls file, call `qa-cls-guard` for user approval.

## Python Tool Reference

This skill uses the Python tool at `tool.py` for deterministic fixing.

### Functions
- `fix_in_content(content, issues)` - Fix issues in content string
- `fix_in_file(file_path, issues)` - Fix issues in a file
- `get_fixed_content(content)` - Auto-detect and fix issues

### Usage
```python
from tool import fix_in_content, get_fixed_content

# Fix detected issues
fixed = fix_in_content(content, issues)

# Auto-detect and fix
fixed = get_fixed_content(content)
```

## CLS Commands Used

The fixer converts hardcoded references to these CLS commands:

| Hardcoded Pattern | CLS Command | Standalone Behavior |
|-------------------|-------------|---------------------|
| `ראה פרק \en{2}` | `\chapterref{2}` | Shows "פרק 2 בספר המלא" |
| `פרקים \en{2-3}` | `\chapterrefrange{2}{3}` | Shows range with note |
| `פרקים \en{6, 9}` | `\chapterreflist{6,9}` | Shows list with note |
| `יוסבר בפרק \en{5}` | `\chapterrefforward{5}` | Shows future ref with note |

## Fix Rules

| Rule ID | Fix Action |
|---------|------------|
| `ref-hardcoded-chapter` | Replace with `\chapterref{N}` |
| `ref-hardcoded-chapters-range` | Replace with `\chapterrefrange{N}{M}` |
| `ref-hardcoded-chapters-list` | Replace with `\chapterreflist{N,M,...}` |

## CLS Command Definitions (Required in CLS)

```latex
% Cross-chapter reference commands
% In master book: shows normal reference
% In standalone: shows reference with note about full book

\newcommand{\chapterref}[1]{%
  \ifSubfilesClassLoaded
    {פרק \en{#1} בספר המלא}%
    {פרק~\en{#1}}%
}

\newcommand{\chapterrefrange}[2]{%
  \ifSubfilesClassLoaded
    {פרקים \en{#1--#2} בספר המלא}%
    {פרקים~\en{#1--#2}}%
}

\newcommand{\chapterreflist}[1]{%
  \ifSubfilesClassLoaded
    {פרקים \en{#1} בספר המלא}%
    {פרקים~\en{#1}}%
}

\newcommand{\chapterrefforward}[1]{%
  \ifSubfilesClassLoaded
    {יוסבר בפרק \en{#1} בספר המלא}%
    {יוסבר בפרק~\en{#1}}%
}
```

## Output Format

```json
{
  "skill": "qa-ref-fix",
  "status": "DONE",
  "fixes_applied": 30,
  "files_modified": 8,
  "changes": [
    {
      "file": "chapter06.tex",
      "line": 77,
      "before": "ראה פרק \\en{2}",
      "after": "\\chapterref{2}"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-23): Initial creation

---

**Parent:** qa-ref (Level 1)
**Detect skill:** qa-ref-detect
