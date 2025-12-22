"""
Caption fix patterns definitions.

Patterns for fixing caption alignment issues in Hebrew RTL LaTeX documents.
All patterns are deterministic regex operations.
"""

CAPTION_PATTERNS = {
    # Pattern 1: Fix captionsetup justification from raggedleft to centering
    "fix-captionsetup-raggedleft": {
        "description": "Change captionsetup justification from raggedleft to centering",
        "find": r"(\\captionsetup\{[^}]*)justification=raggedleft([^}]*\})",
        "replace": r"\1justification=centering\2",
        "applies_to": ["caption-setup-raggedleft"],
    },
    # Pattern 2: Fix standalone captionsetup with only justification
    "fix-captionsetup-simple": {
        "description": "Fix simple captionsetup{justification=raggedleft}",
        "find": r"\\captionsetup\{justification=raggedleft\}",
        "replace": r"\\captionsetup{justification=centering}",
        "applies_to": ["caption-setup-raggedleft"],
    },
    # Pattern 3: Remove flushleft wrapper around caption
    "fix-flushleft-caption": {
        "description": "Remove flushleft wrapper, use centering instead",
        "find": r"\\begin\{flushleft\}\s*(\\caption\{[^}]*\})\s*\\end\{flushleft\}",
        "replace": r"\\centering\n\1",
        "applies_to": ["caption-flushleft-wrapped"],
    },
    # Pattern 4: Fix table-specific caption override
    "fix-table-captionsetup": {
        "description": "Fix table-specific captionsetup justification",
        "find": r"(\\captionsetup\[table\]\{[^}]*)justification=raggedleft([^}]*\})",
        "replace": r"\1justification=centering\2",
        "applies_to": ["caption-table-raggedleft"],
    },
    # Pattern 5: Add centering before caption if missing alignment
    "add-centering-caption": {
        "description": "Add centering before caption without alignment",
        "find": r"(\\begin\{table\}[^\\]*)(\\caption\{)",
        "replace": r"\1\\centering\n\2",
        "applies_to": ["caption-no-alignment"],
        "condition": "no_centering_before",
    },
}
