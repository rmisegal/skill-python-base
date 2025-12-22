"""
Infrastructure scanner for project structure analysis.

Scans project directory and identifies misplaced files.
Aligned with qa-infra-scan skill.md patterns.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Required directories for LaTeX projects
REQUIRED_DIRS = [
    ".claude/commands",
    ".claude/skills",
    ".claude/agents",
    ".claude/tasks",
    "chapters",
    "images",
    "src",
    "reviews",
    "doc",
    "examples",
]

# File categorization rules: pattern -> target directory
FILE_RULES = {
    "README.md": ".",  # Must stay in root
    "*.md": "doc",
    "*.txt": "doc",
    "*.py": "src",
    "*.png": "images",
    "*.jpg": "images",
    "*.jpeg": "images",
    "*.svg": "images",
    "*.pdf": "images",
    "chapter*.tex": "chapters",
    "example*.tex": "examples",
    "*.json": "reviews",
    "*.log": "reviews",
}


@dataclass
class MisplacedFile:
    """Represents a misplaced file."""
    file: str
    current: str
    target: str
    reason: str


@dataclass
class ScanResult:
    """Result of infrastructure scan."""
    required_dirs: int = 0
    present_dirs: int = 0
    missing_dirs: List[str] = field(default_factory=list)
    total_files: int = 0
    correctly_placed: int = 0
    misplaced: int = 0
    misplaced_files: List[MisplacedFile] = field(default_factory=list)


class InfraScanner:
    """Scans project structure and identifies misplaced files."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize scanner with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def scan(self) -> ScanResult:
        """Scan project and return analysis result."""
        result = ScanResult()
        result.required_dirs = len(REQUIRED_DIRS)

        # Check directories
        for dir_path in REQUIRED_DIRS:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                result.present_dirs += 1
            else:
                result.missing_dirs.append(dir_path + "/")

        # Scan root directory for misplaced files
        self._scan_root_files(result)

        return result

    def _scan_root_files(self, result: ScanResult) -> None:
        """Scan files in root directory."""
        for item in self.project_root.iterdir():
            if item.is_file():
                result.total_files += 1
                target = self._get_target_dir(item.name)

                if target == ".":
                    result.correctly_placed += 1
                else:
                    result.misplaced += 1
                    result.misplaced_files.append(MisplacedFile(
                        file=item.name,
                        current="./",
                        target=target + "/",
                        reason=self._get_reason(item.name),
                    ))

    def _get_target_dir(self, filename: str) -> str:
        """Determine target directory for a file."""
        # Check exact match first (README.md)
        if filename in FILE_RULES:
            return FILE_RULES[filename]

        # Check pattern matches
        name_lower = filename.lower()
        ext = Path(filename).suffix.lower()

        # Chapter files
        if name_lower.startswith("chapter") and ext == ".tex":
            return "chapters"

        # Example files
        if name_lower.startswith("example") and ext == ".tex":
            return "examples"

        # Check extension patterns
        for pattern, target in FILE_RULES.items():
            if pattern.startswith("*") and filename.endswith(pattern[1:]):
                return target

        # Unknown files stay in root
        return "."

    def _get_reason(self, filename: str) -> str:
        """Get reason for file relocation."""
        ext = Path(filename).suffix.lower()
        reasons = {
            ".md": "Documentation file",
            ".txt": "Text documentation",
            ".py": "Python source code",
            ".png": "Image file",
            ".jpg": "Image file",
            ".jpeg": "Image file",
            ".svg": "Vector image",
            ".pdf": "PDF document",
            ".json": "Configuration/review file",
            ".log": "Log file",
            ".tex": "LaTeX source",
        }
        return reasons.get(ext, "File type rule")

    def to_dict(self, result: ScanResult) -> Dict:
        """Convert scan result to dictionary."""
        return {
            "skill": "qa-infra-scan",
            "status": "DONE",
            "directories": {
                "required": result.required_dirs,
                "present": result.present_dirs,
                "missing": result.missing_dirs,
            },
            "files": {
                "total": result.total_files,
                "correctly_placed": result.correctly_placed,
                "misplaced": result.misplaced,
            },
            "misplaced_files": [
                {"file": f.file, "current": f.current, "target": f.target}
                for f in result.misplaced_files
            ],
            "triggers": ["qa-infra-reorganize"] if result.misplaced > 0 else [],
        }
