"""
Caption length detector for LaTeX documents.

Detects figure/table captions that are too long (descriptions instead of titles).
These create verbose List of Figures/Tables entries.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .caption_length_rules import CAPTION_LENGTH_RULES, MAX_CAPTION_LENGTH


class CaptionLengthDetector(DetectorInterface):
    """
    Detects captions that are too long for List of Figures/Tables.

    Detects:
    - Captions exceeding max length without short title
    - Captions with description pattern (title: explanation)
    - Multi-sentence captions
    """

    def __init__(self) -> None:
        """Initialize detector with rules."""
        self._rules = CAPTION_LENGTH_RULES

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """Detect long caption issues in content."""
        issues: List[Issue] = []

        # Skip non-tex files
        if not file_path.endswith((".tex", ".ltx")):
            return issues

        lines = content.split("\n")

        for rule_name, rule_def in self._rules.items():
            if rule_def.get("multiline"):
                issues.extend(self._check_multiline_rule(
                    rule_name, rule_def, content, file_path, offset
                ))
            else:
                issues.extend(self._check_line_rule(
                    rule_name, rule_def, lines, file_path, offset
                ))

        return issues

    def _check_line_rule(
        self,
        rule_name: str,
        rule_def: Dict,
        lines: List[str],
        file_path: str,
        offset: int,
    ) -> List[Issue]:
        """Check rule against individual lines."""
        issues = []
        pattern = re.compile(rule_def["pattern"])
        neg_pattern = rule_def.get("negative_pattern")
        is_brace_balanced = rule_def.get("brace_balanced", False)
        max_length = rule_def.get("max_length", MAX_CAPTION_LENGTH)

        for line_num, line in enumerate(lines, start=1):
            # Skip comments
            if line.strip().startswith("%"):
                continue

            # Check negative pattern first (skip if matches)
            if neg_pattern and re.search(neg_pattern, line):
                continue

            # Check main pattern
            match = pattern.search(line)
            if match:
                caption_text = match.group(1) if match.lastindex else match.group(0)

                # For brace_balanced rules, validate length post-match
                if is_brace_balanced and len(caption_text) < max_length:
                    continue  # Skip short captions

                issues.append(self._create_issue(
                    rule_name, rule_def, caption_text,
                    file_path, line_num + offset
                ))

        return issues

    def _check_multiline_rule(
        self,
        rule_name: str,
        rule_def: Dict,
        content: str,
        file_path: str,
        offset: int,
    ) -> List[Issue]:
        """Check multiline patterns (e.g., figure environments)."""
        issues = []
        pattern = re.compile(rule_def["pattern"], re.DOTALL)
        neg_pattern = rule_def.get("negative_pattern")
        is_brace_balanced = rule_def.get("brace_balanced", False)
        max_length = rule_def.get("max_length", 80)  # Stricter for figures

        for match in pattern.finditer(content):
            # Skip if negative pattern matches in this region
            region = match.group(0)
            if neg_pattern and re.search(neg_pattern, region):
                continue

            # Calculate line number
            line_num = content[:match.start()].count("\n") + 1
            caption_text = match.group(1) if match.lastindex else region[:60]

            # For brace_balanced rules, validate length post-match
            if is_brace_balanced and len(caption_text) < max_length:
                continue  # Skip short captions

            issues.append(self._create_issue(
                rule_name, rule_def, caption_text,
                file_path, line_num + offset
            ))

        return issues

    def _create_issue(
        self,
        rule_name: str,
        rule_def: Dict,
        caption_text: str,
        file_path: str,
        line_num: int,
    ) -> Issue:
        """Create issue from match."""
        # Extract short title suggestion
        short_title = self._extract_short_title(caption_text)

        return Issue(
            rule=rule_name,
            file=file_path,
            line=line_num,
            content=caption_text[:80] + "..." if len(caption_text) > 80 else caption_text,
            severity=rule_def["severity"],
            fix=rule_def.get("fix_template", ""),
            context={
                "caption_text": caption_text,
                "suggested_short_title": short_title,
                "caption_length": len(caption_text),
            },
        )

    def _extract_short_title(self, caption_text: str) -> str:
        """Extract suggested short title from caption text."""
        # Strategy 1: Split at colon
        if ":" in caption_text:
            parts = caption_text.split(":", 1)
            if len(parts[0]) <= 60:
                return parts[0].strip()

        # Strategy 2: First sentence
        sentences = re.split(r"\.\s+", caption_text)
        if sentences and len(sentences[0]) <= 60:
            return sentences[0].strip()

        # Strategy 3: First N characters
        if len(caption_text) > 50:
            # Find word boundary near 50 chars
            truncated = caption_text[:50]
            last_space = truncated.rfind(" ")
            if last_space > 30:
                return truncated[:last_space].strip() + "..."

        return caption_text[:50] + "..."

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}

    def detect_in_file(self, file_path: str) -> List[Issue]:
        """Convenience method to detect issues in a file."""
        from pathlib import Path
        path = Path(file_path)
        if not path.exists():
            return []
        content = path.read_text(encoding="utf-8", errors="replace")
        return self.detect(content, str(path))
