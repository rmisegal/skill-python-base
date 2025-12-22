---
name: qa-BiDi-fix-toc-config
description: Fixes TOC counter format configuration in CLS files for proper BiDi rendering (Level 2 skill)
version: 1.1.0
author: QA Team
tags: [qa, bidi, toc, cls, fix, level-2]
---

# QA BiDi Fix TOC Config (Level 2)

## Identity
- **Level:** 2 (Fix)
- **Family:** qa-BiDi
- **Role:** Fix CLS counter format configuration for TOC BiDi
- **Version:** 1.1.0

## CLS Guard
**MANDATORY:** Call `qa-cls-guard` before any CLS modification.

## LLM vs Python Split

| Issue | Handler | Reason |
|-------|---------|--------|
| `toc-numberline-double-wrap` | **Python** | Simple regex removal |
| `toc-missing-thechapter` | **Python** | Insert line pattern |
| `toc-thechapter-no-wrapper` | **Python** | Wrap existing pattern |
| `toc-thesection-no-wrapper` | **Python** | Wrap existing pattern |
| `toc-thesubsection-no-wrapper` | **Python** | Wrap existing pattern |

## Python Tool Integration

```python
from qa_engine.infrastructure.fixing.toc_fixer import TOCFixer

fixer = TOCFixer()

# Fix individual issues
content, changed = fixer.fix_numberline_double_wrap(cls_content)
content, changed = fixer.fix_thechapter_no_wrapper(content)

# Or fix all counter issues at once
content, num_fixes = fixer.fix_all_counter_issues(cls_content)

# Check if a rule needs LLM
if TOCFixer.requires_llm(issue.rule):
    # Delegate to LLM
else:
    # Use Python fixer
```

## Fix Patterns

### 1. Remove Double-Wrapping from `\numberline`

```latex
% BEFORE - Double-wrapping:
\renewcommand{\numberline}[1]{\orig@numberline{\textenglish{#1}}}

% AFTER - Counters handle it:
% \numberline wrapper removed - counters handle LTR
```

### 2. Add `\textenglish{}` Wrapper to Counters

```latex
% BEFORE:
\renewcommand{\thechapter}{\arabic{chapter}}

% AFTER:
\renewcommand{\thechapter}{\textenglish{\arabic{chapter}}}
```

## Performance Benefits

- **Python fixes**: ~0.1ms per fix (deterministic)
- **LLM fixes**: ~500ms+ per fix (requires context)
- **Repeatability**: 100% consistent results

## Report Format

```json
{
  "skill": "qa-BiDi-fix-toc-config",
  "status": "DONE",
  "python_fixes": 3,
  "llm_fixes": 0
}
```

## Version History
- **v1.1.0** (2025-12-19): Added Python fixer integration
- **v1.0.0** (2025-12-19): Initial creation

---

**Parent:** qa-BiDi (Level 1)
**Python Tool:** `qa_engine.infrastructure.fixing.toc_fixer.TOCFixer`
