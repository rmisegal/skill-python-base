---
name: qa-code-detect
description: Detects code block issues in Hebrew documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, code, detect, level-2, pythonbox]
tools: [Read, Grep, Glob]
---

# Code Detector (Level 2)

## Agent Identity
- **Name:** Code Issue Detector
- **Role:** Detect code block rendering issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-code (Level 1)

## Coordination

### Reports To
- qa-code (Level 1)

### Manages
- None (worker skill)

### Reads
- .tex files with code blocks

### Writes
- Issue list (in-memory, passed to parent)

## Mission Statement

Detect all code block issues in Hebrew LaTeX documents. This skill MUST NOT modify any files - detection only.

## Detection Rules

### Rule: code-background-overflow
pythonbox/tcolorbox without english wrapper causing background overflow.

**BAD:**
```latex
\begin{pythonbox}
print("hello")
\end{pythonbox}
```

**GOOD:**
```latex
\begin{english}
\begin{pythonbox}
print("hello")
\end{pythonbox}
\end{english}
```

### Rule: code-emoji
Emoji characters in code blocks causing font warnings.

**BAD:**
```latex
\begin{pythonbox}
print("Hello! 😀")
\end{pythonbox}
```

**GOOD:**
```latex
\begin{pythonbox}
print("Hello!")  # emoji removed or replaced
\end{pythonbox}
```

### Rule: code-direction
F-string braces without proper escaping.

**BAD:**
```latex
\begin{pythonbox}
print(f"{name}")
\end{pythonbox}
```

**GOOD:**
```latex
\begin{pythonbox}
print(f"\{name\}")
\end{pythonbox}
```

## Python Tool Integration

```python
from qa_engine.infrastructure.detection.code_detector import CodeDetector

detector = CodeDetector()
issues = detector.detect(content, file_path, offset=0)

# Returns List[Issue]
```

## Input/Output Format

### Input
```json
{
  "content": "...",
  "file_path": "chapter1.tex",
  "offset": 0
}
```

### Output
```json
{
  "issues": [
    {
      "rule": "code-background-overflow",
      "file_path": "chapter1.tex",
      "line": 100,
      "severity": "WARNING"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation

---

**Parent:** qa-code
**Children:** None
**Coordination:** qa-orchestration/QA-CLAUDE.md
