---
name: qa-bib-english-missing-detect
description: Detects chapters with English citations but missing \printenglishbibliography (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, bib, bibliography, english, citation, detection, level-2, cross-file]
---

# English Bibliography Missing Detection (Level 2)

## Agent Identity
- **Name:** English Bibliography Missing Detector
- **Role:** Detect chapters that have English citations but no English bibliography
- **Level:** 2 (Worker Skill)
- **Parent:** qa-bib (Level 1)

## Coordination

### Reports To
- qa-bib (Level 1 orchestrator)

### Input
- LaTeX chapter files (.tex)
- Bibliography file (.bib)

### Output
- Detection report with chapters missing `\printenglishbibliography`

## Detection Logic

### Rule: `bib-english-references-missing`

| Attribute | Value |
|-----------|-------|
| Rule ID | `bib-english-references-missing` |
| Description | Chapter has English citations but no `\printenglishbibliography` |
| Severity | CRITICAL |
| Scope | Cross-file (requires .tex + .bib analysis) |

### Algorithm

```python
def detect_missing_english_bibliography(chapters_dir, bib_file):
    """
    Detect chapters with English citations but missing \printenglishbibliography.

    Steps:
    1. Load .bib file and identify entries with keyword=english
    2. For each chapter .tex file:
       a. Find all \cite{} commands
       b. Check if any cited entry has keyword=english
       c. Check if chapter has \printenglishbibliography
       d. If has English citations but no English bib → CRITICAL issue
    """
    issues = []

    # Load English citation keys from .bib
    english_keys = get_english_bib_keys(bib_file)

    for chapter_file in glob(chapters_dir + "/chapter*.tex"):
        # Extract citations from chapter
        citations = extract_citations(chapter_file)

        # Check if any citation is English
        has_english_citation = any(cite in english_keys for cite in citations)

        # Check if chapter has English bibliography
        has_english_bib = has_printenglishbibliography(chapter_file)

        if has_english_citation and not has_english_bib:
            issues.append({
                "rule": "bib-english-references-missing",
                "severity": "CRITICAL",
                "file": chapter_file,
                "message": f"Chapter has {len([c for c in citations if c in english_keys])} English citations but no \\printenglishbibliography",
                "english_citations": [c for c in citations if c in english_keys]
            })

    return issues
```

## Execution

### Manual Invocation
```
/qa-bib-english-missing-detect <chapters_dir> <bib_file>
```

### Example
```
/qa-bib-english-missing-detect chapters/ references.bib
```

### Expected Output
```json
{
  "summary": {
    "total_chapters": 11,
    "chapters_with_issues": 1,
    "total_issues": 1
  },
  "issues": [
    {
      "rule": "bib-english-references-missing",
      "severity": "CRITICAL",
      "file": "chapters/chapter03.tex",
      "message": "Chapter has 5 English citations but no \\printenglishbibliography",
      "english_citations": [
        "owasp_agentic_2026",
        "echoleak_cve_2025",
        "wef_nhi_risks_2025",
        "agentic_ai_security_threats_2025"
      ],
      "fix": "Add \\printenglishbibliography after \\printbibliography"
    }
  ]
}
```

## Fix Recommendation

When this issue is detected, use `qa-bib-english-missing-fix` to:
1. Locate the `\printbibliography` command in the chapter
2. Add `\printenglishbibliography` after it

## Version History
- **v1.0.0** (2025-12-21): Initial creation
  - Detects chapters with English citations but missing English bibliography
  - Cross-file analysis: .tex files + .bib file
  - Integrates with qa-bib family orchestrator
