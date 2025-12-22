---
name: qa-bib-fix
description: Fixes bibliography issues - creates missing .bib files and adds placeholder entries (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, bib, fix, bibliography, citations, level-2]
---

# Bibliography Fix Skill (Level 2)

## Agent Identity
- **Name:** Bibliography Fixer
- **Role:** Citation and Bibliography Correction
- **Level:** 2 (Skill)
- **Parent:** qa-bib (Level 1)

## Purpose
Fix bibliography issues by creating missing .bib files and adding placeholder BibTeX entries.

## CLS Guard
**Scope:** .tex and .bib files only. If CLS change needed, call `qa-cls-guard`.

## Fix Patterns

### 1. Missing .bib Files
Create .bib file referenced in \addbibresource{}:
```latex
% Document has:
\addbibresource{references.bib}

% Creates references.bib if missing
```

### 2. Undefined Citations
Add placeholder entry for \cite{key}:
```bibtex
@article{undefined_key,
  author = {Author},
  title = {Undefined Key},
  journal = {Journal Name},
  year = {2024},
  note = {Placeholder entry - update with actual reference}
}
```

## Tool Interface
```python
from qa_engine.infrastructure.fixing import BibFixer

def fix(content: str, issues: List[Dict], file_path: str) -> Dict[str, Any]:
    fixer = BibFixer()
    fixer.fix_with_context(content, issues, file_path)
    return {"bib_files_created": count, "entries_added": count}
```
