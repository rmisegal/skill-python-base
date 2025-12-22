---
name: qa-bib-english-missing-fix
description: Fixes chapters with English citations by adding \printenglishbibliography (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, bib, bibliography, english, citation, fix, level-2, cross-file]
---

# English Bibliography Missing Fix (Level 2)

## Agent Identity
- **Name:** English Bibliography Missing Fixer
- **Role:** Add `\printenglishbibliography` to chapters that have English citations
- **Level:** 2 (Worker Skill)
- **Parent:** qa-bib (Level 1)

## Coordination

### Reports To
- qa-bib (Level 1 orchestrator)

### Input
- Detection report from `qa-bib-english-missing-detect`
- OR: LaTeX chapter files (.tex) + Bibliography file (.bib)

### Output
- Modified chapter files with `\printenglishbibliography` added

## CLS Guard
**Scope:** .tex and .bib files only. If CLS change needed, call `qa-cls-guard`.

## Fix Logic

### Rule: `bib-english-references-missing`

| Attribute | Value |
|-----------|-------|
| Rule ID | `bib-english-references-missing` |
| Fix Action | Add `\printenglishbibliography` after `\printbibliography` |
| Scope | Per-chapter |

### Algorithm

```python
def fix_missing_english_bibliography(chapter_file):
    """
    Add \printenglishbibliography after \printbibliography.

    Steps:
    1. Read chapter file
    2. Find \printbibliography line
    3. Add \printenglishbibliography after it
    4. Write back to file
    """
    content = read_file(chapter_file)

    # Find \printbibliography and add \printenglishbibliography after
    pattern = r'(\\printbibliography\b[^\n]*)'
    replacement = r'\1\n\\printenglishbibliography'

    new_content = re.sub(pattern, replacement, content)

    write_file(chapter_file, new_content)
```

## Execution

### Manual Invocation
```
/qa-bib-english-missing-fix <chapters_dir> <bib_file>
```

### Example
```
/qa-bib-english-missing-fix chapters/ references.bib
```

### Expected Output
```json
{
  "summary": {
    "total_chapters": 11,
    "chapters_fixed": 11,
    "already_correct": 0
  },
  "fixes": [
    {
      "file": "chapters/chapter01.tex",
      "line": 234,
      "action": "Added \\printenglishbibliography after \\printbibliography",
      "english_citations": 8
    }
  ]
}
```

## Safety Checks

1. **Idempotent**: Will not add duplicate `\printenglishbibliography`
2. **Backup**: Creates .bak files before modification (optional)
3. **Verify**: Only modifies if `\printbibliography` exists

## Version History
- **v1.0.0** (2025-12-21): Initial creation
  - Adds `\printenglishbibliography` after `\printbibliography`
  - Idempotent - won't duplicate if already present
  - Works with qa-bib-english-missing-detect output
