"""
Caption fixer for Hebrew RTL LaTeX documents.

Implements FixerInterface - fixes caption alignment issues.
Aligned with qa-table-fix-captions skill.md patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue
from .caption_patterns import CAPTION_PATTERNS


@dataclass
class CaptionFix:
    """Represents a caption fix."""
    file: str
    line: int
    old: str
    new: str
    pattern: str


@dataclass
class CaptionFixResult:
    """Result of caption fixing."""
    fixes_applied: int = 0
    changes: List[CaptionFix] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied > 0 else "NO_CHANGES"


class CaptionFixer(FixerInterface):
    """
    Fixes caption alignment issues in Hebrew RTL LaTeX documents.

    Handles:
    - captionsetup{justification=raggedleft} -> centering
    - flushleft wrapper around caption -> centering
    - Table-specific caption overrides
    """

    def __init__(self) -> None:
        """Initialize fixer with patterns."""
        self._patterns = CAPTION_PATTERNS

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        if not issues:
            return content

        # Group issues by rule
        issues_by_rule: Dict[str, List[Issue]] = {}
        for issue in issues:
            issues_by_rule.setdefault(issue.rule, []).append(issue)

        # Apply applicable patterns
        for pattern_name, pattern_def in self._patterns.items():
            for rule in pattern_def.get("applies_to", []):
                if rule in issues_by_rule:
                    content = self._apply_pattern(content, pattern_def)

        return content

    def fix_content(self, content: str, file_path: str = "") -> tuple:
        """Fix all caption issues in content (auto-detect mode)."""
        result = CaptionFixResult()
        lines = content.split("\n")

        # Pattern 1 & 2: Fix captionsetup justification
        for i, line in enumerate(lines):
            if "captionsetup" in line and "raggedleft" in line:
                new_line = self._fix_captionsetup(line)
                if new_line != line:
                    result.changes.append(CaptionFix(
                        file=file_path, line=i + 1,
                        old=line.strip(), new=new_line.strip(),
                        pattern="fix-captionsetup"
                    ))
                    lines[i] = new_line
                    result.fixes_applied += 1

        content = "\n".join(lines)

        # Pattern 3: Fix flushleft wrapper
        content, flushleft_fixes = self._fix_flushleft_captions(content, file_path)
        result.changes.extend(flushleft_fixes)
        result.fixes_applied += len(flushleft_fixes)

        return content, result

    def _apply_pattern(self, content: str, pattern_def: Dict) -> str:
        """Apply a single pattern to content."""
        find = pattern_def["find"]
        replace = pattern_def.get("replace", "")
        if replace:
            content = re.sub(find, replace, content)
        return content

    def _fix_captionsetup(self, line: str) -> str:
        """Fix captionsetup justification setting."""
        # Handle various forms of captionsetup
        line = re.sub(
            r"(\\captionsetup\{[^}]*)justification=raggedleft([^}]*\})",
            r"\1justification=centering\2",
            line
        )
        return line

    def _fix_flushleft_captions(self, content: str, file_path: str) -> tuple:
        """Fix flushleft-wrapped captions."""
        fixes = []
        pattern = r"\\begin\{flushleft\}\s*(\\caption\{[^}]*\})\s*\\end\{flushleft\}"

        def replacer(match):
            old = match.group(0)
            caption = match.group(1)
            new = f"\\centering\n{caption}"
            # Find approximate line number
            pos = match.start()
            line_num = content[:pos].count("\n") + 1
            fixes.append(CaptionFix(
                file=file_path, line=line_num,
                old=old[:50] + "..." if len(old) > 50 else old,
                new=new[:50] + "..." if len(new) > 50 else new,
                pattern="fix-flushleft-caption"
            ))
            return new

        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        return content, fixes

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        return {
            name: {
                "find": pat.get("find", ""),
                "replace": pat.get("replace", ""),
                "description": pat.get("description", ""),
            }
            for name, pat in self._patterns.items()
        }

    def to_dict(self, result: CaptionFixResult) -> Dict:
        """Convert result to skill.md output format."""
        return {
            "skill": "qa-table-fix-captions",
            "status": result.status,
            "fixes_applied": result.fixes_applied,
            "changes": [
                {"file": c.file, "line": c.line, "old": c.old, "new": c.new}
                for c in result.changes
            ],
        }
