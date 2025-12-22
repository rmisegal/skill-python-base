# BC Skills Upgrade Plan for QA Alignment

## Executive Summary

This document provides a detailed plan for upgrading the 6 BC (Book Creator) skills to ensure full alignment with the QA (Quality Assurance) mechanism. The goal is **zero QA errors** when running `qa-super` after content creation with BC skills.

**Approach:** Every LaTeX command, pattern, and rule in BC skills must be synchronized with QA detection patterns to ensure "write once, pass always."

---

## 1. Cross-Reference Analysis: BC Commands vs QA Detection Patterns

### 1.1 BiDi Rules Cross-Reference (15 QA Rules)

| QA Rule ID | QA Detection Pattern | BC Skill Coverage | Alignment Status |
|------------|---------------------|-------------------|------------------|
| `bidi-numbers` | `\d+` without `\en{}`, `\num{}`, `\hebyear{}` | bc-math: `\num{123}`, `\hebyear{2025}` | **PARTIAL** - missing `\percent{}` |
| `bidi-english` | `[a-zA-Z]{2,}` without `\en{}` | bc-math: `\en{English}` | **PARTIAL** - needs stronger enforcement |
| `bidi-acronym` | `[A-Z]{2,6}` without `\en{}` | NOT MENTIONED | **GAP** - no BC coverage |
| `bidi-year-range` | `\d{4}-\d{4}` without wrapper | bc-math: mentions years | **PARTIAL** - year range not explicit |
| `bidi-tikz-rtl` | `\begin{tikzpicture}` without `english` wrapper | NOT MENTIONED | **CRITICAL GAP** |
| `bidi-tcolorbox` | `\begin{tcolorbox}` without `english` wrapper | bc-code: uses pythonbox | **UNCLEAR** - wrapper needed? |
| `bidi-section-english` | English in `\section{Hebrew}` | bc-architect: `\hebrewsection{}` | **ALIGNED** |
| `bidi-chapter-label` | `\label` after `\hebrewchapter` | NOT MENTIONED | **GAP** |
| `bidi-fbox-mixed` | Mixed content in fbox/parbox | NOT MENTIONED | **GAP** |
| `bidi-standalone-counter` | subfiles without counter setup | NOT MENTIONED | **GAP** |
| `bidi-missing-hebrewchapter` | Missing hebrewchapter counter | NOT MENTIONED | **CRITICAL GAP** |
| `bidi-hebrew-in-english` | Hebrew inside `\en{}` | NOT MENTIONED | **GAP** |
| `bidi-reversed-text` | Final letters at word start | bc-hebrew implicitly | **PARTIAL** |
| `bidi-header-footer` | Hebrew in fancyhdr | NOT MENTIONED | **GAP** |
| `bidi-cover-metadata` | Unwrapped Hebrew in preamble | NOT MENTIONED | **GAP** |

### 1.2 Code Rules Cross-Reference (5 QA Rules)

| QA Rule ID | QA Detection Pattern | BC Skill Coverage | Alignment Status |
|------------|---------------------|-------------------|------------------|
| `code-background-overflow` | `\begin{pythonbox}` without english wrapper | bc-code: mandates pythonbox | **CRITICAL MISALIGNMENT** |
| `code-direction-hebrew` | Hebrew `[א-ת]` in code block | bc-code: "English only comments" | **PARTIAL** - detection not explicit |
| `code-hebrew-content` | Hebrew in comments/strings | bc-code: "English comments" | **ALIGNED** (intent) |
| `code-encoding-emoji` | Emoji characters in code | NOT MENTIONED | **GAP** |
| `code-fstring-brace` | F-string braces outside code | NOT MENTIONED | **GAP** |

### 1.3 Table Rules Cross-Reference (10 QA Rules)

