"""
Caption length fixer for LaTeX documents.

Fixes long captions by adding short titles for List of Figures/Tables.
Uses pure regex - minimal LLM consumption.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue


@dataclass
class CaptionLengthFix:
    """Represents a caption length fix."""
    file: str
    line: int
    old_caption: str
    new_caption: str
    short_title: str
    pattern: str


@dataclass
class CaptionLengthFixResult:
    """Result of caption length fixing."""
    fixes_applied: int = 0
    changes: List[CaptionLengthFix] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied > 0 else "NO_CHANGES"


class CaptionLengthFixer(FixerInterface):
    """
    Fixes long captions by adding short titles for LOF/LOT.

    Strategy (minimal LLM - pure regex):
    1. Extract short title from caption (before ':' or first sentence)
    2. Convert \\caption{long} to \\caption[short]{long}

    Does NOT require LLM for:
    - Extracting short title (uses heuristics)
    - Adding optional argument (pure regex)
    """

    # Maximum length for short title in LOF
    MAX_SHORT_TITLE = 60

    def __init__(self) -> None:
        """Initialize fixer."""
        pass

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        if not issues:
            return content

        # Sort issues by line number descending (fix from bottom up)
        sorted_issues = sorted(issues, key=lambda i: i.line, reverse=True)

        lines = content.split("\n")

        for issue in sorted_issues:
            if issue.rule not in (
                "caption-too-long",
                "caption-description-pattern",
                "caption-multi-sentence",
                "figure-caption-too-long",
            ):
                continue

            # Get caption text from context
            caption_text = issue.context.get("caption_text", "")
            if not caption_text:
                continue

            # Extract short title
            short_title = issue.context.get(
                "suggested_short_title",
                self._extract_short_title(caption_text)
            )

            # Find and fix the caption line
            line_idx = issue.line - 1
            if 0 <= line_idx < len(lines):
                lines[line_idx] = self._fix_caption_line(
                    lines[line_idx], caption_text, short_title
                )

        return "\n".join(lines)

    def fix_content(
        self, content: str, file_path: str = ""
    ) -> Tuple[str, CaptionLengthFixResult]:
        """Fix all long caption issues in content (auto-detect mode)."""
        result = CaptionLengthFixResult()
        lines = content.split("\n")

        # Pattern for caption without optional argument
        caption_pattern = re.compile(
            r"(\\caption)\{([^}]{80,})\}"
        )

        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith("%"):
                continue

            # Skip lines with existing short title
            if re.search(r"\\caption\[[^\]]+\]", line):
                continue

            match = caption_pattern.search(line)
            if match:
                caption_text = match.group(2)
                short_title = self._extract_short_title(caption_text)

                new_line = self._fix_caption_line(line, caption_text, short_title)

                if new_line != line:
                    result.changes.append(CaptionLengthFix(
                        file=file_path,
                        line=i + 1,
                        old_caption=line.strip()[:60] + "...",
                        new_caption=new_line.strip()[:60] + "...",
                        short_title=short_title,
                        pattern="add-short-title",
                    ))
                    lines[i] = new_line
                    result.fixes_applied += 1

        return "\n".join(lines), result

    def _fix_caption_line(
        self, line: str, caption_text: str, short_title: str
    ) -> str:
        """Fix a single caption line by adding short title."""
        # Escape special regex characters in caption_text
        escaped = re.escape(caption_text)

        # Replace \caption{long} with \caption[short]{long}
        pattern = rf"(\\caption)\{{{escaped}\}}"
        replacement = rf"\1[{short_title}]{{{caption_text}}}"

        return re.sub(pattern, replacement, line)

    def _extract_short_title(self, caption_text: str) -> str:
        """Extract short title from caption text using heuristics."""
        # Strategy 1: Split at colon (title: description pattern)
        if ":" in caption_text:
            colon_idx = caption_text.index(":")
            title_part = caption_text[:colon_idx].strip()
            if 10 <= len(title_part) <= self.MAX_SHORT_TITLE:
                return title_part

        # Strategy 2: First sentence
        period_match = re.search(r"^([^.]+\.)", caption_text)
        if period_match:
            first_sentence = period_match.group(1).strip()
            if len(first_sentence) <= self.MAX_SHORT_TITLE:
                return first_sentence.rstrip(".")

        # Strategy 3: Truncate at word boundary
        if len(caption_text) > self.MAX_SHORT_TITLE:
            truncated = caption_text[:self.MAX_SHORT_TITLE]
            last_space = truncated.rfind(" ")
            if last_space > 30:
                return truncated[:last_space].strip()
            return truncated.strip()

        return caption_text.strip()

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {description}."""
        return {
            "add-short-title": {
                "description": "Add short title to caption for LOF/LOT",
                "find": r"\\caption{long text}",
                "replace": r"\\caption[short title]{long text}",
            },
        }

    def to_dict(self, result: CaptionLengthFixResult) -> Dict:
        """Convert result to skill.md output format."""
        return {
            "skill": "qa-img-fix-caption-length",
            "status": result.status,
            "fixes_applied": result.fixes_applied,
            "changes": [
                {
                    "file": c.file,
                    "line": c.line,
                    "short_title": c.short_title,
                    "old": c.old_caption,
                    "new": c.new_caption,
                }
                for c in result.changes
            ],
        }
