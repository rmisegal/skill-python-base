---
name: qa-BiDi-fix-toc-l-at
description: Fixes l@chapter, l@section, l@subsection TOC entry commands for proper Hebrew RTL rendering (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, bidi, toc, cls, fix, level-2, rtl, llm-required]
---

# QA BiDi Fix TOC l@ Commands (Level 2)

## Identity
- **Level:** 2 (Fix)
- **Family:** qa-BiDi
- **Role:** Fix l@chapter, l@section, l@subsection for Hebrew RTL TOC
- **Version:** 1.0.0

## CLS Guard
**MANDATORY:** Call `qa-cls-guard` before any CLS modification.

## LLM vs Python Split

| Issue | Handler | Reason |
|-------|---------|--------|
| `toc-lchapter-no-rtl` | **LLM** | Complex macro restructuring |
| `toc-lsection-no-rtl` | **LLM** | Complex macro restructuring |
| `toc-lsubsection-no-rtl` | **LLM** | Complex macro restructuring |

**Why LLM is required:**
1. Must parse nested LaTeX macro structure
2. Must transform element order (page# -> dots -> title)
3. Must swap leftskip/rightskip correctly
4. Must understand brace balancing across multiple lines
5. Context-dependent decisions based on existing code

## Python Tool - Detection Only

```python
from qa_engine.infrastructure.detection.toc_detector import TOCDetector
from qa_engine.infrastructure.fixing.toc_fixer import TOCFixer

# Detection (Python - fast, deterministic)
detector = TOCDetector()
issues = detector.detect(cls_content, file_path)

# Check if LLM is needed
for issue in issues:
    if TOCFixer.requires_llm(issue.rule):
        # This issue needs LLM - delegate to skill
        pass
```

## Fix Pattern (LLM)

### Key Transformations Required:

1. **Add RTL direction** after `\begingroup`:
   ```latex
   \pardir TRT\textdir TRT
   ```

2. **Swap margin skips**:
   - `\rightskip` -> `\leftskip`
   - `\leftskip` -> `\rightskip`

3. **Reorder elements**:
   - Page number moves to start
   - Title moves to end

### Example Transformation

```latex
% BEFORE (LTR order):
\renewcommand*\l@chapter[2]{%
  \begingroup
    \parindent \z@ \rightskip \@tocrmarg
    #1\nobreak\leaders\hbox{...}\hfill\hb@xt@\@pnumwidth{\hss \textenglish{#2}}\par
  \endgroup
}

% AFTER (RTL order - LLM transforms):
\renewcommand*\l@chapter[2]{%
  \begingroup
    \pardir TRT\textdir TRT
    \parindent \z@ \leftskip \@tocrmarg
    \hb@xt@\@pnumwidth{\textenglish{#2}\hss}\nobreak
    \leaders\hbox{...}\hfill\nobreak #1\par
  \endgroup
}
```

## Performance Considerations

- **Detection**: Python (~1ms for entire CLS file)
- **Fixing**: LLM required (~500ms-1s per command)
- **Total for 3 commands**: ~1.5-3s

## Report Format

```json
{
  "skill": "qa-BiDi-fix-toc-l-at",
  "status": "DONE",
  "handler": "LLM",
  "fixes_applied": [
    {"command": "l@chapter", "line": 651, "status": "FIXED"},
    {"command": "l@section", "line": 671, "status": "FIXED"},
    {"command": "l@subsection", "line": 690, "status": "FIXED"}
  ]
}
```

## Version History
- **v1.0.0** (2025-12-19): Initial creation
  - Detection: Python (via TOCDetector)
  - Fixing: LLM required (complex macro restructuring)

---

**Parent:** qa-BiDi (Level 1)
**Detection:** Python `TOCDetector`
**Fixing:** LLM (semantic understanding required)
