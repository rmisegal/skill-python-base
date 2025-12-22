---
name: qa-BiDi-detect
description: Detects bidirectional text problems in Hebrew-English documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, bidi, detect, level-2, rtl, hebrew]
tools: [Read, Grep, Glob]
---

# BiDi Detector (Level 2)

## Agent Identity
- **Name:** BiDi Issue Detector
- **Role:** Detect bidirectional text rendering issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-BiDi (Level 1)

## Coordination

### Reports To
- qa-BiDi (Level 1)

### Manages
- None (worker skill)

### Reads
- .tex files in project

### Writes
- Issue list (in-memory, passed to parent)

## Mission Statement

Detect all bidirectional text issues in Hebrew-English LaTeX documents. This skill MUST NOT modify any files - detection only.

## Detection Rules

### Rule: bidi-numbers
Numbers in Hebrew context without LTR wrapper.

**BAD:**
```latex
המחיר הוא 99.99 שקלים
```

**GOOD:**
```latex
המחיר הוא \en{99.99} שקלים
```

### Rule: bidi-english
English words in Hebrew context without wrapper.

**BAD:**
```latex
זה טקסט test בעברית
```

**GOOD:**
```latex
זה טקסט \en{test} בעברית
```

### Rule: bidi-acronym
Uppercase acronyms (2+ letters) without wrapper.

**BAD:**
```latex
ראשי תיבות API בעברית
```

**GOOD:**
```latex
ראשי תיבות \en{API} בעברית
```

### Rule: bidi-tikz-rtl
TikZ environments without english wrapper in RTL context.

**BAD:**
```latex
\begin{tikzpicture}...\end{tikzpicture}
```

**GOOD:**
```latex
\begin{english}
\begin{tikzpicture}...\end{tikzpicture}
\end{english}
```

## Python Tool Integration

```python
from qa_engine.infrastructure.detection.bidi_detector import BiDiDetector

detector = BiDiDetector()
issues = detector.detect(content, file_path, offset=0)

# Returns List[Issue] with:
# - rule: str (e.g., "bidi-numbers")
# - file_path: str
# - line: int
# - content: str (matched text)
# - severity: Severity
# - fix: str (suggested fix)
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
      "rule": "bidi-numbers",
      "file_path": "chapter1.tex",
      "line": 42,
      "content": "123",
      "severity": "WARNING",
      "fix": "\\en{123}"
    }
  ]
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial implementation with 6 rules

---

**Parent:** qa-BiDi
**Children:** None
**Coordination:** qa-orchestration/QA-CLAUDE.md
