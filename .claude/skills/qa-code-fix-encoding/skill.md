---
name: qa-code-fix-encoding
description: Fixes character encoding issues in code blocks (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, code, fix, encoding, unicode, level-2, python-tool]
---

# qa-code-fix-encoding (Level 2)

## Agent Identity
- **Name:** Code Fix Encoding
- **Role:** Fix character encoding issues in code blocks
- **Level:** 2 (Worker Skill)
- **Parent:** qa-code (Level 1)

## Coordination

### Reports To
- qa-code (Level 1 orchestrator)

### Input
- LaTeX source files with encoding issues
- Issues detected by qa-code-detect

### Output
- Fixed content with proper encoding

## Python Tool Integration

This skill is backed by Python for deterministic fixing:
- **Module:** tool.py
- **Functions:** run_fix(), get_patterns()

## Fix Patterns

| Pattern | Unicode | Original | Replacement (Text) | Replacement (Code) |
|---------|---------|----------|-------------------|-------------------|
| multiplication | U+00D7 | x | `$\times$` | `*` |
| right-arrow | U+2192 | -> | `$\rightarrow$` | `->` |
| check-mark | U+2713 | checkmark | `[+]` | `[+]` |
| ballot-x | U+2717 | X mark | `[-]` | `[-]` |
| emoji | Various | emoji | Text label | Text label |

## Context-Aware Fixes

The fixer applies different replacements based on context:

1. **In verbatim/lstlisting/minted**: Use ASCII alternatives
   - x -> *
   - -> -> ->
   - checkmark -> [+]
   - X mark -> [-]

2. **In regular text**: Use LaTeX commands
   - x -> $\times$
   - -> -> $\rightarrow$
   - checkmark -> \checkmark
   - X mark -> $\times$

## Mission Statement

Fix character encoding issues in LaTeX documents to prevent missing character
warnings during compilation with LuaLaTeX.

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Version History
- **v1.0.0** (2025-12-15): Initial creation
