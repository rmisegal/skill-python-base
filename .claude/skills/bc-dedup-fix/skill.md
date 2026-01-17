---
name: bc-dedup-fix
description: Level 2 Worker - Applies chapterref fixes to duplicate content
version: 1.0.0
author: BC Team
tags: [bc, worker, level-2, dedup, fixer, python-tool]
parent: bc-dedup
has_python_tool: true
tools: [Read, Write, Edit]
---

# BC Dedup Fix - ChapterRef Fixer (Level 2)

## Agent Identity
- **Name:** Dedup Fixer
- **Role:** Apply chapterref fixes to duplicate content
- **Level:** 2 (Worker)
- **Parent:** bc-dedup

## Coordination

### Reports To
- bc-dedup (Level 1)

### Manages
- None (leaf worker)

## Mission Statement

Apply natural-language fixes to duplicate content by replacing repeated explanations with `\chapterref{}` references. Ensure fixes maintain:
1. Natural reading flow
2. Proper RTL/LTR directionality
3. Grammatically correct Hebrew

## Fix Patterns

| Pattern | Find | Replace |
|---------|------|---------|
| `dedup-chapterref` | Duplicate content | `\chapterref{chapterN}` |
| `dedup-see-reference` | Repeated explanation | `(ראה \chapterref{chapterN})` |

## Workflow

1. Receive list of DedupIssues from detector
2. Group issues by target file
3. For each file:
   a. Load content
   b. Apply fixes in reverse line order (to preserve line numbers)
   c. Write fixed content
4. Validate with BCBiDiValidator

## Python Tool Integration

```python
from bc_engine.dedup.fixer import DedupFixer

fixer = DedupFixer(config_path="config/bc_dedup.json")

# Apply fixes to content
fixed_content = fixer.fix(original_content, issues)

# Get supported patterns
patterns = fixer.get_patterns()
```

## Input/Output Format

### Input
```json
{
  "content": "LaTeX content with duplicates...",
  "issues": [
    {
      "rule": "dedup-semantic-duplicate",
      "file": "chapters/chapter5.tex",
      "line": 42,
      "content": "Neural networks process...",
      "source_chapter": 2,
      "target_chapter": 5,
      "fix": "\\chapterref{chapter2}"
    }
  ]
}
```

### Output
```json
{
  "fixed_content": "LaTeX content with references...",
  "fixes_applied": 3
}
```

## LLM Rewriting (Optional)

When LLM callback is provided, the fixer can generate natural-language rewrites:

**Before:**
```latex
רשתות נוירונים מעבדות מידע בשכבות.
כל שכבה מקבלת קלט ומייצרת פלט.
```

**After (with LLM):**
```latex
כפי שהוסבר ב\chapterref{chapter2}, רשתות נוירונים
מעבדות מידע בשכבות.
```

## QA Integration

Fixes are validated by:
- **BCBiDiValidator**: Ensures references maintain RTL direction
- **BCTOCValidator**: Ensures chapter references are valid

## Version History
- **v1.0.0** (2025-12-24): Initial implementation

---

**Parent:** bc-dedup
**Interface:** FixerInterface
