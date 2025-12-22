"""
Float fixer for typeset issues.

Applies deterministic fixes for "Float too large" warnings.
Context-dependent fixes (code splitting) require LLM guidance.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue
from .float_patterns import (
    FLOAT_PATTERNS,
    OVERFLOW_THRESHOLDS,
    CONTENT_TYPE_PATTERNS,
)


@dataclass
class FloatFix:
    """Represents a single float fix applied."""
    file: str
    line: int
    pattern_id: str
    old: str
    new: str


@dataclass
class FloatFixResult:
    """Result of float fixing operation."""
    fixes_applied: int = 0
    fixes: List[FloatFix] = field(default_factory=list)
    llm_required: List[Dict] = field(default_factory=list)


class FloatFixer(FixerInterface):
    """
    Fixes float-related issues in LaTeX documents.

    Handles deterministic patterns:
    - Adding breakable option to tcolorbox
    - Scaling figures to textheight
    - Using smaller fonts in lstlisting
    - Adjusting float placement options

    Delegates to LLM:
    - Code block splitting (requires semantic understanding)
    - Content restructuring decisions
    """

    def __init__(self) -> None:
        self._patterns = FLOAT_PATTERNS

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        fixed = content
        for issue in issues:
            if issue.rule == "typeset-float-too-large":
                fixed = self._apply_float_fixes(fixed, issue)
        return fixed

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        return {
            name: {
                "find": p["find"],
                "replace": p["replace"],
                "description": p["description"],
            }
            for name, p in self._patterns.items()
        }

    def fix_content(
        self, content: str, file_path: str = "", overflow_pt: float = 0.0
    ) -> tuple[str, FloatFixResult]:
        """
        Fix float issues in content with overflow context.

        Args:
            content: LaTeX source content
            file_path: Source file path
            overflow_pt: Overflow amount in points (from log)

        Returns:
            Tuple of (fixed_content, FloatFixResult)
        """
        result = FloatFixResult()
        fixed = content
        content_type = self._detect_content_type(content)

        # Determine fix strategy based on overflow
        if overflow_pt > OVERFLOW_THRESHOLDS["critical"]:
            result.llm_required.append({
                "reason": "Large overflow requires content splitting",
                "overflow_pt": overflow_pt,
                "suggestion": "Split content into multiple parts",
            })

        # Apply deterministic fixes based on content type
        for pattern_id, pattern in self._patterns.items():
            if self._should_apply(pattern, content_type, fixed):
                new_content = re.sub(pattern["find"], pattern["replace"], fixed)
                if new_content != fixed:
                    result.fixes_applied += 1
                    result.fixes.append(FloatFix(
                        file=file_path, line=0, pattern_id=pattern_id,
                        old=pattern["find"], new=pattern["replace"],
                    ))
                    fixed = new_content

        return fixed, result

    def _apply_float_fixes(self, content: str, issue: Issue) -> str:
        """Apply float-specific fixes around issue location."""
        lines = content.split("\n")
        issue_line = issue.line - 1
        context_start = max(0, issue_line - 10)
        context_end = min(len(lines), issue_line + 10)
        context = "\n".join(lines[context_start:context_end])
        content_type = self._detect_content_type(context)

        for pattern_id, pattern in self._patterns.items():
            if self._should_apply(pattern, content_type, content):
                content = re.sub(pattern["find"], pattern["replace"], content)
        return content

    def _detect_content_type(self, content: str) -> str:
        """Detect content type from LaTeX source."""
        for ctype, patterns in CONTENT_TYPE_PATTERNS.items():
            if any(re.search(p, content) for p in patterns):
                return ctype
        return "any"

    def _should_apply(self, pattern: Dict, content_type: str, content: str) -> bool:
        """Check if pattern should be applied."""
        ptype = pattern.get("content_type", "any")
        if ptype != "any" and ptype != content_type:
            return False

        # Check condition if present
        condition = pattern.get("condition")
        if condition:
            if "breakable not in" in condition and "breakable" in content:
                return False
            if "height not in" in condition and "height=" in content:
                return False
            if "basicstyle not in" in condition and "basicstyle" in content:
                return False
            if "p not in" in condition and "[" in content and "p" in content:
                return False
        return True

    def get_fix_strategy(self, overflow_pt: float) -> Dict[str, str]:
        """Get recommended fix strategy based on overflow amount."""
        if overflow_pt > OVERFLOW_THRESHOLDS["critical"]:
            return {
                "level": "critical",
                "python_fixes": ["scale-figure-height", "use-small-lstlisting"],
                "llm_required": "Split content into logical parts",
            }
        elif overflow_pt > OVERFLOW_THRESHOLDS["warning"]:
            return {
                "level": "warning",
                "python_fixes": ["use-small-lstlisting", "add-breakable-tcolorbox"],
                "llm_required": None,
            }
        return {
            "level": "minor",
            "python_fixes": ["use-page-placement", "add-breakable-tcolorbox"],
            "llm_required": None,
        }
