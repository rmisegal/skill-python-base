---
name: qa-toc-english-text-naked-fix
description: Fixes naked English text in TOC by wrapping in LTR commands to prevent RTL rendering (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, toc, fix, level-2, bidi, english, ltr, naked-english]
tools: [Read, Edit, Grep, Glob]
---

# TOC Naked English Fixer (Level 2)

## Agent Identity
- **Name:** TOC Naked English Fixer
- **Role:** Fix English text that renders RTL in TOC
- **Level:** 2 (Worker Skill)
- **Parent:** qa-BiDi (Level 1)

## Coordination

### Reports To
- qa-BiDi (Level 1)
- qa-super (Level 0)

### Triggered By
- Detection rule: `toc-english-text-naked`
- Manual invocation

### Reads
- .tex source files (chapter files, main files)
- .toc files (for reference)
- Detection output from qa-toc-comprehensive-detect

### Writes
- .tex source files (applies fixes)

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Mission Statement

Fix English text in LaTeX source files that will render RTL (backwards) in the TOC.
This skill wraps naked English text in `\textenglish{}` to ensure proper LTR rendering.

**Problem:**
```
TOC shows: 54 . . . . . . . . secnerefeR hsilgnE 11.2
Should be: 2.11 English References . . . . . . . . 54
```

**Root Cause:** English text in section titles not wrapped in LTR command.

## Fix Strategy

### Strategy 1: Wrap in Source File (PREFERRED)

Fix the source .tex file where the section/chapter is defined.

**Before:**
```latex
\section{English References}
```

**After:**
```latex
\section{\textenglish{English References}}
```

### Strategy 2: Wrap Mixed Content

For mixed Hebrew/English titles:

**Before:**
```latex
\section{מדריך API למפתחים}
```

**After:**
```latex
\section{מדריך \textenglish{API} למפתחים}
```

### Strategy 3: Multiple English Words

For titles with multiple English segments:

**Before:**
```latex
\subsection{הגדרת System Prompt ב-ChatGPT}
```

**After:**
```latex
\subsection{הגדרת \textenglish{System Prompt} ב-\textenglish{ChatGPT}}
```

## Fix Rules

### Rule 1: Full English Title
If title is entirely English, wrap the whole title:
```latex
\section{\textenglish{Complete English Title}}
```

### Rule 2: English at Start
If title starts with English followed by Hebrew:
```latex
\section{\textenglish{API} - ממשק תכנות}
```

### Rule 3: English at End
If title ends with English after Hebrew:
```latex
\section{מדריך למשתמשי \textenglish{Windows}}
```

### Rule 4: English in Middle
If English appears between Hebrew:
```latex
\section{הגדרות \textenglish{Advanced Settings} נוספות}
```

### Rule 5: Acronyms
Short uppercase acronyms (2-5 letters):
```latex
\section{פרוטוקול \textenglish{API} ו-\textenglish{SDK}}
```

## Python Tool Integration

```python
from qa_engine.toc.fixing.naked_english_fixer import NakedEnglishFixer

# Initialize fixer
fixer = NakedEnglishFixer()

# Fix a single file
result = fixer.fix_file("chapters/chapter01.tex")
print(f"Fixed {result.fixes_applied} issues")

# Fix from detection output
from qa_engine.toc import TOCComprehensiveDetector
detector = TOCComprehensiveDetector()
issues = detector.detect_in_file("master/master-main.toc")

# Get naked English issues only
naked_issues = [i for i in issues if i.rule == "toc-english-text-naked"]

# Apply fixes
for issue in naked_issues:
    source_file = fixer.find_source_file(issue)
    if source_file:
        fixer.fix_issue(source_file, issue)
```

## Input/Output Format

### Input (from detector)
```json
{
  "rule": "toc-english-text-naked",
  "file": "master-main.toc",
  "line": 54,
  "content": "English References",
  "context": {
    "naked_words": ["English", "References"],
    "entry_type": "section",
    "fix": "Wrap in \\textenglish{}"
  }
}
```

### Output
```json
{
  "status": "fixed",
  "source_file": "chapters/chapter02.tex",
  "line": 142,
  "original": "\\section{English References}",
  "fixed": "\\section{\\textenglish{English References}}",
  "backup": "chapters/chapter02.tex.bak"
}
```

## Fix Algorithm

```python
def fix_naked_english(content: str, naked_words: List[str]) -> str:
    """
    Wrap naked English words in \textenglish{}.

    Algorithm:
    1. Find each naked word in content
    2. Check if already wrapped (skip if so)
    3. Determine context (full title, mixed, acronym)
    4. Apply appropriate wrapper
    5. Handle adjacent English words as single phrase
    """

    # Group adjacent English words
    phrases = group_adjacent_words(content, naked_words)

    for phrase in phrases:
        if not is_wrapped(content, phrase):
            # Wrap the phrase
            content = wrap_in_textenglish(content, phrase)

    return content


def group_adjacent_words(content: str, words: List[str]) -> List[str]:
    """
    Group adjacent English words into phrases.

    "English References" → ["English References"]
    "API and SDK" → ["API", "SDK"] (and is Hebrew)
    """
    # Implementation groups consecutive English words
    pass
```

## Edge Cases

### Already Wrapped
Skip if already in wrapper:
```latex
\section{\textenglish{Already Wrapped}}  % Skip
\section{\LR{Also Wrapped}}              % Skip
\section{\en{Short Form}}                % Skip
```

### Nested Wrappers
Don't double-wrap:
```latex
% BAD: \textenglish{\textenglish{Double}}
% GOOD: \textenglish{Single}
```

### Math Mode
Don't wrap inside math:
```latex
% Don't touch: $API = \frac{x}{y}$
% API here is math variable, not text
```

### Code Environments
Don't wrap inside verbatim/code:
```latex
% Don't touch: \verb|API_KEY|
% Don't touch: \texttt{function_name}
```

## Execution Workflow

1. Receive detection output with naked English issues
2. For each issue:
   a. Find source .tex file containing the section
   b. Locate the exact line with the section command
   c. Identify naked English words/phrases
   d. Apply appropriate wrapper
   e. Write fixed content back
3. Recompile and verify TOC

## Configuration

Fixer preferences in `toc_fixer_config.json`:
```json
{
  "wrapper_command": "\\textenglish",
  "create_backup": true,
  "backup_extension": ".bak",
  "dry_run": false,
  "min_word_length": 3,
  "always_wrap_acronyms": true
}
```

## Version History
- **v1.0.0** (2025-12-21): Initial implementation
  - Fixes naked English text in section/chapter titles
  - Groups adjacent English words into phrases
  - Handles mixed Hebrew/English content
  - Preserves already-wrapped content

---

**Parent:** qa-BiDi
**Detector:** qa-toc-comprehensive-detect (rule: toc-english-text-naked)
**Related:** qa-BiDi-fix-text
