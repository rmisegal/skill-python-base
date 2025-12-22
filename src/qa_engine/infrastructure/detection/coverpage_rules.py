"""
Coverpage detection rules definitions.

Source-level detection for cover page metadata issues.
PDF-level validation still requires LLM (qa-coverpage skill).
"""

from ...domain.models.issue import Severity

# Hebrew character ranges
HEBREW_CHARS = r"[א-ת]"
HEBREW_FINAL_LETTERS = "ךםןףץ"

COVERPAGE_RULES = {
    # Rule 1: Hebrew title without proper wrapper
    "cover-hebrew-title": {
        "description": "Hebrew title command without RTL wrapper",
        "pattern": r"\\hebrewtitle\{([^}]*)\}",
        "check_content": True,  # Check if content needs wrapper
        "severity": Severity.WARNING,
        "fix_template": "Ensure Hebrew title uses proper RTL direction",
    },
    # Rule 2: Hebrew subtitle issues
    "cover-hebrew-subtitle": {
        "description": "Hebrew subtitle with potential BiDi issues",
        "pattern": r"\\hebrewsubtitle\{([^}]*)\}",
        "check_content": True,
        "severity": Severity.WARNING,
        "fix_template": "Wrap English/numbers with \\en{{}}",
    },
    # Rule 3: Hebrew author name issues
    "cover-hebrew-author": {
        "description": "Hebrew author with potential BiDi issues",
        "pattern": r"\\hebrewauthor\{([^}]*)\}",
        "check_content": True,
        "severity": Severity.WARNING,
        "fix_template": "Ensure proper RTL for Hebrew names",
    },
    # Rule 4: English in Hebrew metadata without wrapper
    "cover-english-in-hebrew": {
        "description": "English text in Hebrew metadata without \\en{{}}",
        "pattern": r"\\hebrew(title|subtitle|author|version)\{([^}]*[a-zA-Z]{3,}[^}]*)\}",
        "exclude_pattern": r"\\en\{",
        "severity": Severity.WARNING,
        "fix_template": "Wrap English with \\en{{{}}}",
    },
    # Rule 5: Numbers in Hebrew metadata without wrapper
    "cover-numbers-unwrapped": {
        "description": "Numbers in Hebrew metadata without \\en{{}}",
        "pattern": r"\\hebrew(title|subtitle|version)\{([^}]*\d+[.,]?\d*[^}]*)\}",
        "exclude_pattern": r"\\en\{",
        "severity": Severity.INFO,
        "fix_template": "Wrap numbers with \\en{{{}}}",
    },
    # Rule 5b: Version number with \num{} instead of \en{} (CRITICAL)
    "cover-version-num-wrong": {
        "description": "Version uses \\num{{}} instead of \\en{{}} - decimals break",
        "pattern": r"\\hebrewversion\{[^}]*\\num\{\d+\}[.,]\d+",
        "severity": Severity.CRITICAL,
        "fix_template": "Use \\en{{1.0}} instead of \\num{{1}}.0 - wrap FULL version",
    },
    # Rule 5c: Version number not fully wrapped
    "cover-version-partial-wrap": {
        "description": "Version number partially wrapped - use \\en{{X.Y}}",
        "pattern": r"\\hebrewversion\{[^}]*(?<!\\en\{)\d+\.\d+",
        "exclude_pattern": r"\\en\{\d+\.\d+\}",
        "severity": Severity.CRITICAL,
        "fix_template": "Wrap FULL version number: גרסה \\en{{1.0}}",
    },
    # Rule 6: Acronym in Hebrew metadata
    "cover-acronym-unwrapped": {
        "description": "Uppercase acronym in Hebrew metadata",
        "pattern": r"\\hebrew(title|subtitle)\{([^}]*[A-Z]{2,}[^}]*)\}",
        "exclude_pattern": r"\\en\{",
        "severity": Severity.WARNING,
        "fix_template": "Wrap acronym with \\en{{{}}}",
    },
    # Rule 7: Date format check
    "cover-date-format": {
        "description": "Date not in DD-MM-YYYY format",
        "pattern": r"\\date\{([^}]*)\}",
        "validate_format": r"\d{2}-\d{2}-\d{4}",
        "severity": Severity.INFO,
        "fix_template": "Use format: DD-MM-YYYY with \\en{{}}",
    },
    # Rule 8: Missing copyright wrapper
    "cover-copyright-bidi": {
        "description": "Copyright line with mixed BiDi content",
        "pattern": r"(כל הזכויות שמורות|All Rights Reserved)",
        "context_pattern": r"©|copyright",
        "severity": Severity.INFO,
        "fix_template": "Use proper BiDi wrappers for copyright",
    },
}
