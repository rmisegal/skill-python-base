"""Hebrew math detection rules definitions."""
from ...domain.models.issue import Severity

# Hebrew character range for regex
HEBREW_RANGE = r"[\u0590-\u05FF]"

HEB_MATH_RULES = {
    "heb-math-text": {
        "description": "Hebrew in \\text{} without \\hebmath{} wrapper",
        "pattern": r"(?<!\\hebmath\{)\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Replace \\text{{{}}} with \\hebmath{{{}}}",
    },
    "heb-math-textbf": {
        "description": "Hebrew in \\textbf{}/\\textit{} inside math mode",
        "pattern": r"\\text(bf|it)\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Wrap with \\hebmath{{\\textbf{{{}}}}}",
        "math_context": True,
    },
    "heb-math-subscript": {
        "description": "Hebrew in subscript without wrapper",
        "pattern": r"_\{(?!\\hebsub|\\hebmath)([^}]*" + HEBREW_RANGE + r"[^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Use $x_{{\\hebsub{{{}}}}}$",
    },
    "heb-math-superscript": {
        "description": "Hebrew in superscript without wrapper",
        "pattern": r"\^\{(?!\\hebmath)([^}]*" + HEBREW_RANGE + r"[^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Use $y^{{\\hebmath{{{}}}}}$",
    },
    "heb-math-cases": {
        "description": "Hebrew in cases environment without \\hebmath{}",
        "pattern": r"\\text\{([^}]*" + HEBREW_RANGE + r"[^}]*)\}",
        "severity": Severity.WARNING,
        "fix_template": "Replace \\text{{{}}} with \\hebmath{{{}}}",
        "cases_context": True,
    },
    "heb-math-definition": {
        "description": "Incorrect \\hebmath{} definition missing \\textdir TRT",
        "pattern": r"\\newcommand\{\\hebmath\}\[1\]\{[^}]*\}",
        "severity": Severity.CRITICAL,
        "fix_template": "Add \\textdir TRT to \\hebmath definition",
        "negative_pattern": r"textdir\s+TRT",
    },
}
