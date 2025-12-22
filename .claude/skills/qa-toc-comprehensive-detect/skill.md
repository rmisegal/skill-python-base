---
name: qa-toc-comprehensive-detect
description: Comprehensive TOC detector for Hebrew-English bilingual documents with 66 validation rules (Level 2 skill)
version: 2.5.0
author: QA Team
tags: [qa, toc, detect, level-2, bidi, hebrew, numbering, structure, unnumbered, naked-english, duplicate, layout, gaps, depth-mismatch, entry-direction]
tools: [Read, Grep, Glob]
---

# TOC Comprehensive Detector (Level 2)

## Agent Identity
- **Name:** TOC Comprehensive Detector
- **Role:** Validate Table of Contents in Hebrew-English documents
- **Level:** 2 (Worker Skill)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0)
- qa-BiDi (Level 1) for BiDi-related issues

### Manages
- None (worker skill - detection only)

### Reads
- .toc files (LaTeX TOC output)
- .tex files (for context)
- JSON configuration files

### Writes
- Issue list (in-memory, passed to parent)

## Mission Statement

Detect ALL issues in Table of Contents for Hebrew-English bilingual LaTeX documents. Validates:
- **Numbering:** Continuity, format, gaps, **presence/absence**
- **BiDi Direction:** Numbers, text, parentheticals in LTR/RTL
- **Structure:** Chapters, bibliography, hierarchy
- **Unnumbered Entries:** Detection and classification
- **Validation:** Page numbers, hyperref, formatting

**CRITICAL:** This skill MUST NOT modify any files - detection only.

## Detection Categories (66 Rules Total)

### English Entry Direction Detection (1 rule) - NEW v2.5
| Rule ID | Description | Severity |
|---------|-------------|----------|
| **toc-english-entry-not-ltr** | Purely English TOC entry renders RTL (text + page number reversed) | CRITICAL |

**Problem Example:**
```
RENDERED (wrong):  54 . . . . . . . . secnerefeR hsilgnE
EXPECTED (correct): English References . . . . . . . . 45
```

**Root Cause:**
```latex
% v6.0.0 (broken) - text wrapped, but line still RTL:
\addcontentsline{toc}{subsection}{\textenglish{#1}}%
                                  ^^^^^^^^^^^^^^^
                                  Text is LTR, but LINE is RTL

% v6.1.0 (fixed) - entire line is LTR:
\addcontentsline{toc}{subsection}{\protect\LRE{\textenglish{#1}}}%
                                  ^^^^^^^^^^^^
                                  Line-level LTR embedding
```

**Detection Logic:**
```python
def detect_english_entry_direction(entry):
    """Check if purely-English entries have line-level LTR wrapper."""
    # Check if entry title is purely English (no Hebrew characters)
    if is_purely_english(entry.title):
        # Check if entry uses \LRE{} or equivalent line-level wrapper
        if not has_line_level_ltr(entry.raw_content):
            # Only \textenglish{} is not enough - need \LRE{}
            if r"\textenglish" in entry.raw_content and r"\LRE" not in entry.raw_content:
                return Issue(
                    rule="toc-english-entry-not-ltr",
                    severity="CRITICAL",
                    message="English entry needs \\LRE{} for line-level LTR, not just \\textenglish{}"
                )
    return None
```

**Why This Is Different From `toc-english-text-naked`:**
| Rule | Checks | Problem |
|------|--------|---------|
| `toc-english-text-naked` | Text wrapping (`\textenglish{}`) | Text itself is RTL |
| `toc-english-entry-not-ltr` | Line wrapping (`\LRE{}`) | Text is LTR but line is RTL |

### Numbering Depth Mismatch Detection (3 rules) - NEW v2.4
| Rule ID | Description | Severity |
|---------|-------------|----------|
| **toc-numbering-depth-mismatch** | Entry type doesn't match numbering depth (e.g., X.Y as subsection instead of section) | CRITICAL |
| **toc-section-as-subsection** | Section-level number (X.Y) declared as subsection | CRITICAL |
| **toc-subsection-as-section** | Subsection-level number (X.Y.Z) declared as section | WARNING |

**Problem Example (Chapter 2 - WRONG):**
```
\contentsline {subsection}{\numberline {\textenglish {2.1}}...  ← WRONG! 2.1 should be section
\contentsline {subsection}{\numberline {\LRE {2.1.1}}...       ← OK, 2.1.1 is subsection
\contentsline {subsection}{\numberline {\textenglish {2.2}}...  ← WRONG! 2.2 should be section
```

