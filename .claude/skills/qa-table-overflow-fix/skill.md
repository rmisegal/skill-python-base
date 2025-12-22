---
name: qa-table-overflow-fix
description: Fix patterns for wide tables causing overfull hbox - wrap with resizebox (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, typeset, fix, table, overflow, resizebox, level-2]
family: typeset
parent: qa-typeset
has_python_tool: true
---

# Table Overflow Fix (Level 2)

## Agent Identity
- **Name:** Table Overflow Fixer
- **Role:** Wide Table Width Correction
- **Level:** 2 (Skill)
- **Parent:** qa-typeset (Level 1)

## Purpose
Fix wide tables that overflow text width by wrapping with `\resizebox{\textwidth}{!}{}`.

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool
This skill has a Python implementation in `tool.py` that provides:
- `fix_content(content, file_path, issues)` - Fix overflow issues in content
- `fix_file(file_path)` - Fix overflow issues in a file

## Fix Pattern

### Before (Unsafe)
```latex
\begin{rtltabular}{|c|c|c|c|c|}
\hline
... table content ...
\hline
\end{rtltabular}
```

### After (Safe)
```latex
\resizebox{\textwidth}{!}{%
\begin{rtltabular}{|c|c|c|c|c|}
\hline
... table content ...
\hline
\end{rtltabular}%
}
```

## Output Format
```json
{
  "skill": "qa-table-overflow-fix",
  "status": "DONE",
  "tables_fixed": 1,
  "changes": [
    {"table": 1, "file": "chapter.tex", "line": 15, "action": "wrapped with resizebox"}
  ]
}
```
