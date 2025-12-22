"""
Subfiles chapter detector for LaTeX documents.

Detects chapter files missing subfiles preamble for standalone compilation.
Aligned with qa-infra-subfiles-detect skill.md patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SubfilesIssue:
    """Represents a subfiles-related issue."""
    rule: str
    file: str
    severity: str
    message: str


@dataclass
class SubfilesDetectResult:
    """Result of subfiles detection scan."""
    issues: List[SubfilesIssue] = field(default_factory=list)
    files_checked: int = 0
    files_with_issues: int = 0

    @property
    def verdict(self) -> str:
        return "FAIL" if self.issues else "PASS"


class SubfilesChapterDetector:
    """
    Detects chapter files missing subfiles preamble.

    Aligned with qa-infra-subfiles-detect skill.md:
    - Rule 1: Missing documentclass[../main.tex]{subfiles}
    - Rule 2: Missing begin{document}
    - Rule 3: Missing end{document}
    """

    SUBFILES_DOCCLASS = r"\\documentclass\[[^\]]*\]\{subfiles\}"
    BEGIN_DOCUMENT = r"\\begin\{document\}"
    END_DOCUMENT = r"\\end\{document\}"

    RULES = {
        "missing-subfiles-documentclass": "File missing \\documentclass[../main.tex]{subfiles}",
        "missing-begin-document": "File missing \\begin{document}",
        "missing-end-document": "File missing \\end{document}",
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize detector with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def detect_in_directory(self, chapters_dir: str = "chapters") -> SubfilesDetectResult:
        """Scan chapters directory for files missing subfiles preamble."""
        result = SubfilesDetectResult()
        chapters_path = self.project_root / chapters_dir

        if not chapters_path.exists():
            return result

        tex_files = list(set(chapters_path.glob("*.tex")))
        for tex_file in tex_files:
            result.files_checked += 1
            file_issues = self.detect_in_file(tex_file)
            if file_issues:
                result.files_with_issues += 1
                result.issues.extend(file_issues)

        return result

    def detect_in_file(self, file_path: Path) -> List[SubfilesIssue]:
        """Check a single file for subfiles issues."""
        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = str(file_path.relative_to(self.project_root))
            return self.detect_content(content, rel_path)
        except Exception:
            return []

    def detect_content(self, content: str, file_path: str) -> List[SubfilesIssue]:
        """Check content string for subfiles issues."""
        issues: List[SubfilesIssue] = []
        checks = [
            (self.SUBFILES_DOCCLASS, "missing-subfiles-documentclass"),
            (self.BEGIN_DOCUMENT, "missing-begin-document"),
            (self.END_DOCUMENT, "missing-end-document"),
        ]
        for pattern, rule in checks:
            if not re.search(pattern, content):
                issues.append(SubfilesIssue(
                    rule=rule, file=file_path, severity="CRITICAL",
                    message=self.RULES[rule],
                ))
        return issues

    def to_dict(self, result: SubfilesDetectResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-infra-subfiles-detect",
            "status": "DONE",
            "verdict": result.verdict,
            "issues": [
                {"rule": i.rule, "file": i.file, "severity": i.severity, "message": i.message}
                for i in result.issues
            ],
            "summary": f"{result.files_with_issues} files missing subfiles preamble",
            "triggers": ["qa-infra-subfiles-fix"] if result.issues else [],
        }

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return self.RULES.copy()
