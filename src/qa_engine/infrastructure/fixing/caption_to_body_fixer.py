"""
Caption to body text fixer for LaTeX documents.

Fixes long captions by:
1. Keeping only short title in caption
2. Moving description to body text after figure
3. Adding figure reference

Uses pure regex - minimal LLM consumption.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue


@dataclass
class CaptionToBodyFix:
    """Represents a caption-to-body fix."""
    file: str
    line: int
    short_title: str
    description: str
    label: str


@dataclass
class CaptionToBodyResult:
    """Result of caption-to-body fixing."""
    fixes_applied: int = 0
    changes: List[CaptionToBodyFix] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied > 0 else "NO_CHANGES"


class CaptionToBodyFixer(FixerInterface):
    """
    Fixes long captions by moving descriptions to body text.

    Strategy (minimal LLM - pure regex):
    1. Extract short title (before ':' or first sentence)
    2. Keep only short title in caption
    3. Insert description after figure with reference
    """

    MAX_SHORT_TITLE = 60

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes based on issues."""
        if not issues:
            return content

        # Sort by line descending (fix from bottom up)
        sorted_issues = sorted(issues, key=lambda i: i.line, reverse=True)

        for issue in sorted_issues:
            if issue.rule not in (
                "caption-too-long",
                "figure-caption-too-long",
                "caption-multi-sentence",
            ):
                continue

            caption_text = issue.context.get("caption_text", "")
            if not caption_text or len(caption_text) < 100:
                continue

            content = self._fix_figure_caption(content, issue.line, caption_text)

        return content

    def fix_content(
        self, content: str, file_path: str = ""
    ) -> Tuple[str, CaptionToBodyResult]:
        """Fix all long captions in content (auto-detect mode)."""
        result = CaptionToBodyResult()

        # Find all figure environments with long captions
        figure_pattern = re.compile(
            r"(\\begin\{figure\}.*?)(\\caption\{)(.*?)(\})\s*"
            r"(\\label\{([^}]+)\})?\s*(\\end\{figure\})",
            re.DOTALL
        )

        def replace_figure(match: re.Match) -> str:
            prefix = match.group(1)
            caption_cmd = match.group(2)
            caption_text = match.group(3)
            label_full = match.group(5) or ""
            label_name = match.group(6) or ""
            suffix = match.group(7)

            # Skip short captions
            if len(caption_text) < 100:
                return match.group(0)

            # Extract short title and description
            short_title, description = self._split_caption(caption_text)

            if not description:
                return match.group(0)

            # Build reference text
            if label_name:
                ref_text = f"כפי שמוצג בתמונה~\\ref{{{label_name}}}"
            else:
                ref_text = ""

            # Build new figure
            new_caption = f"{caption_cmd}{short_title}}}"
            new_figure = f"{prefix}{new_caption}\n{label_full}\n{suffix}"

            # Add description after figure
            if ref_text:
                body_text = f"\n\n{description} ({ref_text}).\n"
            else:
                body_text = f"\n\n{description}\n"

            result.fixes_applied += 1
            result.changes.append(CaptionToBodyFix(
                file=file_path,
                line=content[:match.start()].count("\n") + 1,
                short_title=short_title[:50],
                description=description[:50] + "...",
                label=label_name,
            ))

            return new_figure + body_text

        content = figure_pattern.sub(replace_figure, content)
        return content, result

    def _split_caption(self, caption_text: str) -> Tuple[str, str]:
        """Split caption into short title and description."""
        # Strategy 1: Split at first period followed by space
        period_match = re.search(r"^([^.]+\.)\s+(.+)$", caption_text, re.DOTALL)
        if period_match:
            title = period_match.group(1).strip()
            desc = period_match.group(2).strip()
            if len(title) <= self.MAX_SHORT_TITLE:
                return title.rstrip("."), desc

        # Strategy 2: Split at colon
        if ":" in caption_text:
            colon_idx = caption_text.index(":")
            title = caption_text[:colon_idx].strip()
            desc = caption_text[colon_idx + 1:].strip()
            if len(title) <= self.MAX_SHORT_TITLE:
                return title, desc

        # Strategy 3: Truncate at word boundary
        if len(caption_text) > self.MAX_SHORT_TITLE:
            truncated = caption_text[:self.MAX_SHORT_TITLE]
            last_space = truncated.rfind(" ")
            if last_space > 30:
                title = truncated[:last_space].strip()
                desc = caption_text[last_space:].strip()
                return title, desc

        return caption_text, ""

    def _fix_figure_caption(
        self, content: str, line_num: int, caption_text: str
    ) -> str:
        """Fix a specific figure caption by line number."""
        lines = content.split("\n")
        if line_num - 1 >= len(lines):
            return content

        # Find the figure environment containing this caption
        caption_line_idx = line_num - 1

        # Find start of figure
        start_idx = caption_line_idx
        while start_idx > 0 and "\\begin{figure}" not in lines[start_idx]:
            start_idx -= 1

        # Find end of figure
        end_idx = caption_line_idx
        while end_idx < len(lines) and "\\end{figure}" not in lines[end_idx]:
            end_idx += 1

        if "\\begin{figure}" not in lines[start_idx]:
            return content

        # Extract figure block
        figure_block = "\n".join(lines[start_idx:end_idx + 1])

        # Get label if present
        label_match = re.search(r"\\label\{([^}]+)\}", figure_block)
        label_name = label_match.group(1) if label_match else ""

        # Split caption
        short_title, description = self._split_caption(caption_text)

        if not description:
            return content

        # Replace caption in figure block
        escaped = re.escape(caption_text)
        new_figure_block = re.sub(
            rf"\\caption\{{{escaped}\}}",
            f"\\\\caption{{{short_title}}}",
            figure_block
        )

        # Build body text with reference
        if label_name:
            body_text = f"\n{description} (כפי שמוצג בתמונה~\\ref{{{label_name}}})."
        else:
            body_text = f"\n{description}"

        # Replace in content
        new_lines = lines[:start_idx]
        new_lines.append(new_figure_block)
        new_lines.append(body_text)
        new_lines.extend(lines[end_idx + 1:])

        return "\n".join(new_lines)

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return pattern descriptions."""
        return {
            "caption-to-body": {
                "description": "Move long caption description to body text",
                "strategy": "Extract short title, move description after figure",
            },
        }

    def to_dict(self, result: CaptionToBodyResult) -> Dict:
        """Convert result to output format."""
        return {
            "skill": "qa-img-caption-to-body",
            "status": result.status,
            "fixes_applied": result.fixes_applied,
            "changes": [
                {
                    "file": c.file,
                    "line": c.line,
                    "short_title": c.short_title,
                    "description": c.description,
                    "label": c.label,
                }
                for c in result.changes
            ],
        }
