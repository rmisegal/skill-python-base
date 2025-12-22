"""
Direction fix patterns for Hebrew text in code blocks.

Deterministic patterns for fixing Hebrew text direction in code environments.
All patterns are 100% automatable - no LLM required.
"""

from dataclasses import dataclass, field
from typing import List

# Hebrew character range (including final forms)
HEBREW_RANGE = r"[\u0590-\u05FF]"
HEBREW_PATTERN = r"[\u0590-\u05FF]+"

# Code environments that need direction fixes
CODE_ENVIRONMENTS = [
    "lstlisting",
    "minted",
    "verbatim",
    "pythonbox",
    "pythonbox*",
    "tcolorbox",
    "tcblisting",
]


@dataclass
class DirectionFix:
    """Represents a single direction fix applied."""
    file: str
    line: int
    original: str
    replacement: str
    pattern_id: str


@dataclass
class DirectionFixResult:
    """Result of direction fixing operation."""
    fixes_applied: int = 0
    fixes: List[DirectionFix] = field(default_factory=list)


DIRECTION_PATTERNS = {
    # Pattern 1: Hebrew text in code - wrap with texthebrew
    "hebrew-in-code": {
        "description": "Wrap Hebrew text in code with \\texthebrew{}",
        "find": HEBREW_PATTERN,
        "replace_template": r"\\texthebrew{{{text}}}",
        "applies_to": CODE_ENVIRONMENTS,
        "context": "code",
    },
    # Pattern 2: Hebrew comment - wrap entire comment
    "hebrew-comment-python": {
        "description": "Wrap Hebrew in Python comment",
        "find": r"(#\s*)(" + HEBREW_PATTERN + r")",
        "replace_template": r"\1\\texthebrew{{\2}}",
        "applies_to": ["pythonbox", "pythonbox*", "minted"],
        "context": "comment",
    },
    # Pattern 3: Hebrew string literal
    "hebrew-string": {
        "description": "Wrap Hebrew in string literal",
        "find": r'(["\'])(' + HEBREW_PATTERN + r')(["\'])',
        "replace_template": r'\1\\texthebrew{{\2}}\3',
        "applies_to": CODE_ENVIRONMENTS,
        "context": "string",
    },
}

# Wrapper command options
WRAPPER_COMMANDS = {
    "texthebrew": r"\texthebrew{%s}",
    "he": r"\he{%s}",
    "heb": r"\heb{%s}",
}

DEFAULT_WRAPPER = "texthebrew"