**Correct Example (Chapter 1 - RIGHT):**
```
\contentsline {section}{\numberline {\LRE {1.1}}...     ← CORRECT! 1.1 is section
\contentsline {subsection}{\numberline {\LRE {1.1.1}}... ← CORRECT! 1.1.1 is subsection
\contentsline {section}{\numberline {\LRE {1.2}}...     ← CORRECT! 1.2 is section
```

**Detection Logic:**
```python
def get_expected_entry_type(number_str):
    """Determine expected entry type based on numbering depth."""
    # Remove any wrapping commands like \LRE{}, \textenglish{}
    clean_num = extract_number(number_str)
    depth = clean_num.count('.') + 1

    # depth 1 = chapter (X)
    # depth 2 = section (X.Y)
    # depth 3 = subsection (X.Y.Z)
    # depth 4 = subsubsection (X.Y.Z.W)

    if depth == 1:
        return "chapter"
    elif depth == 2:
        return "section"
    elif depth == 3:
        return "subsection"
    elif depth >= 4:
        return "subsubsection"
    return None

def detect_depth_mismatch(entry):
    """Detect if entry type matches its numbering depth."""
    expected = get_expected_entry_type(entry.number)
    actual = entry.entry_type

    if expected and actual != expected:
        if expected == "section" and actual == "subsection":
            return Issue(
                rule="toc-section-as-subsection",
                severity="CRITICAL",
                message=f"Number {entry.number} implies section, but declared as subsection"
            )
        elif expected == "subsection" and actual == "section":
            return Issue(
                rule="toc-subsection-as-section",
                severity="WARNING",
                message=f"Number {entry.number} implies subsection, but declared as section"
            )
        else:
            return Issue(
                rule="toc-numbering-depth-mismatch",
                severity="CRITICAL",
                message=f"Expected {expected}, got {actual} for number {entry.number}"
            )
    return None
```

