"""
Section orphan fixer for LaTeX documents.

Fixes section orphan issues by adding needspace protection.
Aligned with qa-section-orphan-fix skill patterns.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from ..detection.orphan_rules import SECTION_PATTERNS, NEEDSPACE_PATTERN, ORPHAN_THRESHOLDS


@dataclass
class OrphanFixApplied:
    """Represents an orphan fix that was applied."""
    file: str
    line: int
    section_type: str
    section_title: str
    fix_type: str  # "needspace" or "clearpage"
    threshold: int
    before: str
    after: str


@dataclass
class OrphanFixResult:
    """Result of orphan fix operation."""
    fixes_applied: List[OrphanFixApplied] = field(default_factory=list)
    files_modified: int = 0
    sections_protected: int = 0

    @property
    def status(self) -> str:
        return "DONE" if self.fixes_applied else "NO_CHANGES"


class SectionOrphanFixer:
    """
    Fixes section orphan issues in LaTeX documents.

    Fix strategies:
    1. needspace - Add \\par\\needspace{X\\baselineskip} before section (preferred)
    2. clearpage - Force page break for persistent orphans (last resort)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fixer with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def fix_file(self, file_path: Path, line_numbers: List[int] = None) -> OrphanFixResult:
        """Fix orphan issues in a file."""
        result = OrphanFixResult()
        if not file_path.exists():
            return result

        content = file_path.read_text(encoding="utf-8")
        fixed_content, result = self.fix_content(content, line_numbers, str(file_path))

        if result.fixes_applied:
            result.files_modified = 1
            file_path.write_text(fixed_content, encoding="utf-8")

        return result

    def fix_content(self, content: str, line_numbers: List[int] = None,
                    file_path: str = "input.tex") -> tuple:
        """Fix orphan issues in content string."""
        result = OrphanFixResult()
        lines = content.split("\n")

        # Find unprotected sections if no specific lines given
        targets = self._find_unprotected_sections(lines) if not line_numbers else line_numbers

        # Process in reverse to maintain line numbers
        for line_num in sorted(targets, reverse=True):
            if 0 < line_num <= len(lines):
                fix = self._apply_fix(lines, line_num - 1, file_path)
                if fix:
                    result.fixes_applied.append(fix)
                    result.sections_protected += 1

        return "\n".join(lines), result

    def _find_unprotected_sections(self, lines: List[str]) -> List[int]:
        """Find line numbers with unprotected sections."""
        content = "\n".join(lines)
        unprotected = []

        for sec_type, pattern in SECTION_PATTERNS.items():
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                # Check if already protected
                start_line = max(0, line_num - 4)
                preceding = "\n".join(lines[start_line:line_num - 1])
                if not re.search(NEEDSPACE_PATTERN, preceding):
                    unprotected.append(line_num)

        return unprotected

    def _apply_fix(self, lines: List[str], idx: int, file_path: str) -> Optional[OrphanFixApplied]:
        """Apply needspace fix before section at given index."""
        if idx >= len(lines):
            return None

        line = lines[idx]

        # Find which section type this is
        sec_type = None
        sec_title = ""
        for st, pattern in SECTION_PATTERNS.items():
            match = re.search(pattern, line)
            if match:
                sec_type = st
                sec_title = match.group(1)[:50]
                break

        if not sec_type:
            return None

        threshold = ORPHAN_THRESHOLDS.get(sec_type, 5)
        fix_cmd = f"\\par\\needspace{{{threshold}\\baselineskip}}"
        before = line[:60]

        # Insert fix before the section line
        lines.insert(idx, fix_cmd)

        return OrphanFixApplied(
            file=file_path, line=idx + 1, section_type=sec_type,
            section_title=sec_title, fix_type="needspace", threshold=threshold,
            before=before, after=f"{fix_cmd}\n{before[:40]}..."
        )

    def to_dict(self, result: OrphanFixResult) -> Dict:
        """Convert result to dictionary matching skill output format."""
        return {
            "skill": "qa-section-orphan-fix",
            "status": result.status,
            "fixes_applied": [
                {
                    "file": f.file, "line": f.line, "section_type": f.section_type,
                    "section_title": f.section_title, "fix_type": f.fix_type,
                    "threshold": f.threshold, "before": f.before, "after": f.after
                }
                for f in result.fixes_applied
            ],
            "summary": {
                "files_modified": result.files_modified,
                "fixes_applied": len(result.fixes_applied),
                "sections_protected": result.sections_protected
            }
        }