| QA Rule ID | QA Detection Pattern | BC Skill Coverage | Alignment Status |
|------------|---------------------|-------------------|------------------|
| `table-no-rtl-env` | `\begin{tabular}` without rtltabular | bc-academic-source: `\begin{rtltabular}` | **ALIGNED** |
| `table-not-hebrewtable` | `\begin{table}` instead of hebrewtable | bc-academic-source: `\begin{hebrewtable}` | **ALIGNED** |
| `table-cell-hebrew` | `& [Hebrew] &` without wrapper | bc-academic-source: `\hebcell{}` | **CHECK NEEDED** - verify wrapper match |
| `table-overflow` | Wide table without resizebox | NOT MENTIONED | **GAP** |
| `table-missing-header-color` | No `\rowcolor{blue!15}` | NOT MENTIONED | **GAP** |
| `table-caption-position` | Caption before table | NOT MENTIONED | **GAP** |
| `caption-setup-raggedleft` | Wrong justification | NOT MENTIONED | **GAP** |
| `table-plain-unstyled` | Plain tabular without styling | bc-academic-source: fancy styling | **ALIGNED** |

### 1.4 Bibliography Rules Cross-Reference (5 QA Rules)

| QA Rule ID | QA Detection Pattern | BC Skill Coverage | Alignment Status |
|------------|---------------------|-------------------|------------------|
| `bib-malformed-cite-key` | LaTeX in cite key | NOT MENTIONED | **GAP** |
| `bib-missing-file` | Missing .bib file | bc-source-research creates BibTeX | **ALIGNED** |
| `bib-undefined-cite` | Undefined citation | bc-academic-source verifies sources | **ALIGNED** (intent) |
| `bib-empty-cite` | Empty `\cite{}` | NOT MENTIONED | **GAP** |
| `bib-standalone-missing` | Subfile without biblatex | NOT MENTIONED | **CRITICAL GAP** |

### 1.5 Hebrew Math Rules Cross-Reference (5 QA Rules)

| QA Rule ID | QA Detection Pattern | BC Skill Coverage | Alignment Status |
|------------|---------------------|-------------------|------------------|
| `heb-math-text` | Hebrew in `\text{}` without `\hebmath{}` | bc-math: `\ilm{}` only | **CRITICAL GAP** |
| `heb-math-textbf` | Hebrew in `\textbf{}` in math | NOT MENTIONED | **GAP** |
| `heb-math-subscript` | Hebrew in subscript | NOT MENTIONED | **GAP** |
| `heb-math-superscript` | Hebrew in superscript | NOT MENTIONED | **GAP** |
| `heb-math-cases` | Hebrew in cases environment | NOT MENTIONED | **GAP** |

### 1.6 Caption/Image Rules Cross-Reference

| QA Rule ID | QA Detection Pattern | BC Skill Coverage | Alignment Status |
|------------|---------------------|-------------------|------------------|
| `caption-too-long` | Caption > 100 chars without short title | NOT MENTIONED | **GAP** |
| `img-file-not-found` | Missing image file | bc-architect references figures | **PARTIAL** |
| `img-no-size-spec` | No width/height on image | NOT MENTIONED | **GAP** |

---

## 2. Critical Gaps Summary

### 2.1 CRITICAL Priority (Must Fix First)

| Gap ID | Description | BC Skill | QA Rule | Impact |
|--------|-------------|----------|---------|--------|
| **GAP-C1** | pythonbox needs english wrapper | bc-code | code-background-overflow | Every code block fails QA |
| **GAP-C2** | TikZ needs english wrapper | bc-code | bidi-tikz-rtl | Every diagram fails QA |
| **GAP-C3** | Missing `\hebmath{}` for Hebrew in math | bc-math | heb-math-* | Math with Hebrew fails QA |
| **GAP-C4** | Subfile counter setup missing | bc-architect | bidi-missing-hebrewchapter | Numbering errors |
| **GAP-C5** | Standalone biblatex config | bc-academic-source | bib-standalone-missing | Citations fail in standalone |

### 2.2 HIGH Priority

