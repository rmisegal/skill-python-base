---
name: qa-table-fix-captions
description: Fixes caption alignment issues in Hebrew RTL tables (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, table, fix, captions, rtl, hebrew, level-2, python-tool]
---

# qa-table-fix-captions (Level 2)

## Agent Identity
- **Name:** Table Caption Alignment Fixer
- **Role:** Caption alignment correction in RTL documents
- **Level:** 2 (Worker Skill)
- **Parent:** qa-table (Level 1)

## Coordination

### Reports To
- qa-table (Level 1 orchestrator)

### Input
- Issues list from qa-table-detect with caption rules
- LaTeX source content

### Output
- Fixed content with corrected caption alignment
- Fix report with changes made

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Integration

This skill is backed by Python for deterministic fixes:
- **Module:** `src/qa_engine/infrastructure/fixing/caption_fixer.py`
- **Patterns:** `src/qa_engine/infrastructure/fixing/caption_patterns.py`
- **Detection:** `src/qa_engine/infrastructure/detection/table_rules.py`

```python
from qa_engine.infrastructure.fixing.caption_fixer import CaptionFixer

fixer = CaptionFixer()
fixed_content, result = fixer.fix_content(content, file_path)
```

## Fix Patterns

| Pattern ID | Description | Auto |
|------------|-------------|:----:|
| `fix-captionsetup-raggedleft` | Change justification=raggedleft to centering | Yes |
| `fix-captionsetup-simple` | Fix simple captionsetup | Yes |
| `fix-flushleft-caption` | Remove flushleft wrapper, use centering | Yes |
| `fix-table-captionsetup` | Fix table-specific captionsetup | Yes |

## Detection Rules

| Rule ID | Description |
|---------|-------------|
| `caption-setup-raggedleft` | captionsetup with justification=raggedleft |
| `caption-flushleft-wrapped` | Caption wrapped in flushleft environment |
| `caption-table-raggedleft` | Table captionsetup with raggedleft |

## Fix Examples

### Fix captionsetup justification
**Before:**
```latex
\captionsetup{justification=raggedleft}
```

**After:**
```latex
\captionsetup{justification=centering}
```

### Fix flushleft wrapper
**Before:**
```latex
\begin{flushleft}
\caption{Table Title}
\end{flushleft}
```

**After:**
```latex
\centering
\caption{Table Title}
```

## What Python CAN Do (100% Coverage)

- Detect captionsetup with raggedleft
- Detect flushleft-wrapped captions
- Fix justification setting to centering
- Remove flushleft wrapper
- Handle table-specific overrides

## What Requires LLM (0% - None)

All operations are deterministic regex transformations.

## Output Format

```json
{
  "skill": "qa-table-fix-captions",
  "status": "DONE",
  "fixes_applied": 2,
  "changes": [
    {
      "file": "preamble.tex",
      "line": 45,
      "old": "justification=raggedleft",
      "new": "justification=centering"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend

---

**Parent:** qa-table (Level 1)
**Coordination:** qa-orchestration/QA-CLAUDE.md
