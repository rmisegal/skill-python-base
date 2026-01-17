"""
Dedup Fixer - Implements FixerInterface for QA integration.

Applies chapterref fixes to detected duplicates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional

from qa_engine.domain.interfaces import FixerInterface
from qa_engine.domain.models.issue import Issue

from .config import DedupConfig
from .models import DedupIssue, DedupSeverity
from .rewriter import ChapterRefRewriter


class DedupFixer(FixerInterface):
    """
    Fixer for chapter duplicates.

    Implements FixerInterface for integration with QA pipeline.
    Applies chapterref replacements to duplicate content.
    """

    PATTERNS = {
        "dedup-chapterref": {
            "find": "duplicate content",
            "replace": "\\chapterref{chapterN}",
            "description": "Replace duplicate with chapter reference",
        },
        "dedup-see-reference": {
            "find": "repeated explanation",
            "replace": "(see \\chapterref{chapterN})",
            "description": "Add see-reference to earlier chapter",
        },
    }

    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        llm_callback: Optional[Callable[[str], str]] = None,
    ) -> None:
        """
        Initialize fixer.

        Args:
            config_path: Path to bc_dedup.json
            llm_callback: LLM function for rewriting
        """
        self._config = DedupConfig()
        if config_path:
            self._config.load(config_path)
        self._rewriter = ChapterRefRewriter(self._config, llm_callback)

    def _issue_to_dedup(self, issue: Issue) -> DedupIssue:
        """Convert standard Issue to DedupIssue."""
        context = issue.context or {}
        return DedupIssue(
            rule=issue.rule,
            file=issue.file,
            line=issue.line,
            content=issue.content,
            severity=DedupSeverity(issue.severity.value),
            source_chapter=context.get("source_chapter", 0),
            target_chapter=context.get("target_chapter", 0),
            fix=issue.fix,
            context=context,
        )

    def fix(self, content: str, issues: List[Issue]) -> str:
        """
        Apply fixes to content.

        Args:
            content: Original content
            issues: List of Issue objects to fix

        Returns:
            Fixed content string
        """
        # Filter to only dedup-related issues
        dedup_issues = [
            self._issue_to_dedup(i)
            for i in issues
            if i.rule.startswith("dedup-")
        ]

        if not dedup_issues:
            return content

        return self._rewriter.apply_fixes(content, dedup_issues)

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return supported fix patterns."""
        return self.PATTERNS.copy()
