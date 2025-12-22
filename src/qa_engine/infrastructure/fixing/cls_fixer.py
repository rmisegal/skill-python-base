"""
CLS (LaTeX class file) version fixer.

Copies reference CLS to project and updates references.
Deterministic Python tool - no LLM needed for copy operations.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue

# Reference CLS location
REFERENCE_CLS_DIR = Path(r"C:\25D\CLS-examples")
REFERENCE_CLS_FILE = REFERENCE_CLS_DIR / "hebrew-academic-template.cls"


@dataclass
class FixResult:
    """Result of CLS fix operation."""

    success: bool
    message: str
    backup_path: Optional[str] = None
    new_version: Optional[str] = None


class CLSFixer(FixerInterface):
    """
    Fixes CLS version mismatches by copying reference CLS.

    Operations:
    1. Backup existing CLS file
    2. Copy reference CLS to project
    3. Report new capabilities available
    """

    def __init__(self, reference_cls: Optional[Path] = None) -> None:
        self._reference_cls = reference_cls or REFERENCE_CLS_FILE

    def fix(self, content: str, issues: List[Issue]) -> str:
        """
        Fix is not content-based for CLS - use fix_file instead.

        This method exists to satisfy interface but CLS fixing
        operates on files, not content strings.
        """
        return content

    def fix_file(self, project_cls_path: Path, create_backup: bool = True) -> FixResult:
        """
        Copy reference CLS to project location.

        Args:
            project_cls_path: Path where CLS should be copied
            create_backup: Whether to backup existing file

        Returns:
            FixResult with operation status
        """
        if not self._reference_cls.exists():
            return FixResult(
                success=False,
                message=f"Reference CLS not found: {self._reference_cls}",
            )

        backup_path = None
        if project_cls_path.exists() and create_backup:
            backup_path = project_cls_path.with_suffix(".cls.backup")
            shutil.copy2(project_cls_path, backup_path)

        try:
            shutil.copy2(self._reference_cls, project_cls_path)
        except Exception as e:
            return FixResult(
                success=False,
                message=f"Failed to copy CLS: {e}",
                backup_path=str(backup_path) if backup_path else None,
            )

        # Parse new version for reporting
        new_version = self._get_version(project_cls_path)

        return FixResult(
            success=True,
            message=f"CLS updated to v{new_version}",
            backup_path=str(backup_path) if backup_path else None,
            new_version=new_version,
        )

    def _get_version(self, cls_path: Path) -> Optional[str]:
        """Extract version from CLS file."""
        if not cls_path.exists():
            return None

        content = cls_path.read_text(encoding="utf-8")
        match = re.search(r"% Version (\d+\.\d+(?:\.\d+)?)", content)
        return match.group(1) if match else None

    def get_patterns(self) -> List[str]:
        """Return list of fix patterns."""
        return [
            "copy-reference-cls",
            "backup-existing-cls",
        ]

    def get_new_capabilities(self) -> List[str]:
        """
        Get list of new capabilities in reference CLS.

        Parses CHANGELOG from reference to extract new features.
        This info is passed to LLM skill for intelligent updates.
        """
        if not self._reference_cls.exists():
            return []

        content = self._reference_cls.read_text(encoding="utf-8")
        capabilities = []

        # Extract NEW: entries from changelog
        for match in re.finditer(r"% +- (NEW|FIXED|CRITICAL FIX): (.+)", content):
            capabilities.append(f"{match.group(1)}: {match.group(2)}")

        return capabilities[:20]  # Limit to recent 20 entries