| Gap ID | Description | BC Skill | QA Rule | Impact |
|--------|-------------|----------|---------|--------|
| **GAP-H1** | Acronyms need `\en{}` | ALL | bidi-acronym | Every acronym in Hebrew fails |
| **GAP-H2** | Table header color missing | bc-academic-source | table-missing-header-color | Tables lack styling |
| **GAP-H3** | Caption short title needed | bc-architect | caption-too-long | LOF/LOT cluttered |
| **GAP-H4** | Year ranges need wrapper | ALL | bidi-year-range | Date ranges render wrong |
| **GAP-H5** | Wide table resizebox | bc-academic-source | table-overflow | Overfull hbox warnings |

### 2.3 MEDIUM Priority

| Gap ID | Description | BC Skill | QA Rule | Impact |
|--------|-------------|----------|---------|--------|
| **GAP-M1** | Emoji in code | bc-code | code-encoding-emoji | Font warnings |
| **GAP-M2** | Empty cite detection | ALL | bib-empty-cite | Empty citations |
| **GAP-M3** | Image size spec | bc-architect | img-no-size-spec | Inconsistent sizing |
| **GAP-M4** | Caption position | bc-academic-source | table-caption-position | RTL convention |
| **GAP-M5** | Label after hebrewchapter | bc-architect | bidi-chapter-label | Reference issues |

---

## 3. Detailed Upgrade Plan per BC Skill

### 3.1 bc-code Upgrade Plan

#### Current State
```latex
\begin{pythonbox}[כותרת הקוד בעברית]
import numpy as np
# English comment
\end{pythonbox}
```

#### Target State (QA-Compliant)
```latex
\begin{english}
\begin{pythonbox}[כותרת הקוד בעברית]
import numpy as np
# English comment - NO Hebrew allowed
# NO emoji characters (e.g., no 🔥 or 📊)
\end{pythonbox}
\end{english}
```

#### Required Changes

| Section | Current | Required Change | QA Rule Addressed |
|---------|---------|-----------------|-------------------|
| Environment | `\begin{pythonbox}` | Wrap in `\begin{english}...\end{english}` | code-background-overflow |
| Comments | "English only" | Add: "NO Hebrew characters allowed" | code-direction-hebrew |
| Emoji | Not mentioned | Add: "NO emoji characters in code" | code-encoding-emoji |
| TikZ | Not mentioned | Add: TikZ section requiring `\begin{english}` | bidi-tikz-rtl |
| tcolorbox | Not mentioned | Add: All tcolorbox must be in english env | bidi-tcolorbox |

#### New Section to Add: "TikZ and Diagrams"
```markdown
### TikZ Environment Requirements (MANDATORY)
All TikZ diagrams MUST be wrapped in english environment:

\begin{english}
\begin{tikzpicture}
  % diagram code here
\end{tikzpicture}
\end{english}

**QA Rule:** bidi-tikz-rtl - TikZ without english wrapper fails QA
```

### 3.2 bc-math Upgrade Plan

#### Current State
```latex
\ilm{$math expression$}
\en{English Text}
\num{123}
\hebyear{2025}
```

#### Target State (QA-Compliant)
```latex
\ilm{$math expression$}                    % Math only
\en{English Text}                          % Any English word ≥2 chars
\en{MCP}                                   % Acronyms (2-6 uppercase)
\en{2025-2026}                             % Year ranges
\num{123}                                  % Numbers
\percent{45}                               % Percentages (ADD THIS)
\hebyear{2025}                             % Single years
\hebmath{טקסט עברי}                        % Hebrew IN math mode (ADD THIS)
```

#### Required Changes

| Section | Current | Required Change | QA Rule Addressed |
|---------|---------|-----------------|-------------------|
| Commands | `\num{}`, `\hebyear{}` | Add `\percent{}` | bidi-numbers |
| Acronyms | Not mentioned | Add: "Wrap `[A-Z]{2,6}` with `\en{}`" | bidi-acronym |
| Year Ranges | Not explicit | Add: "Wrap `YYYY-YYYY` with `\en{}` or `\hebyear{}`" | bidi-year-range |
| Hebrew Math | Not mentioned | Add: "Use `\hebmath{}` for Hebrew in math" | heb-math-* |
| Subscripts | Not mentioned | Add: "Use `\hebsub{}` for Hebrew subscripts" | heb-math-subscript |

