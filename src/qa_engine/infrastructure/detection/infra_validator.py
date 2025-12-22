"""
Infrastructure validator for project structure verification.

Validates project structure after reorganization.
Aligned with qa-infra-validate skill.md patterns.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Required directories (same as infra_scanner)
REQUIRED_DIRS = [
    ".claude", ".claude/commands", ".claude/skills", ".claude/agents",
    ".claude/tasks", "chapters", "images", "src", "reviews", "doc", "examples",
]

# Valid file extensions per directory
VALID_EXTENSIONS = {
    "images": {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".gif"},
    "src": {".py", ".pyw"},
    "doc": {".md", ".txt", ".rst"},
    "chapters": {".tex"},
    "examples": {".tex"},
}


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    check: str
    message: str
    severity: str = "error"


@dataclass
class ValidationResult:
    """Result of infrastructure validation."""
    verdict: str = "PASS"
    dirs_present: int = 0
    dirs_required: int = len(REQUIRED_DIRS)
    readme_in_root: bool = False
    files_correct: bool = True
    no_files_lost: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    expected_count: int = 0
    actual_count: int = 0


class InfraValidator:
    """Validates project structure after reorganization."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize validator with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def validate(self, expected_file_count: int = 0) -> ValidationResult:
        """Validate project structure."""
        result = ValidationResult(expected_count=expected_file_count)
        self._check_directories(result)
        self._check_readme(result)
        self._check_file_locations(result)
        if expected_file_count > 0:
            self._check_file_count(result, expected_file_count)
        result.verdict = "PASS" if not result.issues else "FAIL"
        return result

    def _check_directories(self, result: ValidationResult) -> None:
        """Check all required directories exist."""
        for dir_path in REQUIRED_DIRS:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                result.dirs_present += 1
            else:
                result.issues.append(ValidationIssue(
                    check="directories", message=f"Missing: {dir_path}/"))

    def _check_readme(self, result: ValidationResult) -> None:
        """Check README.md exists in root."""
        readme = self.project_root / "README.md"
        result.readme_in_root = readme.exists() and readme.is_file()
        if not result.readme_in_root:
            result.issues.append(ValidationIssue(
                check="readme", message="README.md not found in root"))

    def _check_file_locations(self, result: ValidationResult) -> None:
        """Check files are in correct directories."""
        for dir_name, valid_exts in VALID_EXTENSIONS.items():
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
            for item in dir_path.iterdir():
                if item.is_file() and item.suffix.lower() not in valid_exts:
                    result.files_correct = False
                    result.issues.append(ValidationIssue(
                        check="file_location",
                        message=f"Wrong type in {dir_name}/: {item.name}"))

    def _check_file_count(self, result: ValidationResult, expected: int) -> None:
        """Check no files were lost during reorganization."""
        actual = self._count_all_files()
        result.actual_count = actual
        result.no_files_lost = actual >= expected
        if actual < expected:
            result.issues.append(ValidationIssue(
                check="file_count",
                message=f"Files lost: expected {expected}, found {actual}"))

    def _count_all_files(self) -> int:
        """Count all files in project."""
        count = 0
        for root, _, files in os.walk(self.project_root):
            count += len(files)
        return count

    def to_dict(self, result: ValidationResult) -> Dict:
        """Convert validation result to dictionary."""
        return {
            "skill": "qa-infra-validate",
            "status": "DONE",
            "verdict": result.verdict,
            "checks": {
                "directories": f"{result.dirs_present}/{result.dirs_required} present",
                "readme_in_root": result.readme_in_root,
                "files_correct": result.files_correct,
                "no_files_lost": result.no_files_lost,
            },
            "issues": [{"check": i.check, "message": i.message} for i in result.issues],
        }
