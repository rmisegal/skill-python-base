"""
Itemsep detector for detecting excessive vertical spacing.

Implements v1.5 rule from qa-typeset-detect skill.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from .typeset_models import ItemsepIssue


class ItemsepDetector:
    """
    Detects itemize/enumerate without noitemsep in flushbottom context.

    Detection criteria from skill.md v1.5:
    1. Document class is 'book' (has flushbottom by default)
    2. Log file has >10 "Underfull vbox (badness 10000)" warnings
    3. Preamble does NOT contain raggedbottom
    4. Source contains itemize/enumerate without [noitemsep] or [nosep]
    """

    # List environment patterns
    LIST_PATTERN = r"\\begin\{(itemize|enumerate)\}(\[[^\]]*\])?"

    # Safe option patterns
    SAFE_OPTIONS = ["noitemsep", "nosep"]

    def detect_in_file(
        self,
        file_path: Path,
        has_raggedbottom: bool = False,
        underfull_vbox_count: int = 0,
    ) -> List[ItemsepIssue]:
        """Detect itemsep issues in a LaTeX file."""
        if not file_path.exists():
            return []

        # Skip if raggedbottom is set or few underfull vbox warnings
        if has_raggedbottom or underfull_vbox_count <= 10:
            return []

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        return self.detect_in_content(content, str(file_path))

    def detect_in_content(
        self,
        content: str,
        file_path: str,
        check_context: bool = True,
    ) -> List[ItemsepIssue]:
        """Detect itemsep issues in content."""
        issues: List[ItemsepIssue] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            match = re.search(self.LIST_PATTERN, line)
            if not match:
                continue

            env_type = match.group(1)  # itemize or enumerate
            options = match.group(2) or ""

            # Check if has safe options
            if any(opt in options for opt in self.SAFE_OPTIONS):
                continue

            issues.append(ItemsepIssue(
                file=file_path, line=line_num, env_type=env_type
            ))

        return issues

    def check_raggedbottom(self, content: str) -> bool:
        """Check if content has raggedbottom command."""
        return bool(re.search(r"\\raggedbottom", content))

    def check_book_class(self, content: str) -> bool:
        """Check if document uses book class."""
        return bool(re.search(r"\\documentclass.*\{.*book.*\}", content))