#### New Section to Add: "Hebrew in Math Mode"
```markdown
### Hebrew in Math Mode (MANDATORY)

When Hebrew text appears INSIDE math mode, use these commands:

| Situation | Command | Example |
|-----------|---------|---------|
| Hebrew text in math | `\hebmath{טקסט}` | `$P(\hebmath{חיובי})$` |
| Hebrew subscript | `$x_{\hebsub{חיובי}}$` | Subscript text |
| Hebrew superscript | `$y^{\hebmath{ראשון}}$` | Superscript text |
| Hebrew in cases | `\hebmath{}` | Within cases environment |

**DO NOT USE:** `\text{Hebrew}` - this renders LTR incorrectly!
**QA Rules:** heb-math-text, heb-math-subscript, heb-math-superscript
```

#### New Section to Add: "Acronyms and Abbreviations"
```markdown
### Acronyms (MANDATORY)

ALL uppercase acronyms (2-6 letters) MUST be wrapped:

**VIOLATION:** `פרוטוקול MCP מאפשר` → Renders as PCM
**CORRECT:** `פרוטוקול \en{MCP} מאפשר` → Renders correctly

**QA Rule:** bidi-acronym - Pattern: `[A-Z]{2,6}` without `\en{}`
```

### 3.3 bc-academic-source Upgrade Plan

#### Current State
```latex
\begin{hebrewtable}
\caption{תיאור הטבלה}
\begin{rtltabular}{m{3cm}|m{4cm}|m{3cm}}
\hline
\textbf{\hebheader{עמודה 3}} & \textbf{\hebheader{עמודה 2}} & ...
```

#### Target State (QA-Compliant)
```latex
\begin{hebrewtable}
\begin{rtltabular}{m{3cm}|m{4cm}|m{3cm}}
\hline
\rowcolor{blue!15}  % MANDATORY header styling
\textbf{\hebheader{עמודה 3}} & \textbf{\hebheader{עמודה 2}} & ...
\hline
\hebcell{תוכן} & \encell{English} & ...
\end{rtltabular}
\caption{תיאור הטבלה}  % Caption AFTER table in RTL
\end{hebrewtable}
```

#### Required Changes

| Section | Current | Required Change | QA Rule Addressed |
|---------|---------|-----------------|-------------------|
| Header Color | Not mentioned | Add: `\rowcolor{blue!15}` on first row | table-missing-header-color |
| Caption Position | Before table | Move AFTER table content | table-caption-position |
| Wide Tables | Not mentioned | Add: Wrap wide tables with `\resizebox` | table-overflow |
| Cell Wrappers | `\hebcell{}`, `\encell{}` | Verify these satisfy QA patterns | table-cell-hebrew |
| Empty Cite | Not mentioned | Add: "Never use empty `\cite{}`" | bib-empty-cite |
| Cite Keys | Not mentioned | Add: "No LaTeX commands in cite keys" | bib-malformed-cite-key |
| Standalone Bib | Not mentioned | Add: Biblatex config for standalone | bib-standalone-missing |

#### New Section to Add: "Table Header Styling"
```markdown
### Table Header Styling (MANDATORY)

First row after `\hline` MUST include:
```latex
\rowcolor{blue!15}
```

**QA Rule:** table-missing-header-color
```

#### New Section to Add: "Wide Table Handling"
```markdown
### Wide Tables (>6 columns)

Tables with many columns MUST be wrapped:
```latex
\resizebox{\textwidth}{!}{
\begin{rtltabular}{...}
...
\end{rtltabular}
}
```

**QA Rule:** table-overflow - Pattern detects >6 column specs
```

### 3.4 bc-architect Upgrade Plan

#### Current State
```latex
\hebrewchapter{Title}
\hebrewsection{Title}
\hebrewsubsection{Title}
איור~\ref{fig:example}
טבלה~\ref{tab:example}
```

