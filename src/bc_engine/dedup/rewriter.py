r"""
Rewriter module for chapterref integration.

Handles rewriting duplicate content to use \chapterref{} references.
"""

from __future__ import annotations

import re
from typing import Callable, List, Optional

from .config import DedupConfig
from .models import ComparisonResult, DedupIssue


class ChapterRefRewriter:
    """
    Rewrites duplicate content with chapterref references.

    Uses LLM for natural language rewriting when available,
    falls back to simple replacement patterns.
    """

    def __init__(
        self,
        config: Optional[DedupConfig] = None,
        llm_callback: Optional[Callable[[str], str]] = None,
    ) -> None:
        """
        Initialize rewriter.

        Args:
            config: Dedup configuration
            llm_callback: Function to call LLM for rewriting
        """
        self._config = config or DedupConfig()
        self._llm_callback = llm_callback

    def _build_rewrite_prompt(
        self,
        original: str,
        source_chapter: int,
        source_summary: str,
    ) -> str:
        """Build LLM prompt for rewriting."""
        template = self._config.rewrite_prompt_template
        return template.format(
            original_text=original,
            source_chapter=source_chapter,
            source_summary=source_summary[:300],
        )

    def _simple_rewrite(self, issue: DedupIssue) -> str:
        """Simple rewrite without LLM."""
        ref = f"\\chapterref{{chapter{issue.source_chapter}}}"
        return f"כפי שהוסבר ב{ref}, "

    def rewrite_with_reference(
        self,
        original_text: str,
        source_chapter: int,
        source_summary: str = "",
    ) -> str:
        """
        Rewrite text to use chapterref.

        Args:
            original_text: The duplicate text to rewrite
            source_chapter: Chapter number to reference
            source_summary: Summary of original content

        Returns:
            Rewritten text with chapterref
        """
        if self._llm_callback:
            prompt = self._build_rewrite_prompt(
                original_text,
                source_chapter,
                source_summary,
            )
            return self._llm_callback(prompt)

        # Simple fallback
        ref = f"\\chapterref{{chapter{source_chapter}}}"
        return f"(ראה {ref})"

    def apply_fixes(
        self,
        content: str,
        issues: List[DedupIssue],
    ) -> str:
        """
        Apply all fixes to content.

        Args:
            content: Original file content
            issues: List of dedup issues with fixes

        Returns:
            Fixed content with chapterref replacements
        """
        lines = content.split("\n")

        for issue in sorted(issues, key=lambda i: i.line, reverse=True):
            if issue.fix and 0 < issue.line <= len(lines):
                line_idx = issue.line - 1
                original_line = lines[line_idx]

                # Try to find and replace the duplicate content
                if issue.content in original_line:
                    lines[line_idx] = original_line.replace(
                        issue.content,
                        issue.fix,
                        1,
                    )
                else:
                    # Append reference as comment
                    lines[line_idx] += f" % Deduplicated: {issue.fix}"

        return "\n".join(lines)

    def generate_fix(self, result: ComparisonResult) -> str:
        """
        Generate fix string for a comparison result.

        Args:
            result: ComparisonResult with duplicate info

        Returns:
            LaTeX string with chapterref
        """
        source_ch = result.source_chunk.chapter_num
        ref = f"\\chapterref{{chapter{source_ch}}}"

        if result.duplicate_segments:
            segment = result.duplicate_segments[0][:50]
            return f"ראה {ref} עבור הסבר על {segment}"

        return f"(ראה {ref})"
