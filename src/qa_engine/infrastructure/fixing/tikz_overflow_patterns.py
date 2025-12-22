"""
TikZ overflow fix patterns and models.

Deterministic patterns for fixing TikZ diagrams that overflow text width.
All patterns are 100% automatable - no LLM required.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TikzOverflowFix:
    """Represents a single TikZ overflow fix applied."""
    file: str
    line: int
    pattern_id: str
    description: str


@dataclass
class TikzOverflowFixResult:
    """Result of TikZ overflow fixing operation."""
    fixes_applied: int = 0
    fixes: List[TikzOverflowFix] = field(default_factory=list)


TIKZ_OVERFLOW_PATTERNS = {
    # Pattern 1: Wrap tikzpicture (no options) with resizebox
    "wrap-resizebox": {
        "description": "Wrap tikzpicture in resizebox for text width",
        "find": r"([ \t]*)(\\begin\{tikzpicture\})",
        "replace": r"\1\\resizebox{\\textwidth}{!}{%\n\1\2",
        "end_find": r"([ \t]*)(\\end\{tikzpicture\})",
        "end_replace": r"\1\2%\n\1}",
        "applies_to": ["tikz-no-width-constraint", "tikz-large-coordinates"],
        "preferred": True,
    },
    # Pattern 2: Wrap tikzpicture (with options) with resizebox
    "wrap-resizebox-options": {
        "description": "Wrap tikzpicture with options in resizebox",
        "find": r"([ \t]*)(\\begin\{tikzpicture\}\[[^\]]*\])",
        "replace": r"\1\\resizebox{\\textwidth}{!}{%\n\1\2",
        "end_find": r"([ \t]*)(\\end\{tikzpicture\})",
        "end_replace": r"\1\2%\n\1}",
        "applies_to": ["tikz-no-width-constraint", "tikz-large-coordinates"],
    },
    # Pattern 3: Add scale option to tikzpicture (no existing options)
    "add-scale": {
        "description": "Add scale=0.8 option to tikzpicture",
        "find": r"\\begin\{tikzpicture\}(?!\[)",
        "replace": r"\\begin{tikzpicture}[scale=0.8]",
        "applies_to": ["tikz-no-width-constraint"],
    },
    # Pattern 4: Add scale to existing options
    "add-scale-options": {
        "description": "Add scale=0.8 to existing tikzpicture options",
        "find": r"\\begin\{tikzpicture\}\[([^\]]*)\]",
        "replace": r"\\begin{tikzpicture}[\1, scale=0.8]",
        "condition": "scale not in options",
        "applies_to": ["tikz-no-width-constraint"],
    },
    # Pattern 5: Add xscale for horizontal-only scaling
    "add-xscale": {
        "description": "Add xscale=0.7 for horizontal compression",
        "find": r"\\begin\{tikzpicture\}(?!\[)",
        "replace": r"\\begin{tikzpicture}[xscale=0.7]",
        "applies_to": ["tikz-large-coordinates"],
    },
    # Pattern 6: Wrap with adjustbox
    "wrap-adjustbox": {
        "description": "Wrap tikzpicture in adjustbox environment",
        "find": r"([ \t]*)(\\begin\{tikzpicture\})",
        "replace": r"\1\\begin{adjustbox}{max width=\\textwidth}\n\1\2",
        "end_find": r"([ \t]*)(\\end\{tikzpicture\})",
        "end_replace": r"\1\2\n\1\\end{adjustbox}",
        "requires_package": "adjustbox",
        "applies_to": ["tikz-no-width-constraint", "tikz-large-coordinates"],
    },
    # Pattern 7: Center with makebox (allow controlled overflow)
    "center-makebox": {
        "description": "Center tikzpicture allowing controlled overflow",
        "find": r"([ \t]*)(\\begin\{tikzpicture\})",
        "replace": r"\1\\begin{center}\n\1\\makebox[\\textwidth][c]{%\n\1\2",
        "end_find": r"([ \t]*)(\\end\{tikzpicture\})",
        "end_replace": r"\1\2%\n\1}\n\1\\end{center}",
        "applies_to": ["tikz-large-coordinates"],
        "note": "Use for intentional full-bleed diagrams",
    },
}

# Default fix strategy based on issue type
FIX_STRATEGY = {
    "large_coordinates": ["wrap-resizebox", "add-xscale"],
    "no_width_constraint": ["add-scale", "wrap-resizebox"],
}