#### Target State (QA-Compliant)
```latex
% Standalone chapter file header:
\setcounter{chapter}{N}
\setcounter{hebrewchapter}{N}  % CRITICAL - must match!

\hebrewchapter{Title}
% \label{} goes INSIDE or use \refstepcounter BEFORE

\hebrewsection{Title with \en{English Terms}}

% Figures with short captions:
\caption[Short title for LOF]{Full detailed caption explaining the figure}

% References:
איור~\ref{fig:example}
```

#### Required Changes

| Section | Current | Required Change | QA Rule Addressed |
|---------|---------|-----------------|-------------------|
| Chapter Counter | Not mentioned | Add: `\setcounter{hebrewchapter}{N}` | bidi-missing-hebrewchapter |
| Label Position | Not mentioned | Add: Don't put `\label` right after `\hebrewchapter` | bidi-chapter-label |
| Caption Length | Not mentioned | Add: Short title for captions >100 chars | caption-too-long |
| Image Size | Not mentioned | Add: Always specify width/height | img-no-size-spec |
| Section English | Mentioned | Strengthen: "ALWAYS wrap English in `\en{}`" | bidi-section-english |

#### New Section to Add: "Standalone Chapter Setup"
```markdown
### Standalone Chapter Counter Setup (MANDATORY)

Every standalone chapter file MUST include BOTH counters:
```latex
\setcounter{chapter}{N}         % Standard LaTeX counter
\setcounter{hebrewchapter}{N}   % Hebrew chapter counter - CRITICAL!
```

**Without hebrewchapter:** Sections will be numbered wrong (1.1, 1.2 instead of N.1, N.2)
**QA Rule:** bidi-missing-hebrewchapter - CRITICAL severity
```

#### New Section to Add: "Caption Short Titles"
```markdown
### Caption Short Titles (MANDATORY for long captions)

If caption exceeds 100 characters, use short title:
```latex
% VIOLATION:
\caption{This is a very long caption that explains everything about the figure...}

% CORRECT:
\caption[Architecture Overview]{This is a very long caption that explains everything...}
```

**QA Rule:** caption-too-long - Max 100 chars without short title
```

### 3.5 bc-hebrew Upgrade Plan

#### Current State
- Full writing (ktiv male)
- Academy terminology
- Hebrew punctuation fonts

#### Target State (QA-Compliant)
- All current rules PLUS:
- Detect reversed text (final letters at start)
- Ensure no Hebrew inside `\en{}` wrappers
- Verify year ranges are wrapped

#### Required Changes

| Section | Current | Required Change | QA Rule Addressed |
|---------|---------|-----------------|-------------------|
| Reversed Text | Implicit | Add explicit detection rule | bidi-reversed-text |
| Hebrew in English | Not mentioned | Add: "Never put Hebrew inside `\en{}`" | bidi-hebrew-in-english |
| Year Ranges | Not explicit | Add: "Wrap `YYYY-YYYY` with `\en{}`" | bidi-year-range |

### 3.6 bc-source-research Upgrade Plan

#### Current State
- BibTeX entry creation
- DOI/URL fields
- Source summaries

#### Target State (QA-Compliant)
- Clean citation keys (no LaTeX)
- Complete BibTeX fields
- IEEE format compliance

#### Required Changes

| Section | Current | Required Change | QA Rule Addressed |
|---------|---------|-----------------|-------------------|
| Cite Keys | Not specified | Add: "Keys must be alphanumeric only - no `\en{}`, `\hebyear{}`" | bib-malformed-cite-key |

---

## 4. Implementation Phases

### Phase 1: CRITICAL Fixes (Immediate)

#### Step 1.1: Update bc-code (GAP-C1, GAP-C2)
```markdown
File: .claude/skills/bc-code/skill.md

CHANGES:
1. Line ~41: Change pythonbox template to include english wrapper
2. Add new section: "TikZ and Diagrams" with english wrapper requirement
3. Add: "NO emoji characters in code blocks"
```

