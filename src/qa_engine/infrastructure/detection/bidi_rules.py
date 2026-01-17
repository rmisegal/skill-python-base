"""
BiDi detection rules definitions.

All 15 rules as specified in QA-CLAUDE-MECHANISM-ARCHITECTURE-REPORT.md.
Each rule is regex-based and can be enforced deterministically via Python.
"""

from ...domain.models.issue import Severity

# Hebrew final letters that should not appear at word start
HEBREW_FINAL_LETTERS = "ךםןףץ"

BIDI_RULES = {
    # Rule 1: Cover Page Metadata
    "bidi-cover-metadata": {
        "description": "Unwrapped Hebrew/English in document preamble",
        "pattern": r"\\(title|author|date)\{([^}]*[א-ת][^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Wrap with \\texthebrew{{}} or \\he{{}}",
    },
    # Rule 3: Section Numbering
    "bidi-section-number": {
        "description": "Section with Hebrew text may have numbering issues",
        "pattern": r"\\section\{([^}]*[א-ת][^}]*)\}",
        "severity": Severity.INFO,
        "fix_template": "Consider using \\hebrewsection{{}}",
    },
    # Rule 4: Reversed Text (final letters at word start)
    "bidi-reversed-text": {
        "description": "Hebrew final letter at word start indicates reversed text",
        "pattern": rf"(?:^|[ \t])([{HEBREW_FINAL_LETTERS}][א-ת]*)",
        "severity": Severity.CRITICAL,
        "context_pattern": r"[א-ת]",
        "fix_template": "Check text direction - final letter at start",
    },
    # Rule 5: Header/Footer Hebrew
    "bidi-header-footer": {
        "description": "Hebrew in fancyhdr without RTL wrapper",
        "pattern": r"\\(lhead|chead|rhead|lfoot|cfoot|rfoot)\{([^}]*[א-ת][^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Wrap Hebrew text with \\texthebrew{{}}",
    },
    # Rule 6: Numbers Without LTR
    "bidi-numbers": {
        "description": "Numbers without LTR wrapper in Hebrew context",
        "pattern": r"(?<![\\a-zA-Z0-9{])(\d+(?:[.,]\d+)*)(?![}\\\da-zA-Z-])",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "exclude_pattern": r"\\num\{|\\percent\{|\\hebyear\{|\\textenglish\{|\$|\\\\|\\begin\{equation|\\begin\{align|\\frac\{|\\int_|\\sum_|\\prod_|\\cite\{|\\cite\[",
        "fix_template": "\\en{{{}}}",
        "skip_math_mode": True,
        "skip_cite_context": True,
        "skip_tikz_env": True,  # Don't wrap numbers in TikZ (coordinates, dimensions)
        "skip_color_context": True,  # Don't wrap numbers in color specs (purple!5)
    },
    # Rule 6b: Year Ranges (2025-2026) Without LTR
    "bidi-year-range": {
        "description": "Year range without LTR wrapper in Hebrew context",
        "pattern": r"(?<![\\a-zA-Z0-9{])((?:19|20)\d{2}-(?:19|20)\d{2})(?![\\\da-zA-Z])",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "exclude_pattern": r"\\hebyear\{|\\textenglish\{|\\en\{",
        "fix_template": "\\hebyear{{{}}}",
        "skip_math_mode": True,
        "skip_cite_context": True,
    },
    # Rule 6c: Partial Year Range - wrapped year followed by unwrapped year
    "bidi-partial-year-range": {
        "description": "Year range with first year wrapped but second unwrapped",
        # Match wrapped-year DASH bare-year - captures the unwrapped second year
        "pattern": r"\\(?:hebyear|en|textenglish)\{(?:19|20)\d{2}\}[–\-]((?:19|20)\d{2})",
        "severity": Severity.CRITICAL,
        "context_pattern": r"[א-ת]",
        "fix_template": "Wrap full range with \\en{{XXXX–{}}}",
        "note": "Causes reversed rendering like 2025– becoming –5202 in RTL",
    },
    # Rule 6d: Dash followed by unwrapped year in Hebrew context
    "bidi-dash-year": {
        "description": "Dash followed by year without wrapper in Hebrew context",
        "pattern": r"[–\-]((?:19|20)\d{2})(?![}\d])",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "exclude_pattern": r"\\en\{|\\hebyear\{|\\textenglish\{",
        "fix_template": "Wrap with preceding content: \\en{{XXXX–{}}}",
    },
    # Rule 7: English Without LTR
    "bidi-english": {
        "description": "English words without LTR wrapper in Hebrew",
        "pattern": r"(?<![\\a-zA-Z])([a-zA-Z]{2,})(?![}a-zA-Z=])",  # Added = to negative lookahead
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "fix_template": "\\en{{{}}}",
        "exclude_pattern": r"\\en\{|\\textenglish\{|\\texttt\{|\\cite\{|\\cite\[|\\ref\{|\\label\{|\\hebtitle\{|\\entoc\{|\\ilm\{|\\url\{|\\href\{|\\includegraphics|\\bibliographystyle|\\addbibresource|\\newtcolorbox|\\newenvironment",
        "skip_math_mode": True,
        "skip_cite_context": True,
        "skip_tikz_env": True,  # Don't wrap TikZ commands (node, draw, at, of, etc.)
        "skip_color_context": True,  # Don't wrap color names (purple, green, black)
    },
    # Rule 8: tcolorbox BiDi-Safe (includes custom tcolorbox environments)
    "bidi-tcolorbox": {
        "description": "tcolorbox/custom box without BiDi-safe wrapper in RTL context",
        "pattern": r"\\begin\{(tcolorbox|importantbox|notebox|examplebox|summarybox|questionbox|answerbox|codebox|pythonbox)\}",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "document_context": True,
        "exclude_pattern": r"\\begin\{english\}",
        "fix_template": "Wrap in \\begin{{english}}...\\end{{english}}",
        "note": "Custom boxes defined via \\newtcolorbox inherit BiDi issues from tcolorbox",
    },
    # Rule 9: Section Titles with English
    "bidi-section-english": {
        "description": "English text in Hebrew section title without wrapper",
        "pattern": r"\\(section|subsection|chapter)\{([^}]*[א-ת][^}]*[a-zA-Z]{3,}[^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Wrap English with \\en{{}}",
    },
    # Rule 10: Uppercase Acronyms
    "bidi-acronym": {
        "description": "Uppercase acronyms without LTR wrapper",
        "pattern": r"(?<![A-Z\\])([A-Z]{2,6})(?![}A-Z])",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "exclude_pattern": r"\\en\{|\\textenglish\{",
        "fix_template": "\\en{{{}}}",
        "skip_tikz_env": True,  # Don't wrap TikZ style names (RGB, etc.)
        "skip_color_context": True,  # Don't wrap color acronyms (RGB, HSB, etc.)
    },
    # Rule 12: Chapter Labels
    "bidi-chapter-label": {
        "description": "\\label immediately after \\hebrewchapter may not work",
        "pattern": r"\\hebrewchapter\{[^}]*\}\s*\\label\{([^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Move \\label inside or use \\refstepcounter",
    },
    # Rule 13: fbox/parbox Mixed Content
    "bidi-fbox-mixed": {
        "description": "Mixed Hebrew/English in fbox/parbox without wrapper",
        "pattern": r"\\(fbox|parbox|mbox)\{([^}]*[א-ת][^}]*[a-zA-Z][^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Wrap appropriately with \\texthebrew{{}} or \\en{{}}",
    },
    # Rule 14: Standalone Counter
    "bidi-standalone-counter": {
        "description": "Document using subfiles without chapter counter setup",
        "pattern": r"\\documentclass\[[^\]]*hebrew-academic[^\]]*\]\{subfiles\}",
        "severity": Severity.INFO,
        "negative_pattern": r"\\setcounter\{chapter\}",
        "fix_template": "Add \\setcounter{{chapter}}{{N}} for standalone",
    },
    # Rule 15: Hebrew in English Wrapper
    "bidi-hebrew-in-english": {
        "description": "Hebrew text inside \\en{} or english environment",
        "pattern": r"\\en\{([^}]*[א-ת]+[^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Remove Hebrew from English wrapper or restructure",
    },
    # Rule 16: Missing hebrewchapter counter in subfiles
    "bidi-missing-hebrewchapter": {
        "description": "Subfile sets chapter counter but not hebrewchapter - causes wrong section numbering",
        "pattern": r"\\setcounter\{chapter\}\{(\d+)\}",
        "severity": Severity.CRITICAL,
        "negative_pattern": r"\\setcounter\{hebrewchapter\}",
        "fix_template": "Add \\setcounter{{hebrewchapter}}{{{}}} after chapter counter",
    },
    # Rule: TikZ in RTL
    "bidi-tikz-rtl": {
        "description": "TikZ figure in RTL context without english wrapper",
        "pattern": r"\\begin\{tikzpicture\}",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "document_context": True,
        "exclude_pattern": r"\\begin\{english\}",
        "fix_template": "Wrap in \\begin{{english}}...\\end{{english}}",
    },
}
