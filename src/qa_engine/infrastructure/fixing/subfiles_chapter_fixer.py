"""
Subfiles chapter fixer for LaTeX documents.

Fixes chapter files by adding subfiles preamble for standalone compilation.
Aligned with qa-infra-subfiles-fix skill.md patterns.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FixRecord:
    """Record of fixes applied to a file."""
    file: str
    fixes_applied: List[str] = field(default_factory=list)
    backup: str = ""


@dataclass
class SubfilesFixResult:
    """Result of subfiles fix operation."""
    files_fixed: List[FixRecord] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return f"{len(self.files_fixed)} files fixed with subfiles preamble"


class SubfilesChapterFixer:
    """Fixes chapter files by adding subfiles preamble."""

    SUBFILES_DOCCLASS = r"\\documentclass\[[^\]]*\]\{subfiles\}"
    BEGIN_DOCUMENT = r"\\begin\{document\}"
    END_DOCUMENT = r"\\end\{document\}"
    CHAPTER_PATTERN = r"\\chapter\{"

    PATTERNS = {
        "added-documentclass-subfiles": "Add \\documentclass[../main.tex]{subfiles}",
        "added-begin-document": "Add \\begin{document} after documentclass",
        "added-end-document": "Add \\end{document} at end of file",
    }

    def __init__(self, project_root: Optional[Path] = None, main_path: str = "../main.tex"):
        """Initialize fixer with project root and main.tex path."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.main_path = main_path

    def fix_files(self, issues: List[Dict]) -> SubfilesFixResult:
        """Fix files based on detected issues."""
        result = SubfilesFixResult()
        files_to_fix: Dict[str, List[str]] = {}

        for issue in issues:
            file_path = issue.get("file", "")
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(issue.get("rule", ""))

        for rel_path, rules in files_to_fix.items():
            record = self._fix_file(self.project_root / rel_path, rules)
            if record:
                result.files_fixed.append(record)
        return result

    def _fix_file(self, file_path: Path, rules: List[str]) -> Optional[FixRecord]:
        """Fix a single file based on detected rules."""
        if not file_path.exists():
            return None

        rel_path = str(file_path.relative_to(self.project_root))
        record = FixRecord(file=rel_path)

        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        shutil.copy2(file_path, backup_path)
        record.backup = str(backup_path.relative_to(self.project_root))

        # Apply fixes
        content = file_path.read_text(encoding="utf-8")
        content, applied = self._apply_fixes(content, rules)
        record.fixes_applied = applied

        file_path.write_text(content, encoding="utf-8")
        return record

    def _apply_fixes(self, content: str, rules: List[str]) -> tuple:
        """Apply fixes and return (content, list of applied fixes)."""
        applied = []
        needs_preamble = "missing-subfiles-documentclass" in rules or \
                         "missing-begin-document" in rules

        if needs_preamble and not re.search(self.SUBFILES_DOCCLASS, content):
            content = self._add_preamble(content)
            applied.extend(["added-documentclass-subfiles", "added-begin-document"])

        if "missing-end-document" in rules and not re.search(self.END_DOCUMENT, content):
            content = content.rstrip() + "\n\n\\end{document}\n"
            applied.append("added-end-document")

        return content, applied

    def _add_preamble(self, content: str) -> str:
        """Add documentclass and begin{document} before \\chapter{}."""
        preamble = f"\\documentclass[{self.main_path}]{{subfiles}}\n\\begin{{document}}\n\n"
        chapter_match = re.search(self.CHAPTER_PATTERN, content)

        if chapter_match:
            line_start = content.rfind("\n", 0, chapter_match.start()) + 1
            return content[:line_start] + preamble + content[line_start:]

        # No chapter found - add after initial comments
        lines = content.split("\n")
        insert_pos = next(
            (i for i, line in enumerate(lines) if line.strip() and not line.strip().startswith("%")),
            len(lines)
        )
        lines.insert(insert_pos, preamble)
        return "\n".join(lines)

    def fix_content(self, content: str, rules: List[str]) -> str:
        """Fix content string based on rules (for testing)."""
        content, _ = self._apply_fixes(content, rules)
        return content

    def _verify_fix(self, content: str) -> bool:
        """Verify file has all 3 required elements."""
        return all(re.search(p, content) for p in [
            self.SUBFILES_DOCCLASS, self.BEGIN_DOCUMENT, self.END_DOCUMENT])

    def to_dict(self, result: SubfilesFixResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-infra-subfiles-fix",
            "status": "DONE" if not result.errors else "PARTIAL",
            "files_fixed": [{"file": f.file, "fixes_applied": f.fixes_applied,
                            "backup": f.backup} for f in result.files_fixed],
            "summary": result.summary,
        }

    def get_patterns(self) -> Dict[str, str]:
        """Return dict of fix patterns."""
        return self.PATTERNS.copy()
