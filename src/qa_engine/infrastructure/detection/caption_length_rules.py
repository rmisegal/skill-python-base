"""
Caption length detection rules definitions.

Detects figure/table captions that are too long (descriptions instead of titles).
Long captions create verbose List of Figures/Tables.

NOTE: Rules use 'brace_balanced' flag to handle nested LaTeX commands like
\\en{...}, \\num{...}, etc. Standard [^}] patterns break on nested braces.
"""

from ...domain.models.issue import Severity

# Maximum caption length before it's considered a description
MAX_SHORT_TITLE_LENGTH = 60  # Characters for LOF entry
MAX_CAPTION_LENGTH = 100  # Characters before requiring short title

# Pattern for balanced braces (up to 2 levels deep)
# Matches: text, or {text}, or {text {nested} text}
BRACE_BALANCED_PATTERN = r"(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*"

CAPTION_LENGTH_RULES = {
    # Rule 1: Caption without short title that exceeds max length
    # Uses brace_balanced flag to handle nested commands like \en{...}
    "caption-too-long": {
        "description": "Caption exceeds max length without short title for LOF",
        "pattern": r"\\caption\{(" + BRACE_BALANCED_PATTERN + r")\}",
        "negative_pattern": r"\\caption\[[^\]]+\]\{",
        "severity": Severity.WARNING,
        "fix_template": "Add short title: \\caption[short title]{full caption}",
        "max_length": MAX_CAPTION_LENGTH,
        "brace_balanced": True,  # Flag for length-based validation
    },
    # Rule 2: Caption with colon indicating description pattern
    # Colon pattern still works - checks structure before nesting
    "caption-description-pattern": {
        "description": "Caption uses description pattern (title: explanation)",
        "pattern": r"\\caption\{([^:{]{10,60}):\s*" + BRACE_BALANCED_PATTERN + r"\}",
        "negative_pattern": r"\\caption\[[^\]]+\]\{",
        "severity": Severity.WARNING,
        "fix_template": "Extract title before colon for LOF short title",
    },
    # Rule 3: Caption with sentence structure (periods followed by more text)
    "caption-multi-sentence": {
        "description": "Caption contains multiple sentences",
        "pattern": r"\\caption\{" + BRACE_BALANCED_PATTERN + r"\.\s+" + BRACE_BALANCED_PATTERN + r"\}",
        "negative_pattern": r"\\caption\[[^\]]+\]\{",
        "severity": Severity.INFO,
        "fix_template": "Use first sentence as short title for LOF",
    },
    # Rule 4: Figure caption specifically (more strict)
    "figure-caption-too-long": {
        "description": "Figure caption too long for clean List of Figures",
        "pattern": r"\\begin\{figure\}.*?\\caption\{(" + BRACE_BALANCED_PATTERN + r")\}",
        "negative_pattern": r"\\caption\[[^\]]+\]\{",
        "context_required": "figure",
        "severity": Severity.WARNING,
        "fix_template": "Add short title for List of Figures entry",
        "multiline": True,
        "brace_balanced": True,
    },
}
