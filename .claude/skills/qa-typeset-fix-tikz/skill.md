---
name: qa-typeset-fix-tikz
description: Fix patterns for TikZ diagrams that overflow text width (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, typeset, fix, tikz, overflow, hbox, level-2, python-tool]
---

# qa-typeset-fix-tikz (Level 2)

## Agent Identity
- **Name:** TikZ Overflow Fixer
- **Role:** TikZ width correction in LaTeX documents
- **Level:** 2 (Worker Skill)
- **Parent:** qa-typeset (Level 1)

## Coordination

### Reports To
- qa-typeset (Level 1 orchestrator)

### Input
- Issues list from TikzDetector with overflow risks
- LaTeX source content

### Output
- Fixed content with TikZ width constraints
- Fix report with changes made

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Integration

This skill is **100% backed by Python** for deterministic fixes:
- **Fixer:** `src/qa_engine/infrastructure/fixing/tikz_overflow_fixer.py`
- **Patterns:** `src/qa_engine/infrastructure/fixing/tikz_overflow_patterns.py`
- **Detection:** `src/qa_engine/typeset/detection/tikz_detector.py`

```python
from qa_engine.infrastructure.fixing.tikz_overflow_fixer import TikzOverflowFixer
from qa_engine.typeset.detection.tikz_detector import TikzDetector

# Detection
detector = TikzDetector()
issues = detector.detect_in_content(content, file_path)

# Fixing
fixer = TikzOverflowFixer(strategy="resizebox")
fixed_content, result = fixer.fix_with_resizebox(content, file_path)
# or
fixed_content, result = fixer.fix_with_scale(content, scale=0.8)
```

## Fix Patterns

| Pattern ID | Description | Auto |
|------------|-------------|:----:|
| `wrap-resizebox` | Wrap tikzpicture in resizebox (preferred) | Yes |
| `wrap-resizebox-options` | Wrap tikzpicture with options | Yes |
| `add-scale` | Add scale=0.8 option | Yes |
| `add-scale-options` | Add scale to existing options | Yes |
| `add-xscale` | Add xscale=0.7 for horizontal | Yes |
| `wrap-adjustbox` | Wrap in adjustbox environment | Yes |
| `center-makebox` | Center with makebox | Yes |

## Detection Rules

| Rule ID | Description | Severity |
|---------|-------------|:--------:|
| `tikz-no-width-constraint` | TikZ without wrapper or scale | WARNING |
| `tikz-large-coordinates` | TikZ with coordinates > 10cm | CRITICAL |

## Fix Examples

### Wrap with resizebox (Preferred)
**Before:**
```latex
\begin{tikzpicture}
  \draw (0,0) -- (15,0);
\end{tikzpicture}
```

**After:**
```latex
\resizebox{\textwidth}{!}{%
\begin{tikzpicture}
  \draw (0,0) -- (15,0);
\end{tikzpicture}%
}
```

### Add scale option
**Before:**
```latex
\begin{tikzpicture}
  \draw (0,0) -- (12,0);
\end{tikzpicture}
```

**After:**
```latex
\begin{tikzpicture}[scale=0.8]
  \draw (0,0) -- (12,0);
\end{tikzpicture}
```

## What Python CAN Do (100% Coverage)

- Wrap tikzpicture in resizebox
- Wrap tikzpicture in adjustbox
- Add scale option (0.8 default)
- Add xscale option for horizontal compression
- Center with makebox for intentional overflow
- Handle tikzpicture with/without existing options

## What Requires LLM (0% - None)

All operations are deterministic regex transformations.

## Output Format

```json
{
  "skill": "qa-typeset-fix-tikz",
  "status": "DONE",
  "fixes_applied": 1,
  "fixes": [
    {
      "file": "chapter03.tex",
      "line": 145,
      "pattern_id": "wrap-resizebox",
      "description": "Wrapped tikzpicture in resizebox"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial creation with 100% Python backend

---

**Parent:** qa-typeset (Level 1)
**Coordination:** qa-orchestration/QA-CLAUDE.md
