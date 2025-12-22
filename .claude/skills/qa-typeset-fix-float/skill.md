---
name: qa-typeset-fix-float
description: Fix patterns for Float too large warnings (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, typeset, fix, float, too-large, level-2, python-tool, hybrid]
---

# qa-typeset-fix-float (Level 2)

## Agent Identity
- **Name:** Float Warning Fixer
- **Role:** Oversized float correction in LaTeX documents
- **Level:** 2 (Worker Skill)
- **Parent:** qa-typeset (Level 1)

## Coordination

### Reports To
- qa-typeset (Level 1 orchestrator)

### Input
- Issues list from TypesetDetector with `typeset-float-too-large` rule
- LaTeX source content
- Overflow amount in points (from log)

### Output
- Fixed content with float adjustments
- Fix report with changes made
- LLM guidance for complex fixes

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Integration

This skill uses a **hybrid approach**:
- **Python (`FloatFixer`)**: Deterministic pattern fixes
- **LLM**: Context-dependent decisions (code splitting)

### Python Components
- **Fixer:** `src/qa_engine/infrastructure/fixing/float_fixer.py`
- **Patterns:** `src/qa_engine/infrastructure/fixing/float_patterns.py`
- **Detection:** `src/qa_engine/infrastructure/detection/typeset_detector.py`

```python
from qa_engine.infrastructure.fixing.float_fixer import FloatFixer
from qa_engine.infrastructure.detection.typeset_detector import TypesetDetector

# Detection (100% Python)
detector = TypesetDetector()
issues = detector.detect(log_content, log_path)

# Fixing (hybrid)
fixer = FloatFixer()
fixed_content, result = fixer.fix_content(content, file_path, overflow_pt)

# Check if LLM needed
if result.llm_required:
    # Delegate to LLM for content splitting
    pass
```

## Fix Patterns (Python - Deterministic)

| Pattern ID | Description | Auto |
|------------|-------------|:----:|
| `add-breakable-tcolorbox` | Add breakable option to tcolorbox | Yes |
| `add-breakable-tcolorbox-options` | Add breakable to existing options | Yes |
| `scale-figure-height` | Add height constraint to figures | Yes |
| `scale-figure-height-options` | Add height to existing options | Yes |
| `use-small-lstlisting` | Add smaller font to lstlisting | Yes |
| `use-small-lstlisting-options` | Add small font to existing options | Yes |
| `use-page-placement` | Change float placement to [p] | Yes |
| `add-page-placement` | Add page placement option | Yes |

## Fix Strategy by Overflow

| Overflow | Python Fixes | LLM Required |
|----------|--------------|:------------:|
| > 100pt | scale-figure, use-small | Yes (split content) |
| 50-100pt | use-small, add-breakable | No |
| < 50pt | use-page-placement, add-breakable | No |

## What Python CAN Do (Deterministic)

- Add `[breakable]` option to tcolorbox
- Add `height=0.85\textheight` to figures
- Add `basicstyle=\small\ttfamily` to lstlisting
- Change float placement to `[p]`
- Extract overflow amount from log

## What Requires LLM (Context-Dependent)

- **Code block splitting**: Requires understanding code structure
- **Content restructuring**: Deciding where to split
- **Semantic grouping**: Keeping related code together
- **Caption/label management**: When splitting into parts

## Output Format

```json
{
  "skill": "qa-typeset-fix-float",
  "status": "DONE",
  "fixes_applied": 2,
  "fixes": [
    {
      "file": "chapter03.tex",
      "line": 141,
      "pattern_id": "add-breakable-tcolorbox",
      "old": "\\begin{tcolorbox}",
      "new": "\\begin{tcolorbox}[breakable]"
    }
  ],
  "llm_required": [
    {
      "reason": "Large overflow requires content splitting",
      "overflow_pt": 165.89,
      "suggestion": "Split content into multiple parts"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation with hybrid Python/LLM approach

---

**Parent:** qa-typeset (Level 1)
**Coordination:** qa-orchestration/QA-CLAUDE.md
