"""
Mdframed page break fixer for LaTeX documents.

Fixes mdframed bad page break issues by adding spacing control.
Aligned with qa-mdframed-fix skill.md patterns.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FixApplied:
    """Represents a fix that was applied."""
    file: str
    line: int
    before: str
    after: str
    strategy: str
    verified: bool = False


@dataclass
class MdframedFixResult:
    """Result of mdframed fix operation."""
    fixes_applied: List[FixApplied] = field(default_factory=list)
    files_modified: int = 0
    warnings_eliminated: int = 0

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied else "NO_CHANGES"


class MdframedFixer:
    """
    Fixes mdframed page break issues.

    Strategies (from skill.md):
    1. vspace - Add \\vspace{1em} before box
    2. nopagebreak - Add \\nopagebreak before box
    3. combined - Both vspace and nopagebreak
    4. clearpage - Force page break (last resort)
    """

    BOX_PATTERN = r"(\\begin\{(dobox|dontbox|tcolorbox)\}(\[[^\]]*\])?)"
    HEADING_PATTERN = r"\\(section|subsection|subsubsection|chapter)\{"

    SPACING = {
        "default": r"\vspace{1em}",
        "after_heading": r"\vspace{0.5em}",
        "after_long_para": r"\vspace{1.5em}",
        "important": r"\vspace{2em}",
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fixer with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def fix_file(self, file_path: Path, line_numbers: List[int] = None) -> MdframedFixResult:
        """Fix mdframed issues in a file."""
        result = MdframedFixResult()
        if not file_path.exists():
            return result

        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        modified = False

        # Find all box environments if no specific lines given
        if not line_numbers:
            line_numbers = self._find_box_lines(lines)

        # Process in reverse to maintain line numbers
        for line_num in sorted(line_numbers, reverse=True):
            if 0 < line_num <= len(lines):
                fix = self._apply_fix(lines, line_num - 1)  # 0-indexed
                if fix:
                    result.fixes_applied.append(fix)
                    modified = True

        if modified:
            result.files_modified = 1
            new_content = "\n".join(lines)
            file_path.write_text(new_content, encoding="utf-8")

        return result

    def fix_content(self, content: str, line_numbers: List[int] = None) -> tuple:
        """Fix mdframed issues in content string (for testing)."""
        result = MdframedFixResult()
        lines = content.split("\n")

        if not line_numbers:
            line_numbers = self._find_box_lines(lines)

        for line_num in sorted(line_numbers, reverse=True):
            if 0 < line_num <= len(lines):
                fix = self._apply_fix(lines, line_num - 1)
                if fix:
                    result.fixes_applied.append(fix)

        return "\n".join(lines), result

    def _find_box_lines(self, lines: List[str]) -> List[int]:
        """Find line numbers with box environments."""
        box_lines = []
        for i, line in enumerate(lines):
            if re.search(self.BOX_PATTERN, line):
                box_lines.append(i + 1)  # 1-indexed
        return box_lines

    def _apply_fix(self, lines: List[str], idx: int) -> Optional[FixApplied]:
        """Apply fix before box at given index."""
        if idx >= len(lines):
            return None

        line = lines[idx]
        if not re.search(self.BOX_PATTERN, line):
            return None

        strategy = self._determine_strategy(lines, idx)
        fix_cmd = self._get_fix_command(strategy)
        before = line

        # Insert fix before the box line
        lines.insert(idx, fix_cmd)

        return FixApplied(
            file="", line=idx + 1, before=before[:60],
            after=f"{fix_cmd}\\n{before[:40]}...", strategy=strategy
        )

    def _determine_strategy(self, lines: List[str], idx: int) -> str:
        """Determine best fix strategy based on context."""
        # Check if box is right after heading
        for i in range(max(0, idx - 3), idx):
            if re.search(self.HEADING_PATTERN, lines[i]):
                return "nopagebreak"

        # Check if preceding content is a long paragraph
        prev_content = ""
        for i in range(max(0, idx - 5), idx):
            prev_content += lines[i]
        if len(prev_content) > 500:
            return "vspace_long"

        return "vspace"

    def _get_fix_command(self, strategy: str) -> str:
        """Get LaTeX command for fix strategy."""
        commands = {
            "vspace": r"\vspace{1em}",
            "vspace_long": r"\vspace{1.5em}",
            "nopagebreak": r"\nopagebreak",
            "combined": r"\vspace{1em}" + "\n" + r"\nopagebreak",
            "clearpage": r"\clearpage",
        }
        return commands.get(strategy, r"\vspace{1em}")

    def to_dict(self, result: MdframedFixResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-mdframed-fix",
            "status": result.status,
            "fixes_applied": [
                {
                    "file": f.file, "line": f.line, "before": f.before,
                    "after": f.after, "strategy": f.strategy, "verified": f.verified
                }
                for f in result.fixes_applied
            ],
            "summary": {
                "files_modified": result.files_modified,
                "fixes_applied": len(result.fixes_applied),
                "warnings_eliminated": result.warnings_eliminated
            },
            "qa_report_updated": True
        }
