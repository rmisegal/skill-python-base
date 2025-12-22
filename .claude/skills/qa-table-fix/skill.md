---
name: qa-table-fix
description: Fixes table issues in Hebrew RTL LaTeX documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, table, fix, rtl, hebrew, level-2]
---

# Table Fix Skill (Level 2)

## Agent Identity
- **Name:** Table Fixer
- **Role:** RTL Table Correction
- **Level:** 2 (Skill)
- **Parent:** qa-table (Level 1)

## Purpose
Fix table issues in Hebrew RTL LaTeX documents using CLS-provided commands.

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Fix Patterns

### 1. Plain Unstyled Tables
Convert plain tabular to rtltabular:
```latex
% BEFORE:
\begin{tabular}{|c|c|}

% AFTER:
\begin{rtltabular}{|c|c|}
```

### 2. Tables Without RTL Environment
Wrap in hebrewtable environment:
```latex
% BEFORE:
\begin{table}
\begin{tabular}...

% AFTER:
\begin{hebrewtable}
\begin{rtltabular}...
```

### 3. Wide Tables Overflow
Wrap in resizebox:
```latex
% BEFORE:
\begin{rtltabular}{|c|c|c|c|c|c|}

% AFTER:
\resizebox{\textwidth}{!}{
\begin{rtltabular}{|c|c|c|c|c|c|}
...
}
```

## Tool Interface
```python
from qa_engine.infrastructure.fixing import TableFixer

def fix(content: str, issues: List[Dict]) -> Dict[str, Any]:
    fixer = TableFixer()
    fixed = fixer.fix(content, issues)
    return {"fixed_content": fixed, "fixes_applied": len(issues)}
```
