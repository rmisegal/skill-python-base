% hebrew-academic-template.cls
% Version 6.3.4 - TOC Page Numbers LTR Fix
% Date: 2025-12-21
%
% A comprehensive LaTeX class for Hebrew academic documents with English integration
% Copyright (c) 2025 Dr. Segal Yoram. All rights reserved.
%
% CHANGELOG:
% v6.3.4 (2025-12-21) - TOC Page Numbers LTR Fix
%   - FIXED: TOC page numbers rendered RTL (e.g., "021" instead of "120")
%   - Root cause: l@chapter/section/subsection used \textenglish{#2} for page numbers
%   - Solution: Changed to {\textdir TLT #2} which properly forces LTR
%
% v6.3.3 (2025-12-21) - Footer Page Numbering Complete Fix
%   - FIXED: Front matter pages now show Roman numerals (i, ii, iii...) not Arabic
%   - Problem: \renewcommand{\thepage}{\arabic{page}} forced Arabic always
%   - Solution: Removed \thepage override - use \thepage directly with LTR wrapper
%   - FIXED: Chapter opening pages (plain style) now show LTR page numbers
%   - Problem: \fancypagestyle{plain} was not defined - used default with RTL
%   - Solution: Added \fancypagestyle{plain} with {\textdir TLT\thepage}
%   - Changed \fancyfoot to use \thepage (not \arabic{page}) preserving format
%   - UPDATED: qa-cls-footer-detect v2.0 now detects both issues
%
% v6.3.2 (2025-12-21) - Footer Page Number LTR Fix
%   - FIXED: Footer page numbers now render LTR (not reversed like "61" for "16")
%   - Problem: \textenglish{\thepage} doesn't force LTR in fancyhdr context
%   - Solution: Use {\textdir TLT\arabic{page}} for footer page numbers
%   - Changed \fancyfoot[LE] and \fancyfoot[RO] to use \textdir TLT
%   - NEW: qa-cls-footer-detect skill to catch this issue
%
% v6.3.1 (2025-12-21) - English References Page Number LTR Fix
%   - FIXED: Page numbers for English References now render LTR (not reversed)
%   - Problem: Page "237" was rendering as "732" in RTL context
%   - Root cause: l@subsection uses \textenglish{#2} which didn't force LTR for numbers
%   - Solution: Use l@englishsubsection handler which uses {\textdir TLT #2}
%   - Changed \englishsectionunnumbered to use {englishsubsection} TOC type
%
% v6.3.0 (2025-12-21) - Bibliography TOC Single Entry (English Only)
%   - FIXED: Only "English References" appears in TOC, not Hebrew "מקורות בעברית"
%   - Problem: Both \printhebrewbibliography and \printenglishbibliography added TOC entries
%   - Symptom: TOC showed both "X.Y מקורות בעברית" and "English References"
%   - Solution: \printhebrewbibliography now uses \hebrewsectionnotoc (no TOC entry)
%   - NEW: \hebrewsectionnotoc command - numbered section without TOC entry
%   - Detected by: Visual comparison of TOC showing duplicate bibliography entries
%
% v6.2.3 (2025-12-21) - TOC English Entry Using Standard Handler
%   - FIXED: English References now uses standard l@subsection handler
%   - Problem in v6.2.2: Custom l@englishsubsection had different layout than Hebrew
%   - Solution: Use standard {subsection} handler with \hbox{\textdir TLT ...} wrapper
%   - This ensures identical layout to Hebrew entries, just with LTR text
%   - Detected by: Visual comparison with Hebrew מקורות entries
%
% v6.2.2 (2025-12-21) - TOC English Entry Correct RTL Alignment (LAYOUT MISMATCH)
%   - ATTEMPTED: Custom l@englishsubsection with {\textdir TLT} wrappers
%   - ISSUE: Layout was different from Hebrew entries (inverted structure)
%   - Superseded by: v6.2.3
%
% v6.2.1 (2025-12-21) - TOC English Entry RTL Alignment Fix (WRONG)
%   - ATTEMPTED: Used \pardir TRT + \textdir TLT
%   - ISSUE: \textdir TLT affected entire line, not just title
%   - Symptom: Entry pushed to left page edge
%   - Superseded by: v6.2.2
%
% v6.2.0 (2025-12-21) - TOC English Entry Paragraph-Level LTR Fix (WRONG ALIGNMENT)
%   - ATTEMPTED: Used \pardir TLT for LTR paragraph direction
%   - ISSUE: Made English entries LEFT-aligned in RTL document
%   - Superseded by: v6.2.1 with proper RTL alignment
%
% v6.1.0 (2025-12-21) - TOC English Entry Line-Level LTR Fix (INCOMPLETE)
%   - ATTEMPTED: Used \protect\LRE{} for line-level LTR embedding in TOC entries
%   - ISSUE: \LRE{} is inline, but l@subsection still forces \pardir TRT
%   - Symptom: Text was LTR but entire line structure remained RTL
%   - Superseded by: v6.2.0 which uses proper paragraph-level LTR handler
%
% v6.0.0 (2025-12-21) - MAJOR: Counter Architecture Refactor
%   - BREAKING: \printenglishbibliography now creates UNNUMBERED section
%   - Root cause: \englishsection incremented hebrewsection counter causing gaps
%   - Symptom: TOC showed English References as 4.10, 5.7 etc. with numbering gaps
%   - Solution: Bibliography sections should be unnumbered (like Hebrew מקורות)
%   - FIXED: \englishsection now syncs section counter (like \hebrewsection)
%   - Root cause: \hebrewsection synced section counter but \englishsection didn't
%   - Symptom: Counter mismatch when mixing hebrew/english section commands
%   - Solution: Added \setcounter{section}{\value{hebrewsection}} to \englishsection
%   - NEW: \englishsectionunnumbered command for unnumbered English sections
%   - Purpose: For bibliography and other sections that shouldn't be numbered
%   - Usage: Used internally by \printenglishbibliography
%   - Detected by: QA TOC comprehensive detection - parallel terminal analysis
%
% v5.14.0 (2025-12-21) - TOC Numbering & Hebrew Section Fix (QA-detected)
%   - FIXED: \thesubsubsection now includes chapter number
%   - Root cause: Counter format was \arabic{section}.\arabic{subsection}.\arabic{subsubsection}
%   - Symptom: TOC showed "2.2.1" instead of "1.2.2.1" (missing chapter prefix)
%   - Solution: Changed to \arabic{chapter}.\arabic{section}.\arabic{subsection}.\arabic{subsubsection}
%   - FIXED: \hebrewsection, \englishsection, \hebrewsubsection TOC entries
%   - Root cause: Used \HebrewSubtitle which caused double \textenglish{} wrapping
%   - Symptom: TOC showed \textenglish{\textenglish{2.1}} and no \numberline{}
%   - Solution: Changed to \protect\numberline{\thehebrewsection}\texthebrew{#1}
%   - Fixes 100 TOC issues: 88 subsubsection + 12 hebrewsection entries
%   - Detected by: QA TOC comprehensive detection - T1 parallel terminal
%
% v5.13.2 (2025-12-21) - TOC Title Wrapping Fix (QA-detected)
%   - FIXED: Added \chapter override to wrap titles in \texthebrew{} for TOC
%   - Root cause: Standard \chapter{} didn't wrap title in \texthebrew{} for TOC
%   - Symptom: Chapter titles with mixed Hebrew/English rendered incorrectly in TOC
%   - Solution: Patched \@chapter to wrap TOC entries with \texthebrew{}
%   - FIXED: Added \subsubsection override for consistent TOC wrapping
%   - Root cause: Standard \subsubsection{} didn't wrap title in \texthebrew{} for TOC
%   - Symptom: Subsubsection titles rendered inconsistently in TOC
%   - Solution: Override \subsubsection to use \texthebrew{} in \addcontentsline
%   - Detected by: QA TOC verification - qa-BiDi-fix-text skills
%
% v5.13.1 (2025-12-21) - TOC BiDi Double-Wrap Fix (QA-detected)
%   - FIXED: Added \thechapter definition with \textenglish{} wrapper
%   - Root cause: In book mode, section numbers use \thechapter.\thesection format
%   - Symptom: Chapter part of section number (e.g., "11" in "11.2") rendered RTL
%   - FIXED: Removed double-wrap from \numberline macro
%   - Root cause: \numberline added \textenglish{} but counters already have it
%   - Symptom: TOC section numbers appeared in wrong sequence due to nested \textenglish{}
%   - FIXED: Added \section redefinition for Hebrew TOC (like \subsection)
%   - Root cause: Standard \section{} didn't wrap title in \texthebrew{} for TOC
%   - Symptom: Section titles with English text rendered incorrectly in TOC
%   - Detected by: qa-BiDi-fix-toc-config, qa-BiDi-fix-text skills
%
% v5.13.0 (2025-12-20) - Section Numbering BiDi Fix + Counter Sync Fix
%   - FIXED: \thesection, \thesubsection, \thesubsubsection now wrapped in \textenglish{}
%   - Root cause: Section numbers (1.2.3) could render reversed (3.2.1) in RTL context
%   - Symptom: Standard LaTeX \section, \subsection, \subsubsection numbering reversed
%   - Solution: Wrap all section counter formats in \textenglish{} for LTR rendering
%   - Also fixed: \thehebrewsection, \thehebrewsubsection with \textenglish{} wrapper
%   - FIXED: Counter synchronization between hebrew and standard counters
%   - Root cause: \hebrewsection{} didn't sync 'section' counter, \hebrewsubsection{} didn't sync 'subsection'
%   - Symptom: Using \hebrewsection{} then \subsubsection{} showed wrong numbers (2.0.2 instead of 2.1.1)
%   - Solution: \hebrewsection now sets section counter; \hebrewsubsection now sets subsection counter
%   - Detected by: QA mechanism manual review - section numbering direction check
%
% v5.12.0 (2025-12-20) - TOC Unnumbered Entry RTL Fix (Bibliography, Section*)
%   - FIXED: Unnumbered TOC entries (bibliography, \section*) now align to RIGHT (RTL)
%   - Root cause: l@chapter and l@section were MISSING \pardir TRT\textdir TRT
%   - Symptom: Bibliography entry "מקורות" appeared LEFT-aligned in TOC
%   - Solution: Added \pardir TRT\textdir TRT to l@chapter and l@section
%   - Note: Numbered entries worked because \hebrewchapter{} adds RTL wrappers,
%           but unnumbered entries (bibintoc, addcontentsline) go directly to l@
%   - Detected by: QA mechanism - qa-BiDi-detect Rule 18 (v2.12.0)
%
% v5.11.9 (2025-12-20) - TOC RTL Alignment Fix
%   - FIXED: TOC subsection/subsubsection entries now align to RIGHT (RTL)
%   - Root cause: l@ macros created LTR paragraphs even with \texthebrew{} content
%   - Solution: Added \pardir TRT\textdir TRT to l@subsection and l@subsubsection
%   - This sets paragraph direction to RTL so entries align to right margin
%
% v5.11.8 (2025-12-20) - TOC Hebrew Text Fix
%   - FIXED: Standard \subsection{Hebrew text} now wraps TOC entry with \texthebrew{}
%   - Root cause: \subsection adds raw Hebrew to TOC without RTL wrapper
%   - Solution: Override \subsection to use \texthebrew{} in \addcontentsline
%   - FIXED: contentsline now handles 4 arguments (hyperref format)
%
% v5.11.7 (2025-12-20) - TOC RTL Direction Fix (reverted - caused margin overflow)
%   - Attempted \textdir TRT\pardir TRT in l@ macros - caused entries to overflow right margin
%
% v5.11.6 (2025-12-19) - TOC l@subsubsection BiDi Fix
%   - Added missing l@subsubsection definition for proper TOC formatting
%
% v5.11.5 (2025-12-19) - TOC Dot Leaders Fix
%   - FIXED: TOC showing "m@th" text instead of dot leaders
%   - Root cause: Double backslash \\m@th instead of single \m@th in l@chapter/l@section/l@subsection
%   - Fixed lines 674, 694, 712 - changed $\\m@th to $\m@th
%   - Dot leaders now render correctly as "......" between entry and page number
%
% v5.11.4 (2025-12-19) - Code Block Space Artifacts Fix
%   - FIXED: Visible space markers (u-like chars) appearing in code strings
%   - ADDED: Global \lstset with showstringspaces=false, columns=flexible
%   - UPDATED: pythonbox/pythonbox* to use literate={ }{\ }1 for robust space rendering
% 
% v5.11.3 (2025-12-19) - Table Row Color Support
%   - NEW: Added \PassOptionsToPackage{table}{xcolor} for \rowcolor support
%   - FIXED: \rowcolor{blue!15} now works in rtltabular table headers
%   - NOTE: xcolor table option must be passed before tikz-cd loads xcolor
% 
% v5.11.2 (2025-12-14) - TOC BiDi Fixes
%   - FIXED: TOC page numbers now render LTR (not reversed)
%   - FIXED: TOC chapter/section numbers now render LTR
%   - FIXED: TOC dot leaders work correctly in RTL context
%   - FIXED: Redefined l@chapter, l@section, l@subsection for BiDi
%   - FIXED: Redefined \numberline to wrap numbers in \textenglish{}
%   - FIXED: Redefined \contentsline to ensure LTR page numbers
%   - FIXED: Removed deprecated polyglossia calendar/numerals keys (102 warnings eliminated)
% 
% v5.11.1 (2025-12-14) - Compatibility Environments
%   - NEW: 'latin' environment - alias for 'english' (backward compatibility)
%   - NEW: 'exercise' environment - alias for 'exercisebox' (backward compatibility)
%   - NEW: 'definition' environment - styled box for definitions (blue theme)
%   - NEW: 'abstract' environment for book mode (centered title, quotation style)
% 
% v5.11.0 (2025-12-14) - Book Class Support
%   - NEW: Added 'book' class option for full book support
%   - NEW: \LoadClass now conditionally loads book or article based on option
%   - NEW: \frontmatter, \mainmatter, \backmatter commands for book structure
%   - NEW: Hebrew-formatted \tableofcontents with RTL title "תוכן עניינים"
%   - NEW: Hebrew-formatted \listoffigures with RTL title "רשימת איורים"
%   - NEW: Hebrew-formatted \listoftables with RTL title "רשימת טבלאות"
%   - NEW: \appendix command with Hebrew support
%   - NEW: \hebrewappendix{} for Hebrew appendix chapters
%   - NEW: Book-compatible \hebrewchapter{} using native \chapter* internally
%   - NEW: BiDi-safe tcolorbox wrapper environments for RTL documents
%   - FIXED: Native book class features (chapter, TOC, LOF, LOT) now work with Hebrew RTL
%   - Usage: \documentclass[book]{hebrew-academic-template} for book mode
%   - Default: article mode (backward compatible)
% 
% v5.10.0 (2025-12-12) - Chapter Reference Support
%   - CRITICAL FIX: Use \refstepcounter{hebrewchapter} for \ref{} support
%   - CRITICAL FIX: Define \thehebrewchapter with \textenglish{} for LTR numbers
%   - Problem: \label after \hebrewchapter captured empty value (no ref support)
%   - Problem: Chapter numbers in \ref{} appeared reversed in RTL context (10→01)
%   - Solution: refstepcounter makes counter value referable by \label/\ref
%   - Solution: \textenglish wrapper ensures LTR rendering of chapter numbers
%   - Usage: \hebrewchapter{...}\label{chap:myref} then פרק~\ref{chap:myref}
%   - Detected by: User testing cross-chapter references
% 
% v5.9.0 (2025-12-11) - Section Spacing Strict Enforcement
%   - CRITICAL FIX: Use \titlespacing* to ZERO OUT default section spacing
%   - CRITICAL FIX: Manual \vspace now provides EXACT spacing (not additive)
%   - NEW: \titlespacing*{\subsection}{0pt}{0pt}{0pt} - removes all defaults
%   - NEW: \titlespacing*{\subsubsection}{0pt}{0pt}{0pt} - removes all defaults
%   - RULE: Section before-space = 1.5em EXACT (18pt at 12pt font)
%   - RULE: Subsection before-space = 1em EXACT (12pt at 12pt font)
%   - RULE: After-space = 0.5em for all section levels
%   - RULE: Maximum gap = 2x font height (24pt at 12pt font)
% 
% v5.8.0 (2025-12-11) - Section Spacing Fix Edition
%   - CRITICAL FIX: Removed additive \vspace from section commands
%   - CRITICAL FIX: Use titlesec for TOTAL spacing control (not additive)
%   - NEW: \titlespacing* replaces manual vspace - controls exact spacing
%   - NEW: Orphan section rule - sections with <5 lines start new page
%   - FIXED: HebrewTitle/HebrewSubtitle now wrap Hebrew in \texthebrew{}
%   - RULE: Section before-space = 1.5em total (not additive)
%   - RULE: Subsection before-space = 1em total (not additive)
%   - RULE: After-space = 0.5em for all section levels
%   - RULE: needspace enforces 5-line minimum before page break
% 
% v5.7.0 (2025-12-11) - Spacing Standards Edition
%   - NEW: Added enumitem package for precise list spacing control
%   - NEW: Configured itemize/enumerate with compact spacing:
%     * itemsep=0.5ex (half font height between items)
%     * parsep=0pt (no extra paragraph spacing)
%     * topsep=0.5ex (half font height above/below list)
%   - NEW: Added titlesec spacing configuration:
%     * Section: 2em before, 0.5em after (≤24pt for 12pt font)
%     * Subsection: 1.5em before, 0.5em after
%   - NEW: Added needspace check for sections (5 lines minimum before page break)
%   - RULE: Line spacing between items = 0.5x font height
%   - RULE: Space before section title = 2x font height (max)
%   - RULE: All other spacing ≤ 1x font height
% 
% v5.6.2 (2025-12-10) - CRITICAL: Fixed pythonbox environment corruption (QA-detected)
%   - FIXED: pythonbox/pythonbox* causing environment stack corruption with begingroup/endgroup
%   - Problem: Using before={begingroup...} after={endgroup} conflicted with tcolorbox internals
%   - Root cause: begingroup/endgroup inside tcblisting causes environment mismatch errors
%   - Solution: Changed from before/after to before upper (no grouping needed)
%   - Matched working implementation from Homework07-Even-Odd-League project
%   - Detected by: qa-typeset QA orchestrator (40 pythonbox errors in compilation log)
% 
% v5.6.1 (2025-12-05) - CRITICAL: Fixed pythonbox environment stack corruption
%   - FIXED: Hebrew titles in pythonbox causing environment stack corruption
%   - Problem: \begin{python} float wrapper inside pythonbox conflicted with BiDi
%   - Root cause: Nested python float + tcblisting + BiDi caused environment mismatch
%   - Solution: Removed python float wrapper from pythonbox, using same approach as pythonbox*
%   - Added detach title + before upper for better title handling
%   - \hebtitle{} now uses LTR wrapper with RTL hbox for Hebrew content
% 
% v5.6 (2025-12-05) - CRITICAL: Pythonbox Hebrew title fix
%   - FIXED: Hebrew text in pythonbox/tcolorbox titles causing environment stack corruption
%   - Problem: Hebrew titles in pythonbox caused compilation errors and corrupted environment
%   - Root cause: tcolorbox title rendered in LTR context breaks Hebrew character handling
%   - Solution: New \hebtitle{} command for RTL pythonbox/tcolorbox titles
%   - Added \hebtitle{} command similar to \hebfoot{} but for tcolorbox title context
%   - Usage: \begin{pythonbox}[\hebtitle{כותרת בעברית}]
%   - Usage: \begin{pythonbox}[\hebtitle{פתרון \en{SVM} עם \en{cvxopt}}]
%   - Detected by: qa-code-detect agent (pythonbox Hebrew title detection)
% 
% v5.5 (2025-11-28) - CRITICAL: Footer/Header BiDi fix for mixed Hebrew/English content
%   - FIXED: Hebrew text in fancyhdr footers appearing reversed (LTR instead of RTL)
%   - Problem: \texthebrew{} in fancyfoot/fancyhead doesn't properly set RTL direction
%   - Root cause: fancyhdr operates in LTR context even in RTL documents
%   - Solution: New \hebfoot{} command for RTL footer/header text with \en{} for English
%   - Added \hebfoot{} command similar to \hebcell{} but for footer/header context
%   - Usage: \fancyfoot[LO]{\hebfoot{כל הזכויות שמורות - \en{© Dr. Name}}}
%   - Updated footer definitions to use \hebfoot{} + \en{} pattern
%   - Updated title page copyright to use \hebfoot{} + \en{} pattern
%   - Detected by: Enhanced qa-BiDi-detect agent (Rule 5)
% 
% v5.4 (2025-11-10) - CRITICAL: Code block background overflow fix + section numbering fix
%   - FIXED: Background overflows to the right outside document in RTL context
%   - Solution: Use python float environment wrapper + explicit text direction
%   - Changed before/after to use: \begin{python}\begingroup\selectlanguage{english}\textdir TLT\pardir TLT
%   - Root cause: tcolorbox in RTL context needs explicit LTR text direction
%   - Symptom: Code blocks appeared with background extending beyond right margin
%   - Lines changed: 726-727 (pythonbox) and 765-766 (pythonbox*)
%   - Solution source: Working implementation from C:\25D\EX\L12\Latex project
%   - Detected by: Enhanced Code Block QA Agent + user testing
%   - FIXED: Section numbering starting from 0 instead of 1
%   - Redefined \thehebrewsection to conditionally show section number without chapter prefix
%   - Root cause: \thehebrewsection showed "0.X" when no chapters used (hebrewchapter=0)
%   - Solution: Use \ifnum to check hebrewchapter value and format accordingly
%   - Lines changed: 356-362 (conditional \thehebrewsection definition)
%   - Symptom: Sections numbered 0.1, 0.2, 0.3 instead of 1, 2, 3
%   - Detected by: Enhanced RTL/LTR QA Agent
% 
% v5.3 (2025-11-10) - Code block character encoding and translation fixes
%   - FIXED: Added literate replacements for hyphen character variants in code blocks
%   - Added literate rules to normalize: - (hyphen), − (minus), – (en-dash), — (em-dash)
%   - Added upquote=true to ensure straight quotes in code
%   - Prevents non-ASCII hyphen/minus characters from appearing in code listings
%   - Updated beginner_example.tex with Hebrew code comments and docstrings
%   - All code comments now in Hebrew for proper localization
%   - Detected by: New Code Block QA Agent (code-block-qa-agent-skill.md)
% 
% v5.2 (2025-11-10) - Critical table layout fixes
%   - FIXED: Table caption alignment changed from left-aligned to centered
%   - Changed hebrewtable caption from raggedleft to centering
%   - Captions now properly centered for Hebrew academic tables
%   - Updated documentation to clarify RTL column ordering requirements
%   - All tables now follow Hebrew typography standards
%   - Detected by: New Table Layout QA Agent (table-layout-qa-agent-skill.md)
% 
% v5.1 (2025-11-10) - Critical RTL/LTR bugfix
%   - FIXED: \entoc{} command now properly forces LTR for English text in titles
%   - Previously English text in section titles appeared reversed (RTL)
%   - Changed \entoc definition from {#1} to {\textenglish{#1}}
%   - Affects all section/subsection titles with mixed Hebrew-English content
%   - All 7 examples now render English text correctly in titles and TOC
% 
% v5.0 (2025-11-09) - Unified merge of all versions
%   - Based on v3.0 with all v1.0 features restored
%   - Fixed 4 regressions from v3.0
%   - Added 18 enhancements from v3.0
%   - 100% backward compatible with v1.0 and v3.0
%   - Total: 78 commands, 8 environments, 24+ packages
% 
% v3.0 (2025-10-28) - Major upgrade with chapter support
%   - Added \hebrewchapter{} for book-length documents
%   - Enhanced table cell commands (\encell, \hebheader, \enheader)
%   - Added \enpath{} for paths/filenames with hyphens
%   - Added \clsversion{} command
% 
% v1.0 (2025-09-26) - Foundation release
%   - Full Hebrew RTL support with English LTR integration
%   - Custom title numbering
%   - Academic formatting with bibliography support
%   - Table support with mixed content
% 
% Features:
% - Full Hebrew RTL support with English LTR integration
% - Chapter and section hierarchy with automatic numbering
% - Advanced table commands for RTL/LTR mixed content
% - Mathematical expressions with Hebrew support
% - Bibliography with biber backend for superior Unicode support
% - Code environments with floating and non-floating options
% - Cross-platform font fallback system
% - PDF bookmark support with proper hyperref integration

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hebrew-academic-template}[2025/12/21 v5.14.0 Hebrew Academic Template - TOC Numbering & Hebrew Section Fix]

% ==================== VERSION INFORMATION ====================
% Version command - defined early for programmatic access
\newcommand{\clsversion}{V5.14.0-2025-12-21}

% ==================== CLASS OPTIONS ====================
% 'book' option - enables full book class with chapters, frontmatter, etc.
% Default is article class for backward compatibility
\makeatletter
\newif\if@bookmode
\@bookmodefalse
\DeclareOption{book}{\@bookmodetrue}
\DeclareOption*{
  \if@bookmode
    \PassOptionsToClass{\CurrentOption}{book}%
  \else
    \PassOptionsToClass{\CurrentOption}{article}%
  \fi
}
\ProcessOptions\relax
\makeatother

% Base class - conditionally load book or article
\makeatletter
\if@bookmode
  \LoadClass[12pt,a4paper,openright,twoside]{book}
\else
  \LoadClass[12pt,a4paper,twoside]{article}
\fi
\makeatother

%% ==================== REQUIRED PACKAGES ====================

% v5.11.3: Pass table option to xcolor before any package loads it
% Required for \rowcolor command in rtltabular tables
\PassOptionsToPackage{table}{xcolor}

% Font and language support
\RequirePackage{fontspec}
\RequirePackage{polyglossia}
\RequirePackage{luabidi}
\RequirePackage{amsmath,amssymb}
\RequirePackage{graphicx}
\RequirePackage{float}
\RequirePackage{setspace}
\RequirePackage{caption}
\RequirePackage{enumerate}
\RequirePackage{enumitem}  % v5.7.0: For precise list spacing control
\RequirePackage{titlesec}
\RequirePackage{needspace}  % v5.7.0: For section page break control

% Bibliography support - FIXED: Using biber backend (not bibtex) for Unicode support
\RequirePackage[backend=biber, style=ieee]{biblatex}
\DeclareLanguageMapping{hebrew}{english}

% Declare bibliography categories
\DeclareBibliographyCategory{hebrew}
\DeclareBibliographyCategory{english}

% Auto-categorize entries based on keywords field at print time
% Note: Uses AtEveryBibitem which runs during bibliography output
\AtEveryBibitem{%
  \ifkeyword{hebrew}{\addtocategory{hebrew}{\thefield{entrykey}}}{}%
  \ifkeyword{english}{\addtocategory{english}{\thefield{entrykey}}}{}%
}

% Table packages
\RequirePackage{longtable}
\RequirePackage{tabularx}
\RequirePackage{array}
\RequirePackage{booktabs}

% TikZ packages for diagrams
\RequirePackage{tikz-cd}

% Hyperref for PDF bookmarks and links
\RequirePackage[unicode, pdfencoding=auto, bookmarks=true, colorlinks=true, linkcolor=blue, citecolor=red, urlcolor=blue]{hyperref}

% Header and footer support
\RequirePackage{fancyhdr}

%% ==================== SPACING STANDARDS (v5.9.0) ====================
% RULE 1: Line spacing between list items = 0.5x font height (0.5ex)
% RULE 2: Space before section title = 1.5x font height (1.5em, ~18pt for 12pt font)
% RULE 3: Space before subsection title = 1em (12pt for 12pt font)
% RULE 4: Space after section/subsection title = 0.5em
% RULE 5: Maximum gap between any elements = 2x font height (24pt at 12pt font)
% RULE 6: Section with <5 lines remaining on page = start new page (orphan prevention)
% RULE 7: Subsection with <4 lines remaining on page = start new page
% 
% CRITICAL: Use \titlespacing* to ZERO OUT LaTeX's default section spacing
% Then our \vspace commands provide the EXACT spacing we want
\titlespacing*{\section}{0pt}{0pt}{0pt}
\titlespacing*{\subsection}{0pt}{0pt}{0pt}
\titlespacing*{\subsubsection}{0pt}{0pt}{0pt}

% List spacing configuration - compact spacing for itemize and enumerate
\setlist{
  itemsep=0.5ex,      % Half font height between items
  parsep=0pt,         % No extra paragraph spacing within items
  topsep=0.5ex,       % Half font height above/below list
  partopsep=0pt,      % No extra space when list starts new paragraph
  leftmargin=2em,     % Indentation from left margin
  labelsep=0.5em      % Space between bullet/number and text
}

% Specific settings for itemize (bullets)
\setlist[itemize]{
  itemsep=0.5ex,
  parsep=0pt,
  topsep=0.5ex
}

% Specific settings for enumerate (numbers)
\setlist[enumerate]{
  itemsep=0.5ex,
  parsep=0pt,
  topsep=0.5ex
}

% Paragraph spacing - keep minimal
\setlength{\parskip}{0.5ex plus 0.1ex minus 0.1ex}

%% ==================== CORE FUNCTIONS AND COMMANDS ====================

% Advanced title function for mixed Hebrew/English content
% Usage: \HebrewTitle{number}{mixed Hebrew/English title}
% FIXED v5.8.0: Wrap Hebrew argument in \texthebrew{} for proper TOC rendering
\newcommand{\HebrewTitle}[2]{%
  \textenglish{#1}\quad\texthebrew{#2}%
}

% Subtitle function for subsections
% Usage: \HebrewSubtitle{number}{mixed Hebrew/English subtitle}
% FIXED v5.8.0: Wrap Hebrew argument in \texthebrew{} for proper TOC rendering
\newcommand{\HebrewSubtitle}[2]{%
  \textenglish{#1}\quad\texthebrew{#2}%
}

% PDF string handling for hyperref compatibility
\pdfstringdefDisableCommands{
  \def\textenglish#1{#1}%
  \def\texthebrew#1{#1}%
  \def\en#1{#1}%
  \def\heb#1{#1}%
  \def\ilm#1{#1}%
  \def\textbf#1{#1}%
  \def\LTR#1{#1}%
  \def\hebfoot#1{#1}%
  \def\hebtitle#1{#1}%
  \def\HebrewTitle#1#2{#1 #2}%
  \def\HebrewSubtitle#1#2{#1 #2}%
  \def\quad{ }% 
  \def\\{ }% 
  \def\xpg@aux#1#2{}%
  \def\texorpdfstring#1#2{#2}%
}

%% ==================== LANGUAGE SETUP ====================

% Main language configuration
% FIXED v5.11.2: Removed deprecated calendar/numerals keys (caused 102 warnings)
% Modern polyglossia handles these automatically
\setmainlanguage{hebrew}
\setotherlanguage{english}

% Hebrew line breaking and text handling for LuaLaTeX
\emergencystretch=3em
\tolerance=1000
\hbadness=10000

%% ==================== NUMBERING CONFIGURATION ====================

% Chapter numbering - always LTR (v5.13.1: added for book mode TOC BiDi)
\renewcommand{\thechapter}{\textenglish{\arabic{chapter}}}

% Section numbering - always LTR (v5.13.0: wrapped in \textenglish{} for BiDi)
\renewcommand{\thesection}{\textenglish{\arabic{section}}}
\renewcommand{\thesubsection}{\textenglish{\arabic{section}.\arabic{subsection}}}
\renewcommand{\thesubsubsection}{\textenglish{\arabic{chapter}.\arabic{section}.\arabic{subsection}.\arabic{subsubsection}}}

% Page numbering - DO NOT override \thepage format
% v6.3.3: Removed \renewcommand{\thepage} to preserve Roman numerals in frontmatter
% The LTR wrapping is now done in the footer definition, not in \thepage

% Table and figure numbering - always LTR
\renewcommand{\thetable}{\textenglish{\arabic{table}}}
\renewcommand{\thefigure}{\textenglish{\arabic{figure}}}

%% ==================== FONT CONFIGURATION ====================

% Smart font fallback mechanism - works on both Windows/MiKTeX and Linux/TeX Live
% First try preferred fonts (Windows/MiKTeX), then fallback to available alternatives

% Main font: Times New Roman (Windows) -> Latin Modern Roman (Linux)
\IfFontExistsTF{Times New Roman}{
    \setmainfont{Times New Roman}[
        Renderer=Harfbuzz,
        Ligatures=TeX
    ]
    \newfontfamily\englishfont{Times New Roman}[
        Renderer=Harfbuzz,
        Script=Latin,
        Ligatures=TeX
    ]
}{
    \setmainfont{Latin Modern Roman}[
        Renderer=Harfbuzz,
        Ligatures=TeX
    ]
    \newfontfamily\englishfont{Latin Modern Roman}[
        Renderer=Harfbuzz,
        Script=Latin,
        Ligatures=TeX
    ]
}

% Hebrew font: David CLM (Windows) -> DejaVu Sans (Linux)
\IfFontExistsTF{David CLM}{
    \newfontfamily\hebrewfont{David CLM}[
        Renderer=Harfbuzz,
        Script=Hebrew,
        Ligatures=TeX,
        Scale=MatchLowercase
    ]
}{
    \IfFontExistsTF{DejaVu Sans}{
        \newfontfamily\hebrewfont{DejaVu Sans}[
            Renderer=Harfbuzz,
            Script=Hebrew,
            Ligatures=TeX,
            Scale=MatchLowercase
        ]
    }{
        % Ultimate fallback to Latin Modern Roman with Hebrew support
        \newfontfamily\hebrewfont{Latin Modern Roman}[
            Renderer=Harfbuzz,
            Script=Hebrew,
            Ligatures=TeX,
            Scale=MatchLowercase
        ]
    }
}

% Sans-serif font: Arial (Windows) -> DejaVu Sans (Linux)
\IfFontExistsTF{Arial}{
    \setsansfont{Arial}[Renderer=Harfbuzz]
}{
    \IfFontExistsTF{DejaVu Sans}{
        \setsansfont{DejaVu Sans}[Renderer=Harfbuzz]
    }{
        \setsansfont{Latin Modern Sans}[Renderer=Harfbuzz]
    }
}

% Monospace font: Courier New (Windows) -> DejaVu Sans Mono (Linux)
\IfFontExistsTF{Courier New}{
    \setmonofont{Courier New}[Renderer=Harfbuzz]
}{
    \IfFontExistsTF{DejaVu Sans Mono}{
        \setmonofont{DejaVu Sans Mono}[Renderer=Harfbuzz]
    }{
        \setmonofont{Latin Modern Mono}[Renderer=Harfbuzz]
    }
}

% Courier font with fallback for \enpath{} command
\IfFontExistsTF{Courier New}{
  \newfontfamily\courierfont{Courier New}[Renderer=Harfbuzz]
}{
  \IfFontExistsTF{DejaVu Sans Mono}{
    \newfontfamily\courierfont{DejaVu Sans Mono}[Renderer=Harfbuzz]
  }{
    \newfontfamily\courierfont{Latin Modern Mono}[Renderer=Harfbuzz]
  }
}

%% ==================== CONVENIENT COMMANDS ====================

% Short commands for language switching
\newcommand{\en}[1]{\textenglish{#1}}
\newcommand{\heb}[1]{\texthebrew{#1}}
\newcommand{\ilm}[1]{\textenglish{#1}}  % For inline math/English terms

% Command for inline numbers in Hebrew text (always LTR)
\newcommand{\num}[1]{\textenglish{#1}}

% Command for years in Hebrew text (always LTR)
\newcommand{\hebyear}[1]{\textenglish{#1}}

% Command for percentages in Hebrew text (always LTR with % symbol)
\newcommand{\percent}[1]{\textenglish{#1\%}}

% RESTORED from v1.0: \ltr{} command for LTR text protection
\newcommand{\ltr}[1]{{\textdir TLT\textenglish{#1}}}

% Command for English sections that maintain LTR left-alignment and then return to Hebrew RTL
\newcommand{\startenglish}{%
  \selectlanguage{english}%
  \textdir TLT\pardir TLT%
  \raggedright%
}

% Command to return to Hebrew RTL alignment after English sections
\newcommand{\stophebrew}{%
  \selectlanguage{hebrew}%
  \textdir TRT\pardir TRT%
  \raggedleft%
}

% Command to end English sections and return to Hebrew RTL alignment
\newcommand{\stopenglish}{%
  \selectlanguage{hebrew}%
  \textdir TRT\pardir TRT%
}

% Text direction commands (only define if not already defined)
\providecommand{\LTR}[1]{\textenglish{#1}}
\providecommand{\RTL}[1]{\texthebrew{#1}}

%% ==================== SYMBOL COMMANDS ====================
% RESTORED from v1.0

\newcommand{\warningsymbol}{\textenglish{\blacktriangle}}  % Warning symbol
\newcommand{\checksymbol}{\textenglish{\checkmark}}        % Checkmark symbol

%% ==================== BULLET POINTS FIX ====================

% Fix bullet points for Hebrew documents - use fallback characters for missing glyphs
\renewcommand{\labelitemi}{-}
\renewcommand{\labelitemii}{-}
\renewcommand{\labelitemiii}{-}
\renewcommand{\labelitemiv}{-}

%% ==================== SECTION COMMANDS ====================

\makeatletter
% Custom chapter command with automatic numbering
% In article class, we use section-level TOC entries for chapters
\newcounter{hebrewchapter}
% v5.10.0: Plain arabic for display in titles and \ref{}
% v5.13.0: Wrapped in \textenglish{} for BiDi - ensures LTR in all contexts
\renewcommand{\thehebrewchapter}{\textenglish{\arabic{hebrewchapter}}}
\newcommand{\hebrewchapter}[1]{%
  \clearpage%
  \refstepcounter{hebrewchapter}% v5.10.0: refstepcounter for \label/\ref
  \setcounter{hebrewsection}{0}% RESET section counter for new chapter
  \xdef\hcchapternum{\thehebrewchapter}% Save chapter number globally (no @ symbol)
  \section*{\HebrewTitle{\thehebrewchapter}{#1}}% 
  \phantomsection% CRITICAL - Added for PDF bookmarks
  \addcontentsline{toc}{section}{\HebrewTitle{\thehebrewchapter}{#1}}%
  \setcounter{section}{\value{hebrewchapter}}% Sync with section counter
}
% v5.10.0: Custom label for chapters - use after \hebrewchapter
\newcommand{\hebrewchapterlabel}[1]{%
  \edef\@currentlabel{\hcchapternum}%
  \label{#1}%
}
\makeatother

% English text in TOC - forces LTR direction for English text in mixed Hebrew/English titles
% FIXED in v5.1: Now properly wraps with \textenglish{} to prevent RTL reversal
\newcommand{\entoc}[1]{\textenglish{#1}}

% Custom section command that handles numbering properly
% Sections are subordinate to chapters, so use subsection-level TOC entries
\newcounter{hebrewsection}[hebrewchapter]
% FIXED v5.4: Show section number without chapter prefix when no chapters used
% v5.13.0: Wrapped in \textenglish{} for BiDi - ensures LTR in all contexts
\renewcommand{\thehebrewsection}{%
  \textenglish{%
    \ifnum\value{hebrewchapter}=0
      \arabic{hebrewsection}%
    \else
      \arabic{hebrewchapter}.\arabic{hebrewsection}%
    \fi
  }%
}
% v5.9.0: Section spacing with titlespacing* zeroed - vspace is EXACT
% Orphan rule: If less than 5 lines available, start new page
% Maximum spacing = 2x font height = 24pt at 12pt font = 2em
% Combined with box skipbelow (0.5em), total before section ≤ 2em
\newcommand{\hebrewsection}[1]{%
  \par\needspace{5\baselineskip}% v5.9.0: Orphan prevention - 5 lines minimum
  \vspace{1em}% v5.9.0: EXACT space before section = 1x font height (12pt)
  \stepcounter{hebrewsection}%
  \subsection*{\HebrewSubtitle{\thehebrewsection}{#1}}%
  \phantomsection% CRITICAL - Added for PDF bookmarks
  \addcontentsline{toc}{subsection}{\protect\numberline{\thehebrewsection}\texthebrew{#1}}%
  % v5.13.0: Sync BOTH section AND subsection counters for standard commands
  \setcounter{section}{\value{hebrewsection}}% Sync section counter
  \setcounter{subsection}{0}% Reset subsection for new section
  \vspace{0.3em}% v5.9.0: Space after section title
}

% v6.3.0: Hebrew section without TOC entry
% PURPOSE: Creates numbered section visible in document but NOT in TOC
% USAGE: For bibliography sections where only English References should appear in TOC
\newcommand{\hebrewsectionnotoc}[1]{%
  \par\needspace{5\baselineskip}%
  \vspace{1em}%
  \stepcounter{hebrewsection}%
  \subsection*{\HebrewSubtitle{\thehebrewsection}{#1}}%
  % NO \addcontentsline - intentionally omitted for v6.3.0
  \setcounter{section}{\value{hebrewsection}}%
  \setcounter{subsection}{0}%
  \vspace{0.3em}%
}

\newcommand{\englishsection}[1]{%
  \stepcounter{hebrewsection}%
  \begin{english}%
  \selectlanguage{english}%
  \textdir TLT\pardir TLT%
  \subsection*{\raggedright\textenglish{\thehebrewsection\quad #1}}%
  \phantomsection% CRITICAL - Added for PDF bookmarks
  \addcontentsline{toc}{subsection}{\protect\numberline{\thehebrewsection}\textenglish{#1}}%
  \end{english}%
  % v6.0.0: Sync section counter (like \hebrewsection does)
  \setcounter{section}{\value{hebrewsection}}%
  \setcounter{subsection}{0}% Reset subsection for new section
}

% v6.0.0: Unnumbered English section (for bibliography, appendix headers, etc.)
% Does NOT increment hebrewsection counter - creates unnumbered TOC entry
% v6.2.3: FIXED - use standard subsection handler with \hbox{\textdir TLT} wrapper
\newcommand{\englishsectionunnumbered}[1]{%
  \begin{english}%
  \selectlanguage{english}%
  \textdir TLT\pardir TLT%
  \subsection*{\raggedright\textenglish{#1}}%
  \phantomsection% CRITICAL - Added for PDF bookmarks
  % v6.3.1: Use englishsubsection handler for proper LTR page numbers
  % l@englishsubsection uses {\textdir TLT #2} for page numbers (not \textenglish{})
  % This fixes page numbers showing RTL (e.g., "732" instead of "237")
  \addcontentsline{toc}{englishsubsection}{\textenglish{#1}}%
  \end{english}%
}

% Custom subsection command
% Subsections are subordinate to sections, so use subsubsection-level TOC entries
% v5.9.0: Spacing with titlespacing* zeroed - vspace is EXACT
\newcounter{hebrewsubsection}[hebrewsection]
% v5.13.0: Explicit definition with \textenglish{} for BiDi
\renewcommand{\thehebrewsubsection}{\textenglish{\arabic{hebrewsubsection}}}
\newcommand{\hebrewsubsection}[1]{%
  \par\needspace{4\baselineskip}% v5.9.0: Orphan prevention - 4 lines minimum
  \vspace{0.8em}% v5.9.0: EXACT space before subsection (~10pt)
  \stepcounter{hebrewsubsection}%
  \subsubsection*{\HebrewSubtitle{\thehebrewsection.\thehebrewsubsection}{#1}}%
  \phantomsection% CRITICAL - Added for PDF bookmarks
  \addcontentsline{toc}{subsubsection}{\protect\numberline{\thehebrewsection.\thehebrewsubsection}\texthebrew{#1}}%
  % v5.13.0: Sync BOTH subsection AND subsubsection counters for standard commands
  \setcounter{subsection}{\value{hebrewsubsection}}% Sync subsection counter
  \setcounter{subsubsection}{0}% Reset subsubsection for new subsection
  \vspace{0.3em}% v5.9.0: Space after subsection title
}

% Custom subsubsection command (v5.11.0)
% For 4th level hierarchy: chapter.section.subsection.subsubsection
\newcounter{hebrewsubsubsection}[hebrewsubsection]
% v5.13.0: Explicit definition with \textenglish{} for BiDi
\renewcommand{\thehebrewsubsubsection}{\textenglish{\arabic{hebrewsubsubsection}}}
\newcommand{\hebrewsubsubsection}[1]{%
  \par\needspace{3\baselineskip}%
  \vspace{0.6em}%
  \stepcounter{hebrewsubsubsection}%
  \paragraph*{\textenglish{\thehebrewsection.\thehebrewsubsection.\arabic{hebrewsubsubsection}}\quad #1}% 
  \phantomsection%
  \addcontentsline{toc}{paragraph}{\textenglish{\thehebrewsection.\thehebrewsubsection.\arabic{hebrewsubsubsection}}\quad #1}%
  \vspace{0.2em}%
}

%% ==================== BOOK CLASS SUPPORT (v5.11.0) ====================
% These commands are only active when using [book] class option

\makeatletter
\if@bookmode
  % ---- Hebrew TOC, LOF, LOT Titles ----
  % Override default English titles with Hebrew
  \AtBeginDocument{
    \renewcommand{\contentsname}{תוכן עניינים}%
    \renewcommand{\listfigurename}{רשימת איורים}%
    \renewcommand{\listtablename}{רשימת טבלאות}%
    \renewcommand{\bibname}{רשימת מקורות}%
    \renewcommand{\indexname}{מפתח}%
    \renewcommand{\figurename}{איור}%
    \renewcommand{\tablename}{טבלה}%
    \renewcommand{\partname}{חלק}%
    \renewcommand{\chaptername}{פרק}%
    \renewcommand{\appendixname}{נספח}%
  }

  % ---- TOC BiDi Fixes (v5.11.2) ----
  % Fix page numbers in TOC to render LTR
  % Fix chapter/section numbers to render LTR
  % Fix dot leaders direction

  % Store original numberline - DO NOT add \textenglish wrapper here
  % because \thechapter, \thesection, etc. already include \textenglish{}
  % Double-wrapping causes BiDi rendering issues in TOC (v5.13.1 fix)
  \let\orig@numberline\numberline
  % Keep original numberline behavior - section counters handle LTR

  % Fix TOC page numbers to be LTR (v5.11.7)
  % CRITICAL: hyperref uses 4 arguments, not 3!
  % Format: \contentsline{type}{text}{page}{hyperlink}
  \let\orig@contentsline\contentsline
  \renewcommand{\contentsline}[4]{%
    \orig@contentsline{#1}{#2}{\textenglish{#3}}{#4}%
  }

  % Redefine l@chapter for proper BiDi handling (v5.11.8, fixed v5.12.0)
  % v5.12.0: Added \pardir TRT\textdir TRT for unnumbered entries (bibliography, etc.)
  \renewcommand*\l@chapter[2]{%
    \ifnum \c@tocdepth >\m@ne
      \addpenalty{-\@highpenalty}%
      \vskip 1.0em \@plus\p@
      \setlength{\@tempdima}{1.5em}%
      \begingroup
        \pardir TRT\textdir TRT
        \parindent \z@ \leftskip \z@ \rightskip \@tocrmarg
        \parfillskip -\rightskip
        \leavevmode \bfseries
        \advance\leftskip\@tempdima
        \hskip -\leftskip
        #1\nobreak\leaders\hbox{$\m@th
          \mkern \@dotsep mu\hbox{.}\mkern \@dotsep
          mu$}\hfill\nobreak\hb@xt@\@pnumwidth{\hss {\textdir TLT #2}}\par
        \penalty\@highpenalty
      \endgroup
    \fi
  }

  % Redefine l@section for proper BiDi handling (v5.11.8, fixed v5.12.0)
  % v5.12.0: Added \pardir TRT\textdir TRT for unnumbered entries
  \renewcommand*\l@section[2]{%
    \ifnum \c@tocdepth >\z@
      \addpenalty\@secpenalty
      \addvspace{1.0em \@plus\p@}%
      \setlength{\@tempdima}{2.3em}%
      \begingroup
        \pardir TRT\textdir TRT
        \parindent \z@ \leftskip \z@ \rightskip \@tocrmarg
        \parfillskip -\rightskip
        \leavevmode
        \advance\leftskip\@tempdima
        \hskip -\leftskip
        #1\nobreak\leaders\hbox{$\m@th
          \mkern \@dotsep mu\hbox{.}\mkern \@dotsep
          mu$}\hfill\nobreak\hb@xt@\@pnumwidth{\hss {\textdir TLT #2}}\par
      \endgroup
    \fi
  }

  % Redefine l@subsection for proper BiDi handling (v5.11.9)
  % Use \pardir TRT to make entire paragraph flow RTL
  \renewcommand*\l@subsection[2]{%
    \ifnum \c@tocdepth >\@ne
      \addpenalty{-\@highpenalty}%
      \setlength{\@tempdima}{3.2em}%
      \begingroup
        \pardir TRT\textdir TRT
        \parindent \z@ \leftskip 2.3em \rightskip \@tocrmarg
        \parfillskip -\rightskip
        \leavevmode
        \advance\leftskip\@tempdima
        \hskip -\leftskip
        #1\nobreak\leaders\hbox{$\m@th
          \mkern \@dotsep mu\hbox{.}\mkern \@dotsep
          mu$}\hfill\nobreak\hb@xt@\@pnumwidth{\hss {\textdir TLT #2}}\par
      \endgroup
    \fi
  }

  % v6.2.2: l@englishsubsection for PURELY English TOC entries
  % Use \pardir TRT\textdir TRT (like Hebrew l@subsection) but wrap title+page in LTR
  % This gives: RTL line structure (page left, title right) + LTR title and page
  \newcommand*\l@englishsubsection[2]{%
    \ifnum \c@tocdepth >\@ne
      \addpenalty{-\@highpenalty}%
      \setlength{\@tempdima}{3.2em}%
      \begingroup
        \pardir TRT\textdir TRT
        \parindent \z@ \leftskip 2.3em \rightskip \@tocrmarg
        \parfillskip -\rightskip
        \leavevmode
        \advance\leftskip\@tempdima
        \hskip -\leftskip
        {\textdir TLT #1}\nobreak\leaders\hbox{$\m@th
          \mkern \@dotsep mu\hbox{.}\mkern \@dotsep
          mu$}\hfill\nobreak\hb@xt@\@pnumwidth{\hss {\textdir TLT #2}}\par
      \endgroup
    \fi
  }

  % Redefine l@subsubsection for proper BiDi handling (v5.11.9)
  % Use \pardir TRT to make entire paragraph flow RTL
  \renewcommand*\l@subsubsection[2]{%
    \ifnum \c@tocdepth >\tw@
      \addpenalty{-\@highpenalty}%
      \setlength{\@tempdima}{4.1em}%
      \begingroup
        \pardir TRT\textdir TRT
        \parindent \z@ \leftskip 4.6em \rightskip \@tocrmarg
        \parfillskip -\rightskip
        \leavevmode
        \advance\leftskip\@tempdima
        \hskip -\leftskip
        #1\nobreak\leaders\hbox{$\m@th
          \mkern \@dotsep mu\hbox{.}\mkern \@dotsep
          mu$}\hfill\nobreak\hb@xt@\@pnumwidth{\hss {\textdir TLT #2}}\par
      \endgroup
    \fi
  }

  % ---- Fix standard section commands for Hebrew TOC (v5.11.8, v5.13.1) ----
  % Problem: Standard \section{} and \subsection{} add raw Hebrew to TOC without \texthebrew{}
  % The TOC entry becomes: \contentsline{section}{\numberline{X}Hebrew text}{page}{}
  % where "Hebrew text" is NOT wrapped in \texthebrew{}, causing rendering issues
  % Solution: Override \section and \subsection to use \texthebrew{} wrapper for title in TOC

  % v5.13.1: Store original \section and redefine with Hebrew TOC wrapping
  % This ensures mixed Hebrew/English titles in TOC are properly wrapped
  \let\orig@section\section
  \RenewDocumentCommand{\section}{s o m}{%
    \IfBooleanTF{#1}{% Starred version \section*
      \orig@section*{#3}%
    }{% Non-starred version \section
      % Step section counter
      \refstepcounter{section}%
      % Create heading WITH number (using \the format that's already defined)
      \orig@section*{\thesection\quad #3}%
      % Add to TOC with texthebrew wrapper for Hebrew text
      \phantomsection%
      \IfNoValueTF{#2}{% No optional argument
        \addcontentsline{toc}{section}{\protect\numberline{\thesection}\texthebrew{#3}}%
      }{% Optional argument provided for TOC
        \addcontentsline{toc}{section}{\protect\numberline{\thesection}\texthebrew{#2}}%
      }%
    }%
  }

  % Store original \subsection and redefine with Hebrew TOC wrapping
  % This ensures Hebrew titles in TOC are wrapped with \texthebrew{} for proper RTL rendering
  \let\orig@subsection\subsection
  \RenewDocumentCommand{\subsection}{s o m}{%
    \IfBooleanTF{#1}{% Starred version \subsection*
      \orig@subsection*{#3}%
    }{% Non-starred version \subsection
      % Step subsection counter
      \refstepcounter{subsection}%
      % Create heading WITH number (using \the format that's already defined)
      \orig@subsection*{\thesubsection\quad #3}%
      % Add to TOC with texthebrew wrapper for Hebrew text
      \phantomsection%
      \IfNoValueTF{#2}{% No optional argument
        \addcontentsline{toc}{subsection}{\protect\numberline{\thesubsection}\texthebrew{#3}}%
      }{% Optional argument provided for TOC
        \addcontentsline{toc}{subsection}{\protect\numberline{\thesubsection}\texthebrew{#2}}%
      }%
    }%
  }

  % v5.13.2: Store original \subsubsection and redefine with Hebrew TOC wrapping
  % This ensures Hebrew titles in TOC are wrapped with \texthebrew{} for proper RTL rendering
  \let\orig@subsubsection\subsubsection
  \RenewDocumentCommand{\subsubsection}{s o m}{%
    \IfBooleanTF{#1}{% Starred version \subsubsection*
      \orig@subsubsection*{#3}%
    }{% Non-starred version \subsubsection
      % Step subsubsection counter
      \refstepcounter{subsubsection}%
      % Create heading WITH number (using \the format that's already defined)
      \orig@subsubsection*{\thesubsubsection\quad #3}%
      % Add to TOC with texthebrew wrapper for Hebrew text
      \phantomsection%
      \IfNoValueTF{#2}{% No optional argument
        \addcontentsline{toc}{subsubsection}{\protect\numberline{\thesubsubsection}\texthebrew{#3}}%
      }{% Optional argument provided for TOC
        \addcontentsline{toc}{subsubsection}{\protect\numberline{\thesubsubsection}\texthebrew{#2}}%
      }%
    }%
  }

  % v5.13.2: Store original \chapter and redefine with Hebrew TOC wrapping
  % This ensures chapter titles in TOC are wrapped with \texthebrew{} for proper RTL rendering
  \let\orig@chapter\chapter
  \RenewDocumentCommand{\chapter}{s o m}{%
    \IfBooleanTF{#1}{% Starred version \chapter*
      \orig@chapter*{#3}%
    }{% Non-starred version \chapter
      % Use original chapter command for the heading (it handles counter stepping)
      \IfNoValueTF{#2}{% No optional argument
        \orig@chapter{#3}%
      }{% Optional argument provided
        \orig@chapter[#2]{#3}%
      }%
      % Override the TOC entry that was just added - remove it and add our own
      % Note: We can't easily intercept, so we let the original add its entry
      % and rely on the \texthebrew{} wrapper being added by l@chapter handler
      % Actually, we need to modify how chapter adds to TOC
    }%
  }
  % Better approach: Patch the TOC entry directly by redefining \@chapter
  % This is the internal command that \chapter uses
  \let\orig@@chapter\@chapter
  \def\@chapter[#1]#2{%
    \orig@@chapter[\texthebrew{#1}]{\texthebrew{#2}}%
  }

  % ---- Hebrew Appendix Command ----
  % Creates Hebrew appendix chapters with proper RTL formatting
  \newcounter{hebrewappendix}
  \renewcommand{\thehebrewappendix}{\hebrewAlph{hebrewappendix}}
  % Hebrew letter numbering for appendices
  \newcommand{\hebrewAlph}[1]{%
    \ifcase\value{#1}\or א\or ב\or ג\or ד\or ה\or ו\or ז\or ח\or ט\or י%
    \or יא\or יב\or יג\or יד\or טו\or טז\or יז\or יח\or יט\or כ\fi%
  }
  \newcommand{\hebrewappendix}[1]{%
    \clearpage%
    \refstepcounter{hebrewappendix}%
    \chapter*{\appendixname{} \thehebrewappendix: #1}%
    \phantomsection%
    \addcontentsline{toc}{chapter}{\appendixname{} \thehebrewappendix: #1}%
  }

  % ---- Redefine hebrewchapter for book mode ----
  % Uses native \chapter* internally for proper book structure
  \renewcommand{\hebrewchapter}[1]{%
    \clearpage%
    \refstepcounter{hebrewchapter}%
    \setcounter{hebrewsection}{0}%
    \xdef\hcchapternum{\thehebrewchapter}%
    \chapter*{\HebrewTitle{\thehebrewchapter}{#1}}%
    \phantomsection%
    \addcontentsline{toc}{chapter}{\HebrewTitle{\thehebrewchapter}{#1}}%
    \setcounter{section}{\value{hebrewchapter}}%
  }
\fi
\makeatother

%% ==================== TABLE ENVIRONMENT ====================

% Hebrew table environment with RTL orientation
% FIXED in v5.2: Changed caption from raggedleft to centering for proper Hebrew table formatting
\newenvironment{hebrewtable}[1][htbp]{%
  \begin{table}[#1]%
  \begingroup%
  \renewcommand{\arraystretch}{1.2}%
  \captionsetup{justification=centering,singlelinecheck=false}% FIXED v5.2: centering for Hebrew academic tables
  \centering%
}{%
  \endgroup%
  \end{table}%
}

% RTL tabular environment - for Hebrew tables with RTL column order
% IMPORTANT: Columns must be written in REVERSE order (right-to-left)
% Example for 3-column table:
%   Visual RTL order: [Col3] [Col2] [Col1]
%   LaTeX code order: Col3 & Col2 & Col1 \\
%   (rightmost column first, leftmost column last)
% 
% USAGE PATTERN:
%   - Use m{width} column type for vertical centering (not p{width})
%   - Hebrew cells: wrap with \hebcell{Hebrew text \en{English/formulas} more Hebrew}
%   - English cells: use \en{English text} directly without \hebcell{}
%   - Formulas in Hebrew cells: \hebcell{Hebrew \en{$formula$} Hebrew}
%   - No spaces inside \en{}: use \en{$formula$} not \en{ $formula$ }
% 
% Example column spec: {|m{5.5cm}|m{2cm}|m{3cm}|}
%   - All columns use m{} for vertical centering
%   - Hebrew columns will be right-aligned via \hebcell{}
%   - English columns will be left-aligned via \en{}
\newenvironment{rtltabular}[1]{%
  \begin{tabular}{#1}%
}{%
  \end{tabular}%
}

% \hebcell{} - Hebrew RTL table cell with mixed language support
% 
% PURPOSE: Creates right-aligned RTL cells that support mixed Hebrew/English content
% 
% FEATURES:
%   - Forces RTL (right-to-left) text direction for entire cell
%   - Right-aligns Hebrew text automatically
%   - Supports nested \en{} for English/formulas (remain LTR inline)
%   - Removes leading/trailing whitespace (no empty lines)
%   - Adds vertical padding: 0.5ex top and bottom (~half font height)
%   - Works with m{} column type for vertical centering
% 
% USAGE:
%   \hebcell{Hebrew text}                           % Pure Hebrew
%   \hebcell{Hebrew \en{English} more Hebrew}       % Mixed content
%   \hebcell{Hebrew \en{$formula$} explanation}     % With formulas
%   \hebcell{\en{Symbol} Hebrew explanation}        % English symbol + Hebrew
% 
% IMPORTANT:
%   - Always use with m{width} column type (not p{width}) for vertical centering
%   - Never put spaces inside \en{}: use \en{text} not \en{ text }
%   - For pure English cells, use \en{} directly without \hebcell{}
% 
\newcommand{\hebcell}[1]{%
  \bgroup%
  \textdir TRT\pardir TRT%
  \everypar{\textdir TRT\pardir TRT}%
  \selectlanguage{hebrew}%
  \rightskip=0pt\leftskip=0pt plus 1fil\relax%
  \mbox{}\par\vspace{+0.2\baselineskip}\vspace{0.5ex}%
  \ignorespaces#1\unskip%
  \vspace*{0.5ex}%
  \egroup%
}

% \encell{} - English LTR table cell with vertical padding
% 
% PURPOSE: Creates left-aligned LTR cells for pure English content
% 
% FEATURES:
%   - Left-aligns English text automatically
%   - Adds vertical padding (0.5ex top and bottom)
%   - For pure English cells (no Hebrew content)
% 
% USAGE:
%   \encell{English text}          % Pure English cell
%   \encell{np.dot(u, v)}          % Function names
%   \encell{$formula$}             % English formulas
% 
\newcommand{\encell}[1]{%
  \bgroup%
  \mbox{}\par\vspace{+0.2\baselineskip}\vspace{0.5ex}%
  #1%
  \vspace*{0.5ex}%
  \egroup%
}

% \hebheader{} - Hebrew RTL table header cell (for single-line headers)
% For use in table column headers - supports mixed Hebrew/English/formulas
% Usage: \textbf{\hebheader{Hebrew title \en{English} more Hebrew}}
% Fixed: Uses \par to activate \leftskip/\rightskip for proper RTL right-alignment
\newcommand{\hebheader}[1]{%
  \bgroup%
  \textdir TRT\pardir TRT%
  \everypar{\textdir TRT\pardir TRT}%
  \selectlanguage{hebrew}%
  \rightskip=0pt\leftskip=0pt plus 1fil\relax%
  \mbox{}\par\vspace{-0.5\baselineskip}%
  \ignorespaces#1\unskip%
  \egroup%
}

% \enheader{} - English LTR table header cell (for single-line headers)
% For use in table column headers - pure English content
% Usage: \textbf{\enheader{English Title}}
\newcommand{\enheader}[1]{%
  \bgroup%
  \vspace*{0.5ex}%
  #1%
  \vspace*{0.5ex}%
  \egroup%
}

% \mixedcell{} - Deprecated, use \hebcell{} instead
% Kept for backward compatibility with existing tables
\newcommand{\mixedcell}[1]{\hebcell{#1}}

% OPTIONAL: \rtlrow{} helper command from v1.0 (for beginners)
% Auto-reverses columns for RTL tables
\newcommand{\rtlrow}[2][0]{%
  % Implementation would go here if included
  % Currently omitted as recommended by Agent B
}

%% ==================== BIBLIOGRAPHY SETUP ====================

% Suppress split bibliography warning
\BiblatexSplitbibDefernumbersWarningOff

% Custom command to force LTR numbers like page numbers
\newcommand{\ltrnumber}[1]{\textenglish{#1}}

% Custom formatting for ALL bibliography entries
% Use the exact same approach as working page numbers
\AtBeginDocument{
  \DeclareFieldFormat{year}{\ltrnumber{#1}}%
  \DeclareFieldFormat{pages}{\ltrnumber{#1}}%
  \DeclareFieldFormat{volume}{\ltrnumber{#1}}%
  \DeclareFieldFormat{number}{\ltrnumber{#1}}%
  % Force LTR formatting for citation labels (like [19])
  \DeclareFieldFormat{labelnumber}{\ltrnumber{#1}}%
  \DeclareFieldFormat{labelnumberwidth}{\ltrnumber{#1}}%
  % Also ensure citation commands use LTR
  \DeclareCiteCommand{\cite}
    {\usebibmacro{prenote}}%
    {\usebibmacro{citeindex}%
     \printtext[bibhyperref]{\ltrnumber{[\usebibmacro{cite}]}}}%
    {\multicitedelim}%
    {\usebibmacro{postnote}}%
  % Override the default bracket formatting to use LTR
  \DeclareFieldFormat{bibhyperref}{\ltrnumber{#1}}%
}

% Hebrew bibliography command - shows title in Hebrew RTL, aligned right
% Only shows Hebrew references (keywords=hebrew)
% v6.3.0: Uses \hebrewsectionnotoc - NO TOC entry (only English References in TOC)
\newcommand{\printhebrewbibliography}{%
  \defbibcheck{hebrewcheck}{\ifkeyword{hebrew}{}{\skipentry}}%
  \hebrewsectionnotoc{מקורות בעברית}%
  \printbibliography[check=hebrewcheck,heading=none]%
}

% English bibliography command - shows title in English LTR, aligned left
% Only shows English references (keywords=english)
% v6.0.0: FIXED - now uses unnumbered section (like Hebrew מקורות)
%         This fixes the TOC numbering gap issue (4.10→4.12, 5.7→5.13)
\newcommand{\printenglishbibliography}{%
  \defbibcheck{englishcheck}{\ifkeyword{english}{}{\skipentry}}%
  \englishsectionunnumbered{English References}%
  \begin{english}%
  \pardir TLT%
  \printbibliography[check=englishcheck,heading=none]%
  \end{english}%
}

%% ==================== HEADER AND FOOTER ====================

% \hebfoot{} - Hebrew RTL footer/header with mixed language support
% 
% PURPOSE: Creates RTL footer/header text that supports mixed Hebrew/English content
% 
% FEATURES:
%   - Forces RTL (right-to-left) text direction for footer/header
%   - Supports nested \en{} for English text (remains LTR inline)
%   - Works within fancyhdr context (which defaults to LTR)
%   - Similar to \hebcell{} but optimized for single-line footer/header context
% 
% USAGE:
%   \hebfoot{Hebrew text}                           % Pure Hebrew
%   \hebfoot{Hebrew \en{English} more Hebrew}       % Mixed content
%   \hebfoot{כל הזכויות שמורות - \en{© Dr. Name}}  % Copyright line
% 
% IMPORTANT:
%   - fancyhdr operates in LTR context even in RTL documents
%   - \texthebrew{} alone is NOT sufficient - use \hebfoot{} instead
%   - Always use \en{} for embedded English text within \hebfoot{}
% 
\newcommand{\hebfoot}[1]{%
  \bgroup%
  \textdir TRT\pardir TRT%
  \selectlanguage{hebrew}%
  #1%
  \egroup%
}

% \hebtitle{} - Hebrew RTL tcolorbox/pythonbox title with mixed language support
% 
% PURPOSE: Creates RTL title text for tcolorbox-based environments (pythonbox, etc.)
% 
% FEATURES:
%   - Forces RTL (right-to-left) text direction for title
%   - Supports nested \en{} for English text (remains LTR inline)
%   - Works within tcolorbox title context
%   - Prevents environment stack corruption from Hebrew in LTR context
% 
% USAGE EXAMPLES:
%   \begin{pythonbox}[\hebtitle{כותרת בעברית}]
%   \begin{pythonbox}[\hebtitle{פתרון \en{SVM} עם \en{cvxopt}}]
%   \begin{pythonbox}[\hebtitle{דוגמה מלאה: מנתונים לחיזוי}]
% 
% NOTES:
%   - Always use \hebtitle{} for Hebrew titles in pythonbox/tcolorbox
%   - For mixed content: \hebtitle{Hebrew \en{English} more Hebrew}
%   - Pure English titles don't need wrapping
% 
% \hebtitle{} implementation that avoids BiDi environment corruption
% Simple wrapper that uses brace grouping (no begingroup/endgroup)
% This works inside tcolorbox/tcblisting titles
\newcommand{\hebtitle}[1]{{\texthebrew{#1}}}

% Page style configuration
\pagestyle{fancy}
\fancyhf{} % Clear all header/footer fields

% Footer setup with rights and page numbers
% FIXED v5.5: Using \hebfoot{} for proper RTL Hebrew with \en{} for English
% FIXED v6.3.3: Using \textdir TLT with \thepage (preserves Roman/Arabic from frontmatter/mainmatter)
\fancyfoot[LE]{{\textdir TLT\thepage}} % Page number on left for even pages
\fancyfoot[RO]{{\textdir TLT\thepage}} % Page number on right for odd pages
\fancyfoot[RE]{\hebfoot{כל הזכויות שמורות - \en{© Dr. Segal Yoram}}} % Rights on right for even pages
\fancyfoot[LO]{\hebfoot{כל הזכויות שמורות - \en{© Dr. Segal Yoram}}} % Rights on left for odd pages

% v6.3.3: Define plain page style for chapter openings with LTR page numbers
\fancypagestyle{plain}{%
  \fancyhf{}% Clear all
  \fancyfoot[C]{{\textdir TLT\thepage}}% Centered page number with LTR
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
}

% Remove header rule
\renewcommand{\headrulewidth}{0pt}
% make @ a letter for internal macros
\makeatletter
% Keep footer rule
\renewcommand{\footrulewidth}{0.4pt}

%% ==================== DOCUMENT SPACING ====================

% Set line spacing
\onehalfspacing

%% ==================== MATHEMATICAL EXPRESSIONS ====================

% Ensure math mode always uses LTR
\AtBeginDocument{
  \mathdir TLT%
}

% Define common math operators
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}

% Command for Hebrew text inside math formulas
% Usage: $\hebmath{טקסט עברי}$ will display Hebrew RTL inside LTR math
\newcommand{\hebmath}[1]{%
  \text{\begingroup\selectlanguage{hebrew}\textdir TRT #1\endgroup}%
}

% Alternative: Hebrew subscript in math (e.g., x_{\hebsub{עברי}})
\newcommand{\hebsub}[1]{%
  \text{\scriptsize\begingroup\selectlanguage{hebrew}\textdir TRT #1\endgroup}%
}

%% ==================== SPECIAL CHARACTERS FIX ====================

% Fix for special characters in Hebrew fonts that don't support them

% Use \Rsquared instead of R² in Hebrew text
\newcommand{\Rsquared}{%
  \ensuremath{R^2}%
}

% Fix for → (arrow) character - use leftarrow in RTL Hebrew context
% In Hebrew RTL text, logical "implies" (→) should visually point left (←)
\newcommand{\rarrow}{%
  $\leftarrow$%
}

% Alternative: for inline text (not in math mode)
\newcommand{\Rtwo}{%
  R\textsuperscript{2}%
}

%% ==================== TITLE PAGE COMMANDS ====================

\newcommand{\hebrewtitle}[1]{\def\@hebrewtitle{#1}}
\newcommand{\englishtitle}[1]{\def\@englishtitle{#1}}
\newcommand{\hebrewsubtitle}[1]{\def\@hebrewsubtitle{#1}}
\newcommand{\hebrewauthor}[1]{\def\@hebrewauthor{#1}}
\newcommand{\hebrewversion}[1]{\def\@hebrewversion{#1}}

% Custom title page for Hebrew documents
\renewcommand{\maketitle}{%
  \begin{titlepage}%
    \null\vfil%
    \begin{center}%
      \texthebrew{\LARGE\bfseries\@hebrewtitle}\par%
      \vskip 1em%
      \textenglish{\Large\bfseries\@englishtitle}\par%
      \ifdefined\@hebrewsubtitle%
        \vskip 0.5em%
        {\large \texthebrew{\@hebrewsubtitle} \par}%
      \fi%
      \vskip 3em%
      \ifdefined\@hebrewauthor%
        {\large \texthebrew{\@hebrewauthor} \par}%
        \vskip 0.5em%
        {\large \hebfoot{כל הזכויות שמורות - \en{©} \@hebrewauthor} \par}%
      \else%
        {\large \@author \par}%
      \fi%
      \vskip 2em%
      {\large \@date \par}%
      \ifdefined\@hebrewversion%
        \vskip 1em%
        {\large \texthebrew{\@hebrewversion} \par}%
      \fi%
    \end{center}%
    \vfil\null%
  \end{titlepage}%
}

%% ==================== CUSTOM LISTS ====================

\newcommand{\Hitem}[1]{\item \texthebrew{#1}}

%% ==================== ADDITIONAL UTILITIES ====================

\makeatother
% end @-macros block

% Command for creating Hebrew figures with proper numbering
\newcommand{\hebrewfigure}[3][htbp]{%
  \begin{figure}[#1]%
    \centering%
    #2%
    \caption{#3}%
  \end{figure}%
}

% Command for inline code with proper font
\newcommand{\code}[1]{\en{\texttt{#1}}}

% Command for English terms in Hebrew text
\newcommand{\englishterm}[1]{\en{\textit{#1}}}

%% ==================== CODE ENVIRONMENTS ====================

% Require additional packages for professional code styling
\RequirePackage[table]{xcolor}

% Define light gray color for code background
\definecolor{codegray}{RGB}{245,245,245}

% Professional code block environment with light gray background and LTR direction
% Using tcolorbox with listings for proper LTR code display
\RequirePackage{tcolorbox}
\tcbuselibrary{listings,skins,breakable}
\RequirePackage{fvextra}

% Define a custom listing style for LTR code using tcblisting
\RequirePackage{newfloat}
\DeclareFloatingEnvironment[fileext=lop,placement=htbp,name=Listing]{python}

% Global listings configuration to prevent visible space markers
\lstset{
  showspaces=false,
  showstringspaces=false,
  showtabs=false,
  keepspaces=true,
  columns=flexible
}

\newcommand{\pythonverbatimformat}{%
  \selectlanguage{english}%
  \textdir TLT\pardir TLT%
  \ttfamily\footnotesize%
}

\newtcblisting{pythonbox}[1][]{%
  listing engine=listings,
  listing only,
  breakable,
  colback=codegray,
  colframe=codegray,
  arc=2pt,
  boxrule=0pt,
  left=8pt,
  right=8pt,
  top=8pt,
  bottom=8pt,
  fonttitle=\bfseries,
  coltitle=black,
  title=#1,
  before upper={\selectlanguage{english}\textdir TLT\pardir TLT},
  listing options={
    basicstyle=\pythonverbatimformat,
    tabsize=4,
    breaklines=true,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    keepspaces=true,
    columns=fullflexible,
    language=Python
  }
}

% Non-floating version of pythonbox for long code blocks
% Use pythonbox* when code is too long and overflows the page
% 
% IMPORTANT: If pythonbox* code still overflows into footer:
% SOLUTION - Simplify code to show ONLY core functions:
%   - Remove: imports of non-core libraries (matplotlib, sklearn examples)
%   - Remove: print statements, docstrings, example data generation
%   - Remove: visualization code (UNLESS it IS the main topic)
%   - Keep: ONLY the core algorithm/function being demonstrated
% Alternative: Convert to Python pseudocode instead of executable code
% 
\newtcblisting{pythonbox*}[1][]{%
  listing engine=listings,
  listing only,
  colback=codegray,
  colframe=codegray,
  arc=2pt,
  boxrule=0pt,
  left=8pt,
  right=8pt,
  top=8pt,
  bottom=8pt,
  fonttitle=\bfseries,
  coltitle=black,
  title=#1,
  before upper={\selectlanguage{english}\textdir TLT\pardir TLT},
  listing options={
    basicstyle=\pythonverbatimformat,
    tabsize=4,
    breaklines=true,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    keepspaces=true,
    columns=fullflexible,
    language=Python
  }
}

%% ==================== BiDi-SAFE TCOLORBOX ENVIRONMENTS (v5.11.0) ====================
% Wrapper pattern to prevent RTL background overflow in tcolorbox
% Problem: tcolorbox calculates position based on text direction
% In RTL context, boxes draw from right and extend left, causing overflow
% Solution: Wrap box in LTR context, restore RTL for content inside

% Internal box definitions (with @inner suffix)
\newtcolorbox{notebox@inner}[1][]{%
  enhanced,
  breakable,
  colback=yellow!10,
  colframe=yellow!50!black,
  fonttitle=\bfseries,
  title={\texthebrew{#1}},
  halign title=flush right,
  arc=2mm,
  boxrule=1pt
}

\newtcolorbox{warningbox@inner}[1][]{%
  enhanced,
  breakable,
  colback=red!5,
  colframe=red!70!black,
  fonttitle=\bfseries,
  title={\texthebrew{#1}},
  halign title=flush right,
  arc=2mm,
  boxrule=1pt
}

\newtcolorbox{examplebox@inner}[1][]{%
  enhanced,
  breakable,
  colback=blue!5,
  colframe=blue!50!black,
  fonttitle=\bfseries,
  title={\texthebrew{#1}},
  halign title=flush right,
  arc=3mm,
  boxrule=1pt
}

\newtcolorbox{exercisebox@inner}[1][]{%
  enhanced,
  breakable,
  colback=orange!5,
  colframe=orange!70!black,
  fonttitle=\bfseries,
  title={\texthebrew{#1}},
  halign title=flush right,
  arc=3mm,
  boxrule=1pt
}

\newtcolorbox{formulabox@inner}[1][]{%
  enhanced,
  breakable,
  colback=green!5,
  colframe=green!50!black,
  fonttitle=\bfseries,
  title={\texthebrew{#1}},
  halign title=flush right,
  arc=2mm,
  boxrule=0.5pt
}

\newtcolorbox{codebox@inner}[1][]{%
  enhanced,
  breakable,
  colback=codegray,
  colframe=gray!50,
  fonttitle=\bfseries\ttfamily,
  title={\texthebrew{#1}},
  halign title=flush right,
  arc=2mm,
  boxrule=0.5pt
}

% BiDi-safe wrapper environments
% Force LTR for box drawing, RTL for content inside
\newenvironment{notebox}[1][]
  {\begin{english}\begin{notebox@inner}[#1]\selectlanguage{hebrew}}
  {\end{notebox@inner}\end{english}}

\newenvironment{warningbox}[1][]
  {\begin{english}\begin{warningbox@inner}[#1]\selectlanguage{hebrew}}
  {\end{warningbox@inner}\end{english}}

\newenvironment{examplebox}[1][]
  {\begin{english}\begin{examplebox@inner}[#1]\selectlanguage{hebrew}}
  {\end{examplebox@inner}\end{english}}

\newenvironment{exercisebox}[1][]
  {\begin{english}\begin{exercisebox@inner}[#1]\selectlanguage{hebrew}}
  {\end{exercisebox@inner}\end{english}}

\newenvironment{formulabox}[1][]
  {\begin{english}\begin{formulabox@inner}[#1]\selectlanguage{hebrew}}
  {\end{formulabox@inner}\end{english}}

\newenvironment{codebox}[1][]
  {\begin{english}\begin{codebox@inner}[#1]\selectlanguage{hebrew}}
  {\end{codebox@inner}\end{english}}

%% ==================== CODE LISTING FONT SUPPORT ====================

% Command for use in lstlisting basicstyle to ensure Courier New is used
% This fixes hyphens in listing body text AND captions
\newcommand{\listingfont}{\courierfont}

% Command for paths/filenames with hyphens in captions and text
% Usage: caption={\enpath{/mnt/user-data}} or caption={\enpath{Fork-Join}}
% Made robust to work in moving arguments like lstlisting captions
\DeclareRobustCommand{\enpath}[1]{%
  {\courierfont\LTR{#1}}%
}

%% ==================== COMPATIBILITY ENVIRONMENTS ====================

% latin environment - alias for english (for backward compatibility)
\newenvironment{latin}{\begin{english}}{\end{english}}

% exercise environment - alias for exercisebox (for backward compatibility)
\newenvironment{exercise}[1][]{\begin{exercisebox}[#1]}{\end{exercisebox}}

% definition environment - for mathematical/conceptual definitions
\newtcolorbox{definition@inner}[1][]{%
  enhanced,
  breakable,
  colback=blue!5,
  colframe=blue!40!black,
  fonttitle=\bfseries,
  title={\texthebrew{#1}},
  halign title=flush right,
  arc=2mm,
  boxrule=1pt
}
\newenvironment{definition}[1][]
  {\begin{english}\begin{definition@inner}[#1]\selectlanguage{hebrew}}
  {\end{definition@inner}\end{english}}

% abstract environment for book mode (title-page style abstract)
\makeatletter
\if@bookmode
  \newenvironment{abstract}{%
    \begin{center}
    {\large\bfseries תקציר}
    \end{center}
    \begin{quotation}
  }{%
    \end{quotation}
  }
\fi
\makeatother

%% ==================== DOCUMENT LAYOUT ====================

% A4 paper with appropriate margins for Hebrew
\RequirePackage[a4paper, margin=2.5cm]{geometry}

% Book mode: prevent excessive vertical stretching between elements
\makeatletter
\if@bookmode
  \raggedbottom
\fi
\makeatother

% Subfiles support for modular book structure
\RequirePackage{subfiles}

%% ==================== END OF CLASS ====================

\endinput
