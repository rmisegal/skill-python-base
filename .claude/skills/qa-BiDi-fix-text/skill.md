---
name: qa-BiDi-fix-text
description: Fix patterns for text direction issues in Hebrew RTL context (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, bidi, fix, level-2, rtl, hebrew, text]
tools: [Read, Write, Edit]
---

# BiDi Text Fixer (Level 2)

## Agent Identity
- **Name:** BiDi Text Fixer
- **Role:** Apply fixes for bidirectional text issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-BiDi (Level 1)

## Coordination

### Reports To
- qa-BiDi (Level 1)

### Manages
- None (worker skill)

### Reads
- Issue list from qa-BiDi-detect
- .tex file content

### Writes
- Fixed .tex file content

## Mission Statement

Apply fixes for detected bidirectional text issues. This skill MUST NOT perform detection - it operates only on issues provided by the detector.

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Fix Patterns

### Pattern: wrap-number
Wrap standalone numbers with `\en{}`.

**Before:**
```latex
המחיר הוא 99.99 שקלים
```

**After:**
```latex
המחיר הוא \en{99.99} שקלים
```

### Pattern: wrap-english
Wrap English words with `\en{}`.

**Before:**
```latex
זה טקסט test בעברית
```

**After:**
```latex
זה טקסט \en{test} בעברית
```

### Pattern: wrap-acronym
Wrap uppercase acronyms with `\en{}`.

**Before:**
```latex
ראשי תיבות API בעברית
```

**After:**
```latex
ראשי תיבות \en{API} בעברית
```

## Python Tool Integration

```python
from qa_engine.infrastructure.fixing.bidi_fixer import BiDiFixer

fixer = BiDiFixer()
fixed_content = fixer.fix(content, issues)

# Returns fixed content string
# Only fixes issues in the provided list
```

## Input/Output Format

### Input
```json
{
  "content": "...",
  "issues": [
    {
      "rule": "bidi-numbers",
      "line": 42,
      "content": "123"
    }
  ]
}
```

### Output
```json
{
  "fixed_content": "...",
  "fixes_applied": 5,
  "fixes_skipped": 0
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation

---

**Parent:** qa-BiDi
**Children:** None
**Coordination:** qa-orchestration/QA-CLAUDE.md
