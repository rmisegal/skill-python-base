"""
Hebrew math fixer for LaTeX documents.

Fixes Hebrew text in math mode by wrapping with \hebmath{} for RTL rendering.
Aligned with qa-heb-math-fix skill.md patterns.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue

# Hebrew character range
HEBREW_RANGE = r"[\u0590-\u05FF]"

# Fix patterns aligned with qa-heb-math-fix skill.md
# Note: Uses negative lookahead to avoid double-fixing already wrapped content
FIX_PATTERNS = {
    "text-to-hebmath": {
        "find": r"(?<!\\hebmath)\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}",
        "replace": r"\\hebmath{\1}",
        "description": "Hebrew in \\text{} to \\hebmath{}",
    },
    "textbf-to-hebmath": {
        "find": r"\\text(bf|it)\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}",
        "replace": r"\\hebmath{\\text\1{\2}}",
        "description": "Hebrew in \\textbf/\\textit{} to \\hebmath{}",
    },
    "subscript-to-hebsub": {
        "find": r"_\{(?!\\hebsub)(" + HEBREW_RANGE + r"[^}]*)\}",
        "replace": r"_{\\hebsub{\1}}",
        "description": "Hebrew subscript to \\hebsub{}",
    },
    "superscript-to-hebmath": {
        "find": r"\^\{(?!\\hebmath)(" + HEBREW_RANGE + r"[^}]*)\}",
        "replace": r"^{\\hebmath{\1}}",
        "description": "Hebrew superscript to \\hebmath{}",
    },
    "text-subscript-to-hebsub": {
        "find": r"_\{\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}\}",
        "replace": r"_{\\hebsub{\1}}",
        "description": "\\text{} subscript to \\hebsub{}",
    },
    "text-superscript-to-hebmath": {
        "find": r"\^\{\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}\}",
        "replace": r"^{\\hebmath{\1}}",
        "description": "\\text{} superscript to \\hebmath{}",
    },
    "hebmath-definition": {
        "find": r"\\newcommand\{\\hebmath\}\[1\]\{\\texthebrew\{#1\}\}",
        "replace": "",  # Remove duplicate - CLS provides this
        "description": "Remove duplicate \\hebmath{} definition (CLS provides it)",
    },
    "hebmath-definition-alt": {
        "find": r"\\newcommand\{\\hebmath\}\[1\]\{\\text\{\\texthebrew\{#1\}\}\}",
        "replace": "",  # Remove duplicate
        "description": "Remove duplicate \\hebmath{} definition variant",
    },
}


class HebMathFixer(FixerInterface):
    """Fixes Hebrew text in math mode for RTL rendering."""

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes based on detected issues."""
        fixed, _ = self.fix_content(content)
        return fixed

    def fix_content(self, content: str) -> Tuple[str, List[Dict]]:
        """Fix all Hebrew-in-math issues in content."""
        changes: List[Dict] = []
        result = content

        for name, pattern in FIX_PATTERNS.items():
            regex = re.compile(pattern["find"])
            matches = list(regex.finditer(result))

            if matches:
                for match in matches:
                    changes.append({
                        "pattern": name,
                        "original": match.group(0),
                        "line": result[:match.start()].count("\n") + 1,
                    })
                result = regex.sub(pattern["replace"], result)

        return result, changes

    def fix_line(self, line: str, rule: str) -> str:
        """Fix a single line based on rule type."""
        if rule in ("heb-math-text", "heb-math-cases"):
            return self._fix_text_to_hebmath(line)
        elif rule == "heb-math-subscript":
            return self._fix_subscript(line)
        elif rule == "heb-math-superscript":
            return self._fix_superscript(line)
        elif rule == "heb-math-definition":
            return self._fix_definition(line)
        return line

    def _fix_text_to_hebmath(self, line: str) -> str:
        """Replace \\text{Hebrew} with \\hebmath{Hebrew}."""
        pattern = re.compile(r"\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}")
        return pattern.sub(r"\\hebmath{\1}", line)

    def _fix_subscript(self, line: str) -> str:
        """Fix Hebrew subscripts."""
        # First handle _{\text{}}
        p1 = re.compile(r"_\{\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}\}")
        line = p1.sub(r"_{\\hebsub{\1}}", line)
        # Then handle raw _{Hebrew}
        p2 = re.compile(r"_\{(" + HEBREW_RANGE + r"[^}]*)\}")
        if not re.search(r"_\{\\hebsub", line):
            line = p2.sub(r"_{\\hebsub{\1}}", line)
        return line

    def _fix_superscript(self, line: str) -> str:
        """Fix Hebrew superscripts."""
        # First handle ^{\text{}}
        p1 = re.compile(r"\^\{\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}\}")
        line = p1.sub(r"^{\\hebmath{\1}}", line)
        # Then handle raw ^{Hebrew}
        p2 = re.compile(r"\^\{(" + HEBREW_RANGE + r"[^}]*)\}")
        if not re.search(r"\^\{\\hebmath", line):
            line = p2.sub(r"^{\\hebmath{\1}}", line)
        return line

    def _fix_definition(self, line: str) -> str:
        """Fix incorrect \\hebmath definition."""
        pattern = FIX_PATTERNS["hebmath-definition"]
        return re.sub(pattern["find"], pattern["replace"], line)

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return all fix patterns."""
        return FIX_PATTERNS