**Why This Matters:**
- Wrong entry type = wrong TOC indentation
- Wrong entry type = missing visual gaps (sections get gaps, subsections don't)
- Indicates structural problem in .tex source file

### Layout & Gap Detection (2 rules) - NEW v2.3
| Rule ID | Description | Severity |
|---------|-------------|----------|
| **toc-section-gap-missing** | Section follows subsection without vertical gap | WARNING |
| **toc-page-number-jump** | Anomalous page jump (>10 pages) within subsection group | WARNING |

**Example - Missing Gap:**
```
2.1.4 המלצות הגנה . . . . . . . . 27   ← subsection
2.2 LLM02: חשיפת מידע רגיש . . . 27   ← section (NO GAP - bad!)

GOOD:
2.1.4 המלצות הגנה . . . . . . . . 27   ← subsection
                                        ← [visual gap]
2.2 LLM02: חשיפת מידע רגיש . . . 27   ← section
```

**Example - Page Jump:**
```
2.1.3 תרחיש התקפה . . . . . . . . 23
2.1.4 המלצות הגנה . . . . . . . . 42   ← Jump of 19 pages! (copy-paste error?)
```

### Duplicate Title Detection (3 rules) - NEW v2.2
| Rule ID | Description | Severity |
|---------|-------------|----------|
| **toc-duplicate-title** | Same title appears with different section numbers | WARNING |
| **toc-sequential-duplicate** | Adjacent entries have identical titles | CRITICAL |
| **toc-similar-title** | Very similar titles (>85% match) | INFO |

**Example:**
```
11.19 English References . . . . . . . . 237  ← DUPLICATE
11.20 English References . . . . . . . . 243  ← DUPLICATE
```

**Detection Logic:** Normalizes titles (removes LaTeX, numbers, case) and groups by content.

### Naked English Detection (1 rule) - NEW v2.1
| Rule ID | Description | Severity |
|---------|-------------|----------|
| **toc-english-text-naked** | English text without LTR wrapper renders RTL (backwards) | CRITICAL |

**Example:**
```
BAD (renders as):  54 . . . . . . . . secnerefeR hsilgnE 11.2
GOOD (correct):    2.11 English References . . . . . . . . 54
```

**Detection Logic:** Finds English words NOT inside `\textenglish{}`, `\LR{}`, `\en{}` wrappers.

### Numbering Rules (8 rules) - UPDATED v2.0
| Rule ID | Description |
|---------|-------------|
| toc-numbering-discontinuous | Section numbering gaps |
| toc-numbering-format-invalid | Invalid X.Y.Z format |
| toc-sources-no-number | Bibliography without number (INFO - expected) |
| toc-chapter-gap | Missing chapter numbers in sequence |
| **toc-chapter-no-numberline** | Chapter entry missing `\numberline{}` (NEW) |
| **toc-section-no-numberline** | Section entry missing `\numberline{}` (NEW) |
| **toc-subsection-no-numberline** | Subsection entry missing `\numberline{}` (NEW) |
| **toc-subsubsection-no-numberline** | Subsubsection entry missing `\numberline{}` (NEW) |

### Unnumbered Entry Rules (4 rules) - NEW v2.0
| Rule ID | Description | Severity |
|---------|-------------|----------|
| toc-unnumbered-chapter-unexpected | Chapter without number (not bib/appendix) | WARNING |
| toc-unnumbered-section-unexpected | Section without number | WARNING |
| toc-unnumbered-entry-expected | Expected unnumbered (bib, front matter) | INFO |
| toc-unnumbered-entry-starred | Starred entry without number | INFO |

### BiDi Number Rules (8 rules)
| Rule ID | Description |
|---------|-------------|
| toc-chapter-number-not-ltr | Chapter number not in LTR |
| toc-section-number-not-ltr | Section number not in LTR |
| toc-page-number-not-ltr | Page number not in LTR |
| toc-percentage-not-ltr | Percentage not in LTR |
| toc-formula-not-ltr | Formula not in math mode |
| toc-symbol-not-ltr | Symbol direction incorrect |

### Parenthetical Rules (8 rules)
| Rule ID | Description |
|---------|-------------|
| toc-parentheses-reversed | () reversed in Hebrew context |
| toc-brackets-reversed | [] reversed in Hebrew context |
| toc-curly-braces-reversed | {} reversed in Hebrew context |
| toc-angle-brackets-reversed | <> reversed in Hebrew context |
| toc-quotes-hebrew-incorrect | Wrong Hebrew quote style |
| toc-nested-parens-bidi | Nested parens with mixed text |
| toc-math-parens-in-hebrew | Math parens without math mode |

### Text Direction Rules (8 rules)
| Rule ID | Description |
|---------|-------------|
| toc-english-text-not-ltr | English without textenglish |
| toc-hebrew-text-not-rtl | Hebrew without texthebrew |
| toc-mixed-heb-eng-heb | Hebrew→English→Hebrew pattern |
| toc-mixed-eng-heb-eng | English→Hebrew→English pattern |
| toc-acronym-not-ltr | Acronym without LTR wrapper |
| toc-url-path-not-ltr | URL/path not in LTR |

### Structure Rules (8 rules)
| Rule ID | Description |
|---------|-------------|
| toc-missing-chapter | Expected chapter not in TOC |
| toc-bibliography-missing | Bibliography not in TOC |
| toc-duplicate-entry | Duplicate TOC entry |
| toc-empty-title | Empty or whitespace title |
| toc-orphan-subsection | Subsection without parent |
| toc-indentation-incorrect | Wrong indentation level |

## Unnumbered Entry Detection Logic (v2.0)

### How We Detect Unnumbered Entries

```
TOC Entry Pattern:
\contentsline {chapter}{\numberline {\LRE {1}}Title...}{page}{anchor}%
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                       NUMBERED - has \numberline{}

\contentsline {chapter}{\texthebrew {מקורות}}{page}{chapter*.32}%
                       ^^^^^^^^^^^^^^^^^^^^
                       UNNUMBERED - NO \numberline{}
```

### Classification Rules

| Entry Contains | hyperref Pattern | Classification |
|----------------|------------------|----------------|
| `\numberline{}` | Any | NUMBERED (normal) |
| No `\numberline{}` | `chapter*.N` | UNNUMBERED-STARRED |
| No `\numberline{}` | `section*.N` | UNNUMBERED-STARRED |
| No `\numberline{}` | Any | UNNUMBERED-UNEXPECTED |
| Title = מקורות/Bibliography | Any | UNNUMBERED-EXPECTED (bib) |
| Title = נספח/Appendix | Any | UNNUMBERED-EXPECTED (appendix) |

### Detection Algorithm

```python
def detect_unnumbered_entries(entries):
    """Detect and classify unnumbered TOC entries."""
    issues = []

    EXPECTED_UNNUMBERED = [
        r"מקורות",           # Hebrew bibliography
        r"bibliography",     # English bibliography
        r"references",       # References
        r"נספח",             # Hebrew appendix
        r"appendix",         # English appendix
        r"תוכן עניינים",    # Table of contents
        r"רשימת",            # List of (figures/tables)
    ]

    for entry in entries:
        has_numberline = r"\numberline" in entry.raw_content
        is_starred = "*." in entry.hyperref

        if not has_numberline:
            # Check if expected unnumbered
            is_expected = any(
                re.search(pattern, entry.title, re.IGNORECASE)
                for pattern in EXPECTED_UNNUMBERED
            )

            if is_expected:
                issues.append(Issue(
                    rule="toc-unnumbered-entry-expected",
                    severity="INFO",
                    message=f"Expected unnumbered: {entry.title}"
                ))
            elif is_starred:
                issues.append(Issue(
                    rule="toc-unnumbered-entry-starred",
                    severity="INFO",
                    message=f"Starred entry: {entry.title}"
                ))
            else:
                # UNEXPECTED - should have number!
                issues.append(Issue(
                    rule=f"toc-{entry.entry_type}-no-numberline",
                    severity="WARNING",
                    message=f"Missing \\numberline in {entry.entry_type}"
                ))

    return issues
```

## Python Tool Integration

```python
from qa_engine.toc import TOCComprehensiveDetector

# Initialize detector
detector = TOCComprehensiveDetector(expected_chapters=11)

# Detect in .toc file
issues = detector.detect_in_file("master/master-main.toc")

# Or detect in content
issues = detector.detect_in_content(toc_content, "master-main.toc")

# Generate report
report = detector.generate_report(issues)

# Get all rules
rules = detector.get_all_rules()  # Returns 56 rules (v2.0)

# NEW v2.0: Get unnumbered entries specifically
unnumbered = detector.get_unnumbered_entries("master/master-main.toc")
for entry in unnumbered:
    print(f"{entry.entry_type}: {entry.title} - {entry.classification}")
```

## Configuration

All rules loaded from JSON configuration files:
- `toc_rules_config.json` - Rule definitions
- `toc_patterns.json` - Regex patterns
- `toc_fixer_mapping.json` - Rule to fixer mapping

**No hardcoded data in Python code.**

## Input/Output Format

### Input
```json
{
  "toc_path": "master/master-main.toc",
  "expected_chapters": 11
}
```

### Output
```json
{
  "summary": {
    "total_issues": 5,
    "critical": 2,
    "warning": 2,
    "info": 1
  },
  "issues": [
    {
      "rule": "toc-chapter-number-not-ltr",
      "file": "master-main.toc",
      "line": 32,
      "content": "Chapter 1 not wrapped",
      "severity": "CRITICAL",
      "fix": "Run skill: qa-BiDi-fix-toc-config | Use fixer: TOCFixer"
    }
  ]
}
```

## Fixer Recommendations

Each detected issue includes fix recommendations:

| Rule Category | Recommended Fixer/Skill |
|---------------|------------------------|
| Number direction | TOCFixer, qa-BiDi-fix-toc-config |
| Text direction | BiDiFixer, qa-BiDi-fix-text |
| Parentheticals | qa-BiDi-fix-text (manual) |
| Structure | Manual fix required |
| **Depth mismatch** | **Fix .tex source: change `\subsection` to `\section` (v2.4)** |

## Execution Workflow

1. Parse .toc file into structured entries
2. Run numbering detector
3. **Run depth mismatch detector (NEW v2.4)**
4. Run BiDi detector (numbers, text, parentheticals)
5. Run structure detector
6. Deduplicate issues
7. Generate report with fix recommendations

## Example Detection Output (v2.0)

Given this TOC content:
```latex
\contentsline {chapter}{\numberline {\LRE {1}}מבוא...}{1}{chapter.1}%
\contentsline {chapter}{\texthebrew {מקורות}}{15}{chapter*.32}%
\contentsline {subsubsection}{הגדרה}{54}{subsubsection*.96}%
```

The detector will output:
```json
{
  "issues": [
    {
      "rule": "toc-unnumbered-entry-expected",
      "severity": "INFO",
      "line": 2,
      "content": "מקורות",
      "message": "Expected unnumbered: Bibliography section",
      "classification": "BIBLIOGRAPHY"
    },
    {
      "rule": "toc-subsubsection-no-numberline",
      "severity": "WARNING",
      "line": 3,
      "content": "הגדרה",
      "message": "Subsubsection missing \\numberline{} wrapper",
      "fix": "Check source .tex file for missing counter"
    }
  ],
  "summary": {
    "total_entries": 3,
    "numbered": 1,
    "unnumbered_expected": 1,
    "unnumbered_unexpected": 1
  }
}
```

## Version History
- **v2.5.0** (2025-12-21): Added English entry direction detection
  - NEW: `toc-english-entry-not-ltr` - Detects purely English TOC entries that render RTL (CRITICAL)
  - Root cause: `\textenglish{}` wraps text but entire TOC line still renders RTL
  - Symptom: "54...secnerefeR hsilgnE" instead of "English References...45"
  - Solution: CLS v6.1.0 uses `\protect\LRE{\textenglish{#1}}` for line-level LTR
  - Distinguishes from `toc-english-text-naked` (text-level) vs this rule (line-level)
  - Total rules: 66 (was 65)
- **v2.4.0** (2025-12-21): Added numbering depth mismatch detection
  - NEW: `toc-numbering-depth-mismatch` - Entry type doesn't match numbering depth (CRITICAL)
  - NEW: `toc-section-as-subsection` - Section-level number (X.Y) declared as subsection (CRITICAL)
  - NEW: `toc-subsection-as-section` - Subsection-level number (X.Y.Z) declared as section (WARNING)
  - Detects structural problems where section commands don't match numbering hierarchy
  - Root cause: Chapter 2 uses `\subsection` for items numbered 2.1, 2.2, etc. instead of `\section`
  - This causes missing visual gaps in TOC because subsections don't get vertical spacing
  - Total rules: 65 (was 62)
- **v2.3.0** (2025-12-21): Added layout and gap detection
  - NEW: `toc-section-gap-missing` - Detects missing vertical gaps before sections (WARNING)
  - NEW: `toc-page-number-jump` - Detects anomalous page jumps within subsection groups (WARNING)
  - Helps identify visual hierarchy issues and copy-paste errors
  - Threshold: 10+ pages jump triggers warning
- **v2.2.0** (2025-12-21): Added duplicate title detection
  - NEW: `toc-duplicate-title` - Same title with different numbers (WARNING)
  - NEW: `toc-sequential-duplicate` - Adjacent identical titles (CRITICAL)
  - NEW: `toc-similar-title` - Very similar titles >85% match (INFO)
  - Normalizes titles for comparison (removes LaTeX, numbers, case)
- **v2.1.0** (2025-12-21): Added naked English detection
  - NEW: `toc-english-text-naked` - Detects English text that will render RTL (CRITICAL)
  - Finds English words not wrapped in `\textenglish{}`, `\LR{}`, `\en{}`
  - Example: "English References" → "secnerefeR hsilgnE" when not wrapped
- **v2.0.0** (2025-12-21): Added unnumbered entry detection with 8 new rules
  - NEW: `toc-chapter-no-numberline` - Detects chapters without `\numberline{}`
  - NEW: `toc-section-no-numberline` - Detects sections without `\numberline{}`
  - NEW: `toc-subsection-no-numberline` - Detects subsections without `\numberline{}`
  - NEW: `toc-subsubsection-no-numberline` - Detects subsubsections without `\numberline{}`
  - NEW: `toc-unnumbered-chapter-unexpected` - Flags unexpected unnumbered chapters
  - NEW: `toc-unnumbered-section-unexpected` - Flags unexpected unnumbered sections
  - NEW: `toc-unnumbered-entry-expected` - Classifies expected unnumbered (bib, appendix)
  - NEW: `toc-unnumbered-entry-starred` - Classifies starred entries
  - FIX: Now properly detects "מקורות" without number as expected behavior
- **v1.0.0** (2025-12-21): Initial implementation with 48 rules

---

**Parent:** qa-super
**Related:** qa-BiDi, qa-BiDi-fix-toc-config, qa-BiDi-fix-text
**Configuration:** src/qa_engine/toc/config/*.json
