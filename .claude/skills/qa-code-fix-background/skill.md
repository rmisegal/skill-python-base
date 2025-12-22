---
name: qa-code-fix-background
description: Fixes code block background overflow by wrapping in english environment (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, code, fix, level-2, background, pythonbox]
tools: [Read, Write, Edit]
---

# Code Background Fixer (Level 2)

## Agent Identity
- **Name:** Code Background Fixer
- **Role:** Fix code block background overflow issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-code (Level 1)

## Coordination

### Reports To
- qa-code (Level 1)

### Manages
- None (worker skill)

### Reads
- Issue list from qa-code-detect
- .tex file content

### Writes
- Fixed .tex file content

## Mission Statement

Fix code block background overflow by wrapping pythonbox environments in english environment. This skill MUST NOT perform detection.

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Fix Patterns

### Pattern: wrap-pythonbox
Wrap pythonbox in english environment.

**Before:**
```latex
\begin{pythonbox}
print("hello")
\end{pythonbox}
```

**After:**
```latex
\begin{english}
\begin{pythonbox}
print("hello")
\end{pythonbox}
\end{english}
```

## Python Tool Integration

```python
from qa_engine.infrastructure.fixing.code_fixer import CodeFixer

fixer = CodeFixer()
fixed_content = fixer.fix(content, issues)
```

## Input/Output Format

### Input
```json
{
  "content": "...",
  "issues": [{"rule": "code-background-overflow", "line": 100}]
}
```

### Output
```json
{
  "fixed_content": "...",
  "fixes_applied": 3
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation

---

**Parent:** qa-code
**Children:** None
**Coordination:** qa-orchestration/QA-CLAUDE.md
