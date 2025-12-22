"""
Hebrew chapter counter fixer.

Fixes subfiles that set chapter counter but not hebrewchapter counter.
This causes wrong section numbering in TOC (e.g., "12" instead of "4.11").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class HebrewChapterFix:
    """Single fix record."""
    file: str = ""
    line: int = 0
    chapter_value: int = 0
    hebrewchapter_value: int = 0


@dataclass
class HebrewChapterResult:
    """Result of hebrew chapter fixing."""
    fixes_applied: int = 0
    changes: List[HebrewChapterFix] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied > 0 else "NO_CHANGES"


class HebrewChapterFixer:
    """
    Fixes missing hebrewchapter counter in subfiles.

    When a subfile has \\setcounter{chapter}{N} but not \\setcounter{hebrewchapter}{M},
    the section numbering will be wrong (shows just section number, not chapter.section).

    This fixer adds \\setcounter{hebrewchapter}{N+1} after \\setcounter{chapter}{N}.
    """

    CHAPTER_PATTERN = r"(\\setcounter\{chapter\}\{(\d+)\})"
    HEBREWCHAPTER_PATTERN = r"\\setcounter\{hebrewchapter\}"

    def fix_content(self, content: str, file_path: str = "") -> tuple[str, HebrewChapterResult]:
        """Fix content by adding hebrewchapter counter."""
        result = HebrewChapterResult()

        # Check if hebrewchapter is already set
        if re.search(self.HEBREWCHAPTER_PATTERN, content):
            return content, result

        lines = content.split("\n")
        fixed_lines = []

        for line_num, line in enumerate(lines, start=1):
            fixed_lines.append(line)

            # Find \setcounter{chapter}{N}
            match = re.search(self.CHAPTER_PATTERN, line)
            if match:
                chapter_value = int(match.group(2))
                hebrewchapter_value = chapter_value + 1  # chapter is set to N-1, actual chapter is N

                # Add hebrewchapter counter on next line
                indent = len(line) - len(line.lstrip())
                hebrewchapter_line = " " * indent + f"\\setcounter{{hebrewchapter}}{{{hebrewchapter_value}}}"
                fixed_lines.append(hebrewchapter_line)

                result.changes.append(HebrewChapterFix(
                    file=file_path,
                    line=line_num,
                    chapter_value=chapter_value,
                    hebrewchapter_value=hebrewchapter_value,
                ))
                result.fixes_applied += 1

        return "\n".join(fixed_lines), result

    def fix_file(self, file_path: Path, dry_run: bool = False) -> HebrewChapterResult:
        """Fix a single file."""
        if not file_path.exists():
            return HebrewChapterResult(errors=[f"File not found: {file_path}"])

        content = file_path.read_text(encoding="utf-8")
        fixed, result = self.fix_content(content, str(file_path))

        if not dry_run and result.fixes_applied > 0:
            file_path.write_text(fixed, encoding="utf-8")

        return result

    def to_dict(self, result: HebrewChapterResult) -> dict:
        """Convert result to dictionary for reporting."""
        return {
            "skill": "qa-BiDi-fix-hebrewchapter",
            "status": result.status,
            "fixes_applied": result.fixes_applied,
            "changes": [
                {
                    "file": c.file,
                    "line": c.line,
                    "chapter_value": c.chapter_value,
                    "hebrewchapter_value": c.hebrewchapter_value,
                }
                for c in result.changes
            ],
            "errors": result.errors,
        }
