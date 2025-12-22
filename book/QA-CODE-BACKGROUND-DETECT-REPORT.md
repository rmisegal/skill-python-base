# QA-CODE-BACKGROUND-DETECT Report

**Book:** AI Tools in Business (כלי בינה מלאכותית בעסקים)
**Date:** 2025-12-15
**Skill:** qa-code-background-detect v1.1
**Document Type:** RTL Hebrew (hebrew-academic-template.cls v5.11.2)

---

## Executive Summary

```
┌─────────────────────────────────────────────────────────┐
│  QA-CODE-BACKGROUND-DETECT RESULT: ✓ PASS              │
├─────────────────────────────────────────────────────────┤
│  pythonbox total:     2                                 │
│  pythonbox wrapped:   2                                 │
│  pythonbox unwrapped: 0                                 │
│  tcolorbox found:     0                                 │
│  tcblisting found:    0                                 │
│  Issues detected:     0                                 │
└─────────────────────────────────────────────────────────┘
```

**Verdict:** All code environments with tcolorbox backgrounds are correctly wrapped with `\begin{english}...\end{english}`.

---

## Book Coverage Checklist

| # | Component | File | pythonbox | tcolorbox | tcblisting | Status |
|---|-----------|------|-----------|-----------|------------|--------|
| 0 | **Cover Page** | `main.tex` | 0 | 0 | 0 | **PASS** |
| 1 | Chapter 01 | `chapter-01.tex` | 0 | 0 | 0 | **PASS** |
| 2 | Chapter 02 | `chapter-02.tex` | 2 (wrapped) | 0 | 0 | **PASS** |
| 3 | Chapter 03 | `chapter-03.tex` | 0 | 0 | 0 | **PASS** |
| 4 | Chapter 04 | `chapter-04.tex` | 0 | 0 | 0 | **PASS** |
| 5 | Chapter 05 | `chapter-05.tex` | 0 | 0 | 0 | **PASS** |
| 6 | Chapter 06 | `chapter-06.tex` | 0 | 0 | 0 | **PASS** |
| 7 | Chapter 07 | `chapter-07.tex` | 0 | 0 | 0 | **PASS** |
| 8 | Chapter 08 | `chapter-08.tex` | 0 | 0 | 0 | **PASS** |
| 9 | Chapter 09 | `chapter-09.tex` | 0 | 0 | 0 | **PASS** |
| 10 | Chapter 10 | `chapter-10.tex` | 0 | 0 | 0 | **PASS** |
| 11 | Chapter 11 | `chapter-11.tex` | 0 | 0 | 0 | **PASS** |
| 12 | Chapter 12 | `chapter-12.tex` | 0 | 0 | 0 | **PASS** |
| 13 | Chapter 13 | `chapter-13.tex` | 0 | 0 | 0 | **PASS** |

**Total Components Checked:** 14/14

---

## Detailed Findings

### Chapter 02: chapter-02.tex

Two `pythonbox*` environments found, both correctly wrapped:

#### Instance 1 (Line 655) - ✓ WRAPPED
```latex
% Line 654:
\begin{english}
% Line 655:
\begin{pythonbox*}[\hebtitle{השוואת מחירי API}]
```
**Status:** PASS - `\begin{english}` on immediate previous line (654)

#### Instance 2 (Line 728) - ✓ WRAPPED
```latex
% Line 727:
\begin{english}
% Line 728:
\begin{pythonbox*}[\hebtitle{בדיקת \en{Latency} של מודלים}]
```
**Status:** PASS - `\begin{english}` on immediate previous line (727)

---

## Other Code Environments (Not Affected)

The book uses `lstlisting` environments extensively for code blocks. These are NOT affected by the background overflow issue because `lstlisting` (from the `listings` package) does not use tcolorbox's background rendering system.

| Chapter | lstlisting Count | Background Issue |
|---------|------------------|------------------|
| chapter-01 | 1 | N/A (listings package) |
| chapter-04 | 5 | N/A (listings package) |
| chapter-06 | 9 | N/A (listings package) |
| chapter-08 | 17 | N/A (listings package) |
| chapter-10 | 4 | N/A (listings package) |
| chapter-11 | 15 | N/A (listings package) |
| chapter-12 | 3 | N/A (listings package) |
| chapter-13 | 3 | N/A (listings package) |

**Note:** lstlisting environments do not require `\begin{english}` wrapper for background rendering.

---

## Detection Criteria Applied

### Environments Checked (tcolorbox-based)
- ✓ `\begin{pythonbox}` - Custom environment using tcolorbox
- ✓ `\begin{pythonbox*}` - Starred variant
- ✓ `\begin{tcolorbox}` - Direct tcolorbox usage
- ✓ `\begin{tcblisting}` - tcolorbox listing environment

### Environments NOT Checked (Not tcolorbox-based)
- `\begin{lstlisting}` - Uses listings package (different rendering)
- `\begin{minted}` - Uses minted package (not found in book)
- `\begin{verbatim}` - Plain TeX environment

---

## Technical Notes

### Why english Wrapper is Required

In RTL (Hebrew) documents, tcolorbox renders backgrounds based on text direction:
- The box calculates position using RTL coordinates
- This causes background to extend RIGHT, outside the page margin
- Wrapping in `\begin{english}...\end{english}` forces LTR rendering for the box background

### CLS-Level Fix is Insufficient

The `hebrew-academic-template.cls` includes:
```latex
before upper={\selectlanguage{english}\setLTR}
```

This only sets text direction INSIDE the box, but the **background** is still rendered in RTL context. Each pythonbox must be wrapped at the document level.

---

## JSON Output

```json
{
  "skill": "qa-code-background-detect",
  "status": "DONE",
  "verdict": "PASS",
  "document_type": "RTL_HEBREW",
  "cls_version": "5.11.2",
  "pythonbox_total": 2,
  "pythonbox_wrapped": 2,
  "pythonbox_unwrapped": 0,
  "tcolorbox_total": 0,
  "tcblisting_total": 0,
  "issues_found": 0,
  "components_checked": 14,
  "details": [
    {
      "file": "chapters/chapter-02.tex",
      "line": 655,
      "environment": "pythonbox*",
      "title": "השוואת מחירי API",
      "has_english_wrapper": true,
      "wrapper_line": 654,
      "status": "PASS"
    },
    {
      "file": "chapters/chapter-02.tex",
      "line": 728,
      "environment": "pythonbox*",
      "title": "בדיקת Latency של מודלים",
      "has_english_wrapper": true,
      "wrapper_line": 727,
      "status": "PASS"
    }
  ],
  "triggers": []
}
```

---

## Recommendations

**No action required.** All pythonbox environments are correctly wrapped.

For future additions:
1. Always wrap new `pythonbox` environments with `\begin{english}...\end{english}`
2. The wrapper must be on the **immediate previous line** (not just nearby)
3. Use the qa-code-background-detect skill to verify before compilation

---

**Report Generated:** 2025-12-15
**Skill Version:** qa-code-background-detect v1.1
**Parent Orchestrator:** qa-code (Level 1)