#### Step 1.2: Update bc-math (GAP-C3)
```markdown
File: .claude/skills/bc-math/skill.md

CHANGES:
1. Add command table entry for \hebmath{}
2. Add new section: "Hebrew in Math Mode"
3. Add new section: "Acronyms" with \en{} requirement
```

#### Step 1.3: Update bc-architect (GAP-C4)
```markdown
File: .claude/skills/bc-architect/skill.md

CHANGES:
1. Add new section: "Standalone Chapter Counter Setup"
2. Add: Both chapter and hebrewchapter counters MUST be set
```

#### Step 1.4: Update bc-academic-source (GAP-C5)
```markdown
File: .claude/skills/bc-academic-source/skill.md

CHANGES:
1. Add new section: "Standalone Biblatex Configuration"
2. Add: Subfiles must include biblatex setup for standalone compilation
```

### Phase 2: HIGH Priority Fixes

#### Step 2.1: All Skills - Acronym Wrapper (GAP-H1)
Add to ALL BC skills:
```markdown
### Acronym Rule (MANDATORY)
ALL uppercase acronyms (2-6 letters) in Hebrew context MUST use \en{}:
- MCP → \en{MCP}
- API → \en{API}
- LLM → \en{LLM}

**QA Rule:** bidi-acronym
```

#### Step 2.2: bc-academic-source - Table Styling (GAP-H2, GAP-H5)
```markdown
CHANGES:
1. Add \rowcolor{blue!15} requirement
2. Add \resizebox{} requirement for wide tables
3. Move caption position guidance (after table)
```

#### Step 2.3: bc-architect - Caption Short Titles (GAP-H3)
```markdown
CHANGES:
1. Add caption length limit (100 chars)
2. Add \caption[short]{long} pattern requirement
```

#### Step 2.4: All Skills - Year Range Wrapper (GAP-H4)
Add to relevant skills:
```markdown
### Year Ranges (MANDATORY)
Year ranges in Hebrew context MUST be wrapped:
- 2025-2026 → \en{2025-2026}

**QA Rule:** bidi-year-range
```

### Phase 3: MEDIUM Priority Fixes

- Add emoji restriction to bc-code
- Add empty cite warning
- Add image size recommendation
- Add caption position clarification
- Add label position guidance

---

## 5. Verification Checklist

After implementing upgrades, verify each BC skill with these tests:

### 5.1 bc-code Verification
- [ ] pythonbox wrapped in english environment
- [ ] No Hebrew characters in code (except in string literals if needed)
- [ ] No emoji characters in code
- [ ] TikZ diagrams wrapped in english environment
- [ ] tcolorbox environments wrapped in english

### 5.2 bc-math Verification
- [ ] All English words ≥2 chars wrapped in `\en{}`
- [ ] All acronyms (2-6 uppercase) wrapped in `\en{}`
- [ ] All year ranges wrapped in `\en{}` or `\hebyear{}`
- [ ] All numbers wrapped in `\en{}`, `\num{}`, or `\percent{}`
- [ ] Hebrew in math mode uses `\hebmath{}`
- [ ] Hebrew subscripts use `\hebsub{}`

### 5.3 bc-academic-source Verification
- [ ] Tables use `\begin{hebrewtable}` not `\begin{table}`
- [ ] Tables use `\begin{rtltabular}` not `\begin{tabular}`
- [ ] Header row has `\rowcolor{blue!15}`
- [ ] Wide tables wrapped with `\resizebox{}`
- [ ] Caption placed AFTER table content
- [ ] Citation keys are alphanumeric only
- [ ] No empty `\cite{}` commands
- [ ] Standalone files have biblatex config

### 5.4 bc-architect Verification
- [ ] Standalone files set BOTH chapter and hebrewchapter counters
- [ ] `\label{}` not immediately after `\hebrewchapter{}`
- [ ] Long captions (>100 chars) have short title
- [ ] All images have width/height specification
- [ ] All section English wrapped in `\en{}`

### 5.5 bc-hebrew Verification
- [ ] No reversed text (final letters at word start)
- [ ] No Hebrew inside `\en{}` wrappers
- [ ] Year ranges wrapped properly

