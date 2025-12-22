---
name: qa-img-fix-paths
description: Fixes image path issues in LaTeX source (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, img, fix, paths, level-2, python-tool]
---

# qa-img-fix-paths (Level 2)

## Agent Identity
- **Name:** Image Path Fixer
- **Role:** LaTeX image path correction
- **Level:** 2 (Worker Skill)
- **Parent:** qa-img (Level 1)

## Coordination

### Reports To
- qa-img (Level 1 orchestrator)

### Input
- LaTeX source files
- Issues list from qa-img-detect

### Output
- Fixed content with corrected paths

## CLS Guard
**Scope:** .tex files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Integration

This skill is backed by Python for deterministic fixes:
- **Module:** `src/qa_engine/infrastructure/fixing/image_fixer.py`
- **Patterns:** 6 patterns defined in `image_patterns.py`

```python
from qa_engine.infrastructure.fixing.image_fixer import ImageFixer

fixer = ImageFixer()
fixed_content = fixer.fix(content, issues)
```

## Fix Patterns

| Pattern ID | Description | Auto |
|------------|-------------|:----:|
| `add-graphicspath` | Add graphicspath to preamble | Yes |
| `fix-path-prefix` | Add images/ prefix | Yes |
| `replace-placeholder` | Replace fbox with includegraphics | No |
| `add-width-spec` | Add width specification | Yes |
| `fix-extension-png` | Fix file extension | Yes |
| `fix-case-lower` | Lowercase filename | Yes |

## Fix Examples

### Add graphicspath
**Before:**
```latex
\begin{document}
```

**After:**
```latex
\graphicspath{{images/}{./images/}}

\begin{document}
```

### Fix Path Prefix
**Before:**
```latex
\includegraphics{myimage.png}
```

**After:**
```latex
\includegraphics{images/myimage.png}
```

## Mission Statement

Fix image path issues in LaTeX source based on detected problems.
Operates ONLY on issues provided by qa-img-detect.

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend
