"""
Naked English fixer for TOC entries.

Fixes English text that renders RTL by wrapping in LTR commands.
Modifies source .tex files, not .toc files.

Version: 1.0.0
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class FixResult:
    """Result of a fix operation."""

    status: str  # "fixed", "skipped", "error"
    source_file: str
    line: int
    original: str
    fixed: str
    message: str = ""
    backup: str = ""


@dataclass
class FixerConfig:
    """Configuration for the fixer."""

    wrapper_command: str = "\\textenglish"
    create_backup: bool = True
    backup_extension: str = ".bak"
    dry_run: bool = False
    min_word_length: int = 3
    always_wrap_acronyms: bool = True


class NakedEnglishFixer:
    """Fixes naked English text in LaTeX source files."""

    # LaTeX commands to skip (not real English words)
    LATEX_COMMANDS = {
        "textenglish", "texthebrew", "textbf", "textit", "texttt",
        "chapter", "section", "subsection", "subsubsection",
        "numberline", "contentsline", "addcontentsline",
        "hskip", "hfill", "quad", "qquad", "nobreak",
        "penalty", "leaders", "hbox", "vbox", "mbox",
        "pardir", "textdir", "bfseries", "relax",
        "phantomsection", "label", "ref", "pageref",
        "begin", "end", "item", "caption", "centering",
    }

    # Section commands to process
    SECTION_COMMANDS = [
        r"\\chapter\s*\{",
        r"\\section\s*\{",
        r"\\subsection\s*\{",
        r"\\subsubsection\s*\{",
        r"\\hebrewchapter\s*\{",
        r"\\hebrewsection\s*\{",
        r"\\hebrewsubsection\s*\{",
    ]

    # LTR wrapper patterns (already wrapped = skip)
    LTR_WRAPPERS = [
        r"\\textenglish\s*\{",
        r"\\LR\s*\{",
        r"\\textLR\s*\{",
        r"\\en\s*\{",
        r"\\begin\s*\{english\}",
    ]

    def __init__(self, config: Optional[FixerConfig] = None) -> None:
        """Initialize fixer with config."""
        self.config = config or FixerConfig()
        self._combined_section_pattern = "|".join(self.SECTION_COMMANDS)

    def fix_file(self, file_path: str) -> List[FixResult]:
        """
        Fix all naked English in a source file.

        Returns list of fix results.
        """
        path = Path(file_path)
        if not path.exists():
            return [FixResult(
                status="error",
                source_file=file_path,
                line=0,
                original="",
                fixed="",
                message=f"File not found: {file_path}"
            )]

        content = path.read_text(encoding="utf-8", errors="replace")
        results = []

        # Find all section commands
        lines = content.split("\n")
        modified_lines = []
        has_changes = False

        for line_num, line in enumerate(lines, start=1):
            fixed_line, fix_result = self._fix_line(line, line_num, file_path)

            if fix_result:
                results.append(fix_result)
                if fix_result.status == "fixed":
                    has_changes = True

            modified_lines.append(fixed_line)

        # Write changes if not dry run
        if has_changes and not self.config.dry_run:
            if self.config.create_backup:
                backup_path = str(path) + self.config.backup_extension
                shutil.copy2(path, backup_path)
                for r in results:
                    r.backup = backup_path

            path.write_text("\n".join(modified_lines), encoding="utf-8")

        return results

    def _fix_line(
        self, line: str, line_num: int, file_path: str
    ) -> Tuple[str, Optional[FixResult]]:
        """Fix naked English in a single line."""
        # Check if line contains a section command
        if not re.search(self._combined_section_pattern, line):
            return line, None

        # Extract the title content
        title_match = re.search(
            r"(\\(?:sub)*section|\\chapter|\\hebrewchapter|\\hebrewsection"
            r"|\\hebrewsubsection)\s*\{(.+)\}",
            line
        )

        if not title_match:
            return line, None

        command = title_match.group(1)
        title = title_match.group(2)

        # Find naked English words
        naked_words = self._find_naked_english(line, title)

        if not naked_words:
            return line, None

        # Apply fix
        fixed_title = self._wrap_naked_english(title, naked_words)

        if fixed_title == title:
            return line, FixResult(
                status="skipped",
                source_file=file_path,
                line=line_num,
                original=title,
                fixed=title,
                message="No changes needed"
            )

        # Replace in line
        fixed_line = line.replace(
            f"{command}{{{title}}}",
            f"{command}{{{fixed_title}}}"
        )

        return fixed_line, FixResult(
            status="fixed",
            source_file=file_path,
            line=line_num,
            original=f"{command}{{{title}}}",
            fixed=f"{command}{{{fixed_title}}}",
            message=f"Wrapped: {naked_words}"
        )

    def _find_naked_english(
        self, raw_line: str, title: str
    ) -> List[str]:
        """Find English words not wrapped in LTR commands."""
        naked = []

        # Find all English words (3+ chars)
        for match in re.finditer(r'[A-Za-z]{3,}', title):
            word = match.group(0)

            # Skip LaTeX commands
            if word.lower() in self.LATEX_COMMANDS:
                continue

            # Skip if already wrapped
            if self._is_wrapped(raw_line, word):
                continue

            naked.append(word)

        # Also find short acronyms (2-3 uppercase)
        if self.config.always_wrap_acronyms:
            for match in re.finditer(r'\b[A-Z]{2,5}\b', title):
                word = match.group(0)
                if word not in naked and not self._is_wrapped(raw_line, word):
                    naked.append(word)

        return naked

    def _is_wrapped(self, content: str, word: str) -> bool:
        """Check if word is inside an LTR wrapper."""
        for pattern in self.LTR_WRAPPERS:
            # Match wrapper containing the word
            wrapper_regex = pattern + r'[^}]*' + re.escape(word) + r'[^}]*\}'
            if re.search(wrapper_regex, content, re.IGNORECASE):
                return True
        return False

    def _wrap_naked_english(
        self, title: str, naked_words: List[str]
    ) -> str:
        """Wrap naked English words in textenglish."""
        result = title

        # Group adjacent words into phrases
        phrases = self._group_adjacent_words(title, naked_words)

        # Sort by position (reverse) to avoid offset issues
        phrases_with_pos = []
        for phrase in phrases:
            match = re.search(re.escape(phrase), result)
            if match:
                phrases_with_pos.append((match.start(), phrase))

        phrases_with_pos.sort(reverse=True)

        # Apply wrapping from end to start
        for _, phrase in phrases_with_pos:
            if not self._is_wrapped(result, phrase):
                wrapper = self.config.wrapper_command
                result = result.replace(phrase, f"{wrapper}{{{phrase}}}", 1)

        return result

    def _group_adjacent_words(
        self, title: str, words: List[str]
    ) -> List[str]:
        """Group adjacent English words into phrases."""
        if not words:
            return []

        # Find positions of all words
        word_positions = []
        for word in words:
            for match in re.finditer(re.escape(word), title):
                word_positions.append((match.start(), match.end(), word))

        if not word_positions:
            return words

        # Sort by position
        word_positions.sort()

        # Group adjacent words (separated only by spaces)
        phrases = []
        current_phrase = []
        last_end = -1

        for start, end, word in word_positions:
            if last_end == -1:
                current_phrase = [word]
            elif start - last_end <= 1:  # Adjacent or 1 space
                # Check if separator is space only
                sep = title[last_end:start]
                if sep.strip() == "" or sep == " ":
                    current_phrase.append(word)
                else:
                    # Not adjacent, save current and start new
                    if current_phrase:
                        phrases.append(" ".join(current_phrase))
                    current_phrase = [word]
            else:
                if current_phrase:
                    phrases.append(" ".join(current_phrase))
                current_phrase = [word]

            last_end = end

        if current_phrase:
            phrases.append(" ".join(current_phrase))

        return phrases

    def fix_from_detection(
        self,
        issues: List[Dict[str, Any]],
        project_root: str
    ) -> List[FixResult]:
        """
        Fix issues from detection output.

        Finds source files and applies fixes.
        """
        results = []

        for issue in issues:
            if issue.get("rule") != "toc-english-text-naked":
                continue

            # Find source file
            source_file = self._find_source_file(issue, project_root)
            if not source_file:
                results.append(FixResult(
                    status="error",
                    source_file="unknown",
                    line=issue.get("line", 0),
                    original=issue.get("content", ""),
                    fixed="",
                    message="Could not find source file"
                ))
                continue

            # Fix the file
            file_results = self.fix_file(source_file)
            results.extend(file_results)

        return results

    def _find_source_file(
        self, issue: Dict[str, Any], project_root: str
    ) -> Optional[str]:
        """Find source .tex file containing the section."""
        root = Path(project_root)
        content = issue.get("content", "")

        if not content:
            return None

        # Search in chapters/, standalone-*/, and root
        search_dirs = [
            root / "chapters",
            root / "standalone-chapter01",
            root / "standalone-chapter02",
            root / "standalone-chapter03",
            root,
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for tex_file in search_dir.glob("*.tex"):
                try:
                    file_content = tex_file.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    if content in file_content:
                        return str(tex_file)
                except Exception:
                    continue

        return None

    def generate_report(self, results: List[FixResult]) -> Dict[str, Any]:
        """Generate a summary report of fixes."""
        fixed = [r for r in results if r.status == "fixed"]
        skipped = [r for r in results if r.status == "skipped"]
        errors = [r for r in results if r.status == "error"]

        return {
            "summary": {
                "total": len(results),
                "fixed": len(fixed),
                "skipped": len(skipped),
                "errors": len(errors),
            },
            "fixed": [
                {
                    "file": r.source_file,
                    "line": r.line,
                    "original": r.original,
                    "fixed": r.fixed,
                }
                for r in fixed
            ],
            "errors": [
                {
                    "file": r.source_file,
                    "message": r.message,
                }
                for r in errors
            ],
        }
