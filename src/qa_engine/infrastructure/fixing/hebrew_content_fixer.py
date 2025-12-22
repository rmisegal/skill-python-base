"""
Hebrew content fixer for code blocks.

Translates Hebrew comments and strings in code to English.
This fixer requires LLM for semantic translation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Callable


@dataclass
class HebrewContentFix:
    """Single Hebrew content fix record."""
    file: str = ""
    line: int = 0
    original: str = ""
    translated: str = ""
    context: str = ""  # comment, docstring, string


@dataclass
class HebrewContentResult:
    """Result of Hebrew content fixing."""
    fixes_applied: int = 0
    changes: List[HebrewContentFix] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied > 0 else "NO_CHANGES"


# Common Hebrew-to-English translations for code
COMMON_TRANSLATIONS = {
    # Comments
    "שימוש": "Usage",
    "הערה": "Note",
    "דוגמה": "Example",
    "פלט": "Output",
    "קלט": "Input",
    "החזרה": "Returns",
    "פרמטרים": "Parameters",
    "ארגומנטים": "Arguments",
    "תיאור": "Description",
    "הגדרה": "Definition",
    "יצירת": "Creating",
    "חישוב": "Calculation",
    "בדיקה": "Testing",
    "בדיקת": "Testing",
    "סריקה": "Scan",
    "סריקת": "Scanning",
    "אוטומטית": "automatic",
    "אוטומטי": "automatic",
    "מריץ": "Running",
    "בודק": "Checking",
    "דוח": "report",
    "מפורט": "detailed",
    "כולל": "total",
    "ציון": "score",
    "תוצאות": "results",
    "הושלמה": "completed",
    "נשמר": "saved",
    "מקיפה": "comprehensive",
    "המשלבת": "combining",
    "כלים": "tools",
    "מרובים": "multiple",
    "הגדרת": "configuration",
    "המודל": "the model",
    "עם": "with",
}


class HebrewContentFixer:
    """Translates Hebrew content in code blocks to English."""

    CODE_ENVS = r"(pythonbox\*?|lstlisting|minted|verbatim|tcolorbox)"
    HEBREW_PATTERN = r"[א-ת]+"

    def __init__(self, translator: Optional[Callable[[str], str]] = None):
        """
        Initialize fixer.

        Args:
            translator: Optional function for LLM translation.
                       If None, uses basic dictionary translation.
        """
        self._translator = translator or self._basic_translate
        self._hebrew_re = re.compile(self.HEBREW_PATTERN)

    def _basic_translate(self, hebrew_text: str) -> str:
        """Basic translation using common dictionary."""
        result = hebrew_text
        for heb, eng in COMMON_TRANSLATIONS.items():
            result = result.replace(heb, eng)
        # If still has Hebrew, mark as untranslated
        if self._hebrew_re.search(result):
            return f"[TRANSLATE: {hebrew_text}]"
        return result

    def fix_content(self, content: str, file_path: str = "") -> tuple[str, HebrewContentResult]:
        """Fix Hebrew content in code blocks."""
        result = HebrewContentResult()
        lines = content.split("\n")
        fixed_lines = []
        in_code = False

        for line_num, line in enumerate(lines, start=1):
            # Track code environment
            if re.search(rf"\\begin\{{{self.CODE_ENVS}\}}", line):
                in_code = True
            elif re.search(rf"\\end\{{{self.CODE_ENVS}\}}", line):
                in_code = False

            if in_code and self._hebrew_re.search(line):
                fixed_line = self._translate_line(line, line_num, file_path, result)
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines), result

    def _translate_line(self, line: str, line_num: int,
                        file_path: str, result: HebrewContentResult) -> str:
        """Translate Hebrew text in a single line."""
        # Skip LaTeX commands like \hebtitle{}, \en{}, etc.
        if line.strip().startswith("\\"):
            return line

        def replace_hebrew(match: re.Match) -> str:
            hebrew = match.group(0)
            translated = self._translator(hebrew)
            if translated != hebrew:
                result.changes.append(HebrewContentFix(
                    file=file_path,
                    line=line_num,
                    original=hebrew,
                    translated=translated,
                ))
                result.fixes_applied += 1
                return translated
            return hebrew

        return self._hebrew_re.sub(replace_hebrew, line)

    def fix_file(self, file_path: Path, dry_run: bool = False) -> HebrewContentResult:
        """Fix a single file."""
        if not file_path.exists():
            return HebrewContentResult(errors=[f"File not found: {file_path}"])

        content = file_path.read_text(encoding="utf-8")
        fixed, result = self.fix_content(content, str(file_path))

        if not dry_run and result.fixes_applied > 0:
            file_path.write_text(fixed, encoding="utf-8")

        return result

    def to_dict(self, result: HebrewContentResult) -> Dict:
        """Convert result to dictionary for reporting."""
        return {
            "skill": "qa-code-fix-hebrew-content",
            "status": result.status,
            "fixes_applied": result.fixes_applied,
            "changes": [
                {"file": c.file, "line": c.line,
                 "original": c.original, "translated": c.translated}
                for c in result.changes
            ],
            "errors": result.errors,
        }
