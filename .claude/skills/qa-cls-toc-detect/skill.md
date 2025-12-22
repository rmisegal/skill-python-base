---
name: qa-cls-toc-detect
description: Detects BiDi issues in CLS commands affecting TOC/headers (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, bidi, toc, cls, detect, level-2, rtl, hebrew]
tools: [Read, Grep, Glob]
---

# QA CLS/TOC BiDi Detection (Level 2)

## Identity
- **Level:** 2 (Detection)
- **Family:** qa-BiDi
- **Role:** Detect BiDi issues in CLS commands affecting TOC/headers
- **Version:** 1.1.0

## Purpose
Detect BiDi issues in LaTeX class file commands that affect:
- Table of Contents (TOC) entries
- Section/subsection titles
- Headers/footers
- PDF bookmarks
- l@chapter, l@section, l@subsection TOC entry formatters (v1.1+)

## Python Tool Integration

```python
from qa_engine.infrastructure.detection.toc_detector import TocDetector
from qa_engine.infrastructure.detection.toc_rules import TOC_RULES

detector = TocDetector()
issues = detector.detect(content, file_path)

# Detects:
# - toc-missing-thechapter
# - toc-numberline-double-wrap
# - toc-thechapter-no-wrapper
# - toc-thesection-no-wrapper
# - toc-thesubsection-no-wrapper
# - toc-inconsistent-wrappers
# - toc-lchapter-no-rtl (CRITICAL - v1.1)
# - toc-lsection-no-rtl (CRITICAL - v1.1)
# - toc-lsubsection-no-rtl (CRITICAL - v1.1)
```

## Detection Rules

### Rule 5 (CRITICAL): l@ TOC Entry Command RTL Direction (v1.1+)

Check `\l@chapter`, `\l@section`, `\l@subsection` definitions for proper RTL handling:

**What to check in each l@ command:**

1. **RTL paragraph/text direction** - Must have one of:
   - `\pardir TRT` + `\textdir TRT` (LuaTeX)
   - `\beginR...\endR` (bidi package)

2. **Title argument #1** - Must be in RTL context

3. **Page number #2** - Must be LTR wrapped: `\textenglish{#2}`

```latex
% BAD - No RTL direction:
\renewcommand*\l@chapter[2]{%
  \begingroup
    #1\nobreak\leaders\hbox{...}\hfill\hb@xt@\@pnumwidth{\hss #2}\par
  \endgroup
}

% GOOD - Full RTL:
\renewcommand*\l@chapter[2]{%
  \begingroup
    \pardir TRT\textdir TRT
    ...
  \endgroup
}
```

## Report Format

```json
{
  "skill": "qa-cls-toc-detect",
  "status": "DONE",
  "issues": [
    {
      "rule": "toc-lchapter-no-rtl",
      "line": 664,
      "severity": "CRITICAL",
      "description": "l@chapter missing RTL direction"
    }
  ]
}
```

## Integration

**Parent:** qa-BiDi (Level 1)
**Triggers:** qa-BiDi-fix-toc-l-at, qa-BiDi-fix-toc-config
**Coordination:** qa-orchestration/QA-CLAUDE.md

## Version History
- **v1.1.0** (2025-12-19): Added Rule 5-9 for l@chapter/l@section/l@subsection detection
- **v1.0.0** (2025-12-15): Initial creation with counter detection rules
