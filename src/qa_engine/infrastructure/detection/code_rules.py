"""Code block detection rules."""

from ...domain.models.issue import Severity

CODE_RULES = {
    "code-background-overflow": {
        "description": "Code block without english wrapper causing overflow",
        "pattern": r"\\begin\{(pythonbox\*?|tcolorbox|tcblisting)\}",
        "severity": Severity.WARNING,
    },
    "code-encoding-emoji": {
        "description": "Emoji characters in code that may cause font issues",
        "pattern": r"[\U0001F300-\U0001F9FF]",
        "severity": Severity.INFO,
    },
    "code-direction-hebrew": {
        "description": "Hebrew text in code without proper wrapper",
        "pattern": r"[א-ת]",
        "severity": Severity.WARNING,
        "in_code_block": True,
    },
    "code-hebrew-content": {
        "description": "Hebrew text in code comments/strings needs translation",
        "pattern": r'(#.*[א-ת]|"""[^"]*[א-ת][^"]*"""|\'\'\'[^\']*[א-ת][^\']*\'\'\'|"[^"]*[א-ת][^"]*"|\'[^\']*[א-ת][^\']*\')',
        "severity": Severity.WARNING,
        "in_code_block": True,
    },
    "code-fstring-brace": {
        "description": "F-string with problematic braces outside code block",
        "pattern": r'f["\'][^"\']*\{[^}]*\}[^"\']*["\']',
        "severity": Severity.INFO,
        "outside_code_block": True,
    },
}

CODE_ENV_PATTERN = r"(lstlisting|minted|verbatim|pythonbox\*?|tcolorbox|tcblisting)"
HEBREW_WRAPPERS = ["texthebrew{", "hebtitle{", "he{", "hebtext{"]

FIX_SUGGESTIONS = {
    "code-background-overflow": r"Wrap in \begin{english}...\end{english}",
    "code-encoding-emoji": "Remove emoji or use appropriate font setup",
    "code-direction-hebrew": r"Use \texthebrew{} for Hebrew text",
    "code-hebrew-content": "Translate Hebrew comments/strings to English",
    "code-fstring-brace": "Escape braces with {{ and }}",
}
