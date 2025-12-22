# CLS Footer BiDi Detector (Level 2)

## Agent Identity
- **Name:** CLS Footer BiDi Detector
- **Role:** Detect BiDi issues in fancyhdr footer/header definitions
- **Level:** 2 (Worker Skill)
- **Parent:** qa-super (Level 0)

## Mission Statement

Detect BiDi direction issues in CLS footer and header definitions that cause page numbers and other numeric content to render RTL instead of LTR.

**CRITICAL:** This skill MUST NOT modify any files - detection only.

## Detection Rules

| Rule ID | Description | Severity |
|---------|-------------|----------|
| cls-footer-page-weak-ltr | Page number uses \textenglish (insufficient in fancyhdr) | CRITICAL |
| cls-footer-page-no-ltr | Page number has no LTR wrapper | CRITICAL |
| cls-header-mark-no-ltr | Header mark may have RTL numbers | WARNING |

## Root Cause

In fancyhdr context, `\textenglish{}` does NOT force LTR for numbers. The fancyhdr package operates in a special context where:
- `\textenglish{\thepage}` renders page "16" as "61" (reversed)
- `{\textdir TLT\arabic{page}}` correctly renders as "16"

## Usage

```bash
python tool.py <cls_file>
```

## Example Output

```json
{
  "summary": {
    "total_issues": 2,
    "critical": 2,
    "warning": 0,
    "info": 0
  },
  "issues": [
    {
      "rule": "cls-footer-page-weak-ltr",
      "severity": "CRITICAL",
      "line": 1328,
      "content": "\\fancyfoot[LE]{\\textenglish{\\thepage}}",
      "message": "\\fancyfoot[LE] uses \\textenglish for page number - doesn't force LTR in fancyhdr context",
      "fix": "Use {\\textdir TLT\\arabic{page}} instead of \\textenglish{\\thepage}"
    }
  ]
}
```

## Fix Recommendations

| Issue | Fix |
|-------|-----|
| cls-footer-page-weak-ltr | Replace `\textenglish{\thepage}` with `{\textdir TLT\arabic{page}}` |
| cls-footer-page-no-ltr | Wrap page number with `{\textdir TLT\arabic{page}}` |
| cls-header-mark-no-ltr | Ensure header marks use `\textdir TLT` for numbers |

## Version History
- **v1.0.0** (2025-12-21): Initial implementation
  - Detects weak LTR wrappers (\textenglish) in fancyhdr context
  - Detects missing LTR wrappers for page numbers
  - Detects header marks without LTR protection

---

**Parent:** qa-super
**Related:** qa-BiDi-detect, qa-cls-version-detect
