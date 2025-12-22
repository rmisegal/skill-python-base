"""
TikZ source analyzer for detecting overflow risks.

Implements Step 3 from qa-typeset-detect skill.md v1.4.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from .typeset_models import TikzOverflowRisk


class TikzDetector:
    """
    Detects TikZ pictures that may overflow text width.

    Detection criteria from skill.md:
    1. tikzpicture NOT preceded by resizebox within 50 chars
    2. tikzpicture NOT inside adjustbox
    3. tikzpicture options do NOT contain scale= or xscale=
    4. TikZ picture contains absolute coordinates > 10cm
    """

    # Pattern to find tikzpicture environments
    TIKZ_PATTERN = r"\\begin\{tikzpicture\}(\[[^\]]*\])?"

    # Safe wrapper patterns
    RESIZEBOX_PATTERN = r"\\resizebox\{[^}]*\}\{[^}]*\}\s*\{"
    ADJUSTBOX_PATTERN = r"\\begin\{adjustbox\}\{[^}]*width[^}]*\}"

    # Scale pattern in options
    SCALE_PATTERN = r"\[.*(?:scale|xscale).*\]"

    # Large coordinate pattern (>=10 in any axis)
    LARGE_COORD_PATTERN = r"\((\d{2,}),|,(\d{2,})\)"

    def detect_in_file(self, file_path: Path) -> List[TikzOverflowRisk]:
        """Detect TikZ overflow risks in a LaTeX file."""
        if not file_path.exists():
            return []
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        return self.detect_in_content(content, str(file_path))

    def detect_in_content(self, content: str, file_path: str) -> List[TikzOverflowRisk]:
        """Detect TikZ overflow risks in content."""
        issues: List[TikzOverflowRisk] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            match = re.search(self.TIKZ_PATTERN, line)
            if not match:
                continue

            # Check for safe wrappers
            if self._has_safe_wrapper(content, line_num, lines):
                continue

            # Check for scale option
            options = match.group(1) or ""
            if re.search(self.SCALE_PATTERN, options):
                continue

            # Check for large coordinates in tikz block
            tikz_block = self._extract_tikz_block(lines, line_num - 1)
            has_large_coords = bool(re.search(self.LARGE_COORD_PATTERN, tikz_block))

            severity = "CRITICAL" if has_large_coords else "WARNING"
            issue_type = "large_coordinates" if has_large_coords else "no_width_constraint"
            fix = r"Wrap with \resizebox{\textwidth}{!}{...} or add scale option"

            issues.append(TikzOverflowRisk(
                file=file_path, line=line_num,
                content=line.strip()[:80],
                issue=issue_type, severity=severity, fix=fix
            ))

        return issues

    def _has_safe_wrapper(self, content: str, line_num: int, lines: List[str]) -> bool:
        """Check if tikzpicture has safe wrapper."""
        # Check preceding 50 characters for resizebox
        start = max(0, line_num - 3)
        prefix = "\n".join(lines[start:line_num])
        if re.search(self.RESIZEBOX_PATTERN, prefix[-100:] if len(prefix) > 100 else prefix):
            return True

        # Check for adjustbox wrapper
        if re.search(self.ADJUSTBOX_PATTERN, prefix):
            return True

        return False

    def _extract_tikz_block(self, lines: List[str], start_idx: int) -> str:
        """Extract tikzpicture block content."""
        block_lines = []
        depth = 0
        for i in range(start_idx, min(start_idx + 100, len(lines))):
            line = lines[i]
            block_lines.append(line)
            if r"\begin{tikzpicture}" in line:
                depth += 1
            if r"\end{tikzpicture}" in line:
                depth -= 1
                if depth <= 0:
                    break
        return "\n".join(block_lines)
