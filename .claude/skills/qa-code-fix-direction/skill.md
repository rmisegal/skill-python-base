---
name: qa-code-fix-direction
description: Fix patterns for Hebrew text direction in code blocks (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, code, fix, direction, hebrew, level-2, python-tool]
---

# qa-code-fix-direction (Level 2)

## Agent Identity
- **Name:** Code Direction Fixer
- **Role:** Hebrew text direction correction in code blocks
- **Level:** 2 (Worker Skill)
- **Parent:** qa-code (Level 1)

## Coordination

### Reports To
- qa-code (Level 1 orchestrator)

### Input
- Issues list from CodeDetector with `code-direction-hebrew` rule
- LaTeX source content

### Output
- Fixed content with Hebrew text wrapped in `\texthebrew{}`
- Fix report with changes made

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Integration

This skill is **100% backed by Python** for deterministic fixes:
- **Fixer:** `src/qa_engine/infrastructure/fixing/direction_fixer.py`
- **Patterns:** `src/qa_engine/infrastructure/fixing/direction_patterns.py`
- **Detection:** `src/qa_engine/infrastructure/detection/code_detector.py`

```python
from qa_engine.infrastructure.fixing.direction_fixer import DirectionFixer
from qa_engine.infrastructure.detection.code_detector import CodeDetector

# Detection
detector = CodeDetector()
issues = detector.detect(content, file_path)
direction_issues = [i for i in issues if i.rule == "code-direction-hebrew"]

# Fixing
fixer = DirectionFixer(wrapper="texthebrew")
fixed_content, result = fixer.fix_content(content, file_path)
# or with different wrapper:
fixed_content, result = fixer.fix_with_wrapper(content, wrapper="he")
```

## Fix Patterns

| Pattern ID | Description | Auto |
|------------|-------------|:----:|
| `hebrew-in-code` | Wrap Hebrew text with `\texthebrew{}` | Yes |
| `hebrew-comment-python` | Wrap Hebrew in Python comments | Yes |
| `hebrew-string` | Wrap Hebrew in string literals | Yes |

## Code Environments Supported

- `lstlisting`
- `minted`
- `verbatim`
- `pythonbox` / `pythonbox*`
- `tcolorbox`
- `tcblisting`

## Fix Examples

### Hebrew in Code Block
**Before:**
```latex
\begin{pythonbox}
print("שלום")  # תגובה
\end{pythonbox}
```

**After:**
```latex
\begin{pythonbox}
print("\texthebrew{שלום}")  # \texthebrew{תגובה}
\end{pythonbox}
```

### With Alternative Wrapper
**Before:**
```latex
\begin{lstlisting}
name = "שם"
\end{lstlisting}
```

**After (with wrapper="he"):**
```latex
\begin{lstlisting}
name = "\he{שם}"
\end{lstlisting}
```

## What Python CAN Do (100% Coverage)

- Detect Hebrew characters in code blocks
- Wrap Hebrew text with `\texthebrew{}`
- Use alternative wrappers (`\he{}`, `\heb{}`)
- Handle all common code environments
- Skip already-wrapped Hebrew text
- Preserve line structure and indentation

## What Requires LLM (0% - None)

All operations are deterministic regex transformations.

## Output Format

```json
{
  "skill": "qa-code-fix-direction",
  "status": "DONE",
  "fixes_applied": 3,
  "fixes": [
    {
      "file": "chapter03.tex",
      "line": 45,
      "original": "שלום",
      "replacement": "\\texthebrew{שלום}",
      "pattern_id": "hebrew-in-code"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial creation with 100% Python backend

---

**Parent:** qa-code (Level 1)
**Coordination:** qa-orchestration/QA-CLAUDE.md
