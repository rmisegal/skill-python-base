---
name: qa-typeset-fix-hbox
description: Fix patterns for Overfull/Underfull hbox warnings (Level 2 skill)
version: 1.2.0
author: QA Team
tags: [qa, typeset, fix, hbox, overfull, underfull, level-2, llm-assisted]
family: typeset
parent: qa-typeset
has_python_tool: true
---

# Hbox Fix Patterns (Level 2)

## Agent Identity
- **Name:** Hbox Warning Fixer
- **Role:** Line Width Correction
- **Level:** 2 (Skill)
- **Parent:** qa-typeset (Level 1)

## Purpose
Fix Overfull and Underfull hbox warnings in LaTeX documents using a hybrid approach:
- **Python Tool**: Automated fixes for deterministic patterns
- **LLM**: Intelligent fixes requiring context understanding

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Workflow

### Phase 1: Python Auto-Fix
The Python tool automatically fixes:
1. Table cells with long code identifiers → Add `\small`
2. Lines with `{\sloppy ...}` wrapper needs
3. Code identifiers needing `\allowbreak`

### Phase 2: LLM-Assisted Fix
For issues requiring judgment, the tool generates `manual_review` items with:
- `content`: The problematic line
- `context`: Surrounding lines for understanding
- `suggestion`: Recommended fix approach
- `options`: Available fix strategies

The LLM then:
1. Reads the `manual_review` items
2. Uses `generate_llm_prompt()` to get structured guidance
3. Applies fixes using `apply_llm_fix()`

## Python Tool Functions

```python
# Auto-fix content
fixed_content, result = fixer.fix_content(content, file_path, issues)

# Generate prompt for LLM to fix a manual review item
prompt = fixer.generate_llm_prompt(review_item)

# Apply LLM's fix
fixed_content, fix = fixer.apply_llm_fix(content, line_num, fix_type, new_content)
```

## Output Format
```json
{
  "skill": "qa-typeset-fix-hbox",
  "status": "DONE",
  "fixes_applied": [
    {"file": "ch.tex", "line": 15, "issue_type": "overfull",
     "fix_type": "small", "before": "...", "after": "..."}
  ],
  "manual_review": [
    {"file": "ch.tex", "line": 20, "issue_type": "overfull",
     "content": "...", "suggestion": "reword", "options": ["..."]}
  ],
  "summary": {"auto_fixed": 1, "needs_review": 1}
}
```

## LLM Fix Types
- `reword`: Text was reworded for better flow
- `hyphenate`: Hyphenation hints added (`\-`)
- `sloppy`: Wrapped with `{\sloppy ...}`
- `abbreviate`: Long phrase abbreviated