### 5.6 bc-source-research Verification
- [ ] BibTeX keys alphanumeric only
- [ ] No LaTeX commands in cite keys

---

## 6. QA Rules Quick Reference

### 6.1 Commands That Satisfy BiDi Rules

| Content Type | QA-Approved Commands | Example |
|--------------|---------------------|---------|
| English word | `\en{}`, `\textenglish{}` | `\en{Python}` |
| Number | `\en{}`, `\num{}`, `\percent{}` | `\num{42}` |
| Year | `\hebyear{}`, `\en{}` | `\hebyear{2025}` |
| Year range | `\en{}`, `\hebyear{}` | `\en{2025-2026}` |
| Acronym | `\en{}` | `\en{API}` |
| Math inline | `\ilm{$...$}` | `\ilm{$x=5$}` |
| Hebrew in math | `\hebmath{}` | `\hebmath{חיובי}` |

### 6.2 Environments That Need english Wrapper

| Environment | Wrapper Required |
|-------------|-----------------|
| `pythonbox` | `\begin{english}...\end{english}` |
| `pythonbox*` | `\begin{english}...\end{english}` |
| `tikzpicture` | `\begin{english}...\end{english}` |
| `tcolorbox` | `\begin{english}...\end{english}` |
| `tcblisting` | `\begin{english}...\end{english}` |

### 6.3 QA-Approved Table Structure

```latex
\begin{hebrewtable}                    % NOT table
\begin{rtltabular}{col specs}          % NOT tabular
\hline
\rowcolor{blue!15}                     % Header color
\textbf{\hebheader{...}} & ...         % Headers
\hline
\hebcell{...} & \encell{...}           % Cell content
\hline
\end{rtltabular}
\caption[short]{long caption}          % Caption AFTER, with short title
\label{tab:...}
\end{hebrewtable}
```

---

## 7. Success Metrics

After implementing this upgrade plan:

| Metric | Current | Target |
|--------|---------|--------|
| BiDi violations per chapter | 15-30 | 0 |
| Code block violations | 5-10 | 0 |
| Table violations | 3-5 | 0 |
| Caption violations | 5-10 | 0 |
| Bibliography violations | 2-3 | 0 |
| **Total QA errors** | **30-60** | **0** |

---

## Appendix A: QA Rule ID Reference

### BiDi Rules (15)
`bidi-cover-metadata`, `bidi-section-number`, `bidi-reversed-text`, `bidi-header-footer`, `bidi-numbers`, `bidi-year-range`, `bidi-english`, `bidi-tcolorbox`, `bidi-section-english`, `bidi-acronym`, `bidi-chapter-label`, `bidi-fbox-mixed`, `bidi-standalone-counter`, `bidi-hebrew-in-english`, `bidi-missing-hebrewchapter`, `bidi-tikz-rtl`

### Code Rules (5)
`code-background-overflow`, `code-encoding-emoji`, `code-direction-hebrew`, `code-hebrew-content`, `code-fstring-brace`

### Table Rules (10)
`table-no-rtl-env`, `table-caption-position`, `table-cell-hebrew`, `table-plain-unstyled`, `table-missing-header-color`, `table-not-hebrewtable`, `table-overflow`, `caption-setup-raggedleft`, `caption-flushleft-wrapped`, `caption-table-raggedleft`

### Bibliography Rules (5)
`bib-malformed-cite-key`, `bib-missing-file`, `bib-undefined-cite`, `bib-empty-cite`, `bib-standalone-missing`

### Hebrew Math Rules (5)
`heb-math-text`, `heb-math-textbf`, `heb-math-subscript`, `heb-math-superscript`, `heb-math-cases`

### Image/Caption Rules (9)
`img-file-not-found`, `img-no-graphicspath`, `img-wrong-extension`, `img-case-mismatch`, `img-placeholder-box`, `img-empty-figure`, `img-hebrew-figure-empty`, `img-no-size-spec`, `caption-too-long`

---

*Document Version: 1.0.0*
*Date: 2025-12-21*
*Author: Claude Code Planning Agent*
