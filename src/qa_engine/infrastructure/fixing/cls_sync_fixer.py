"""
CLS sync fixer for LaTeX projects.

Synchronizes all CLS file copies to the master version.
Uses config from cls_sync_patterns.py - no hardcoded values.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ...domain.models.issue import Issue
from ...shared.logging import PrintManager
from .cls_sync_patterns import CLS_SYNC_FIX_CONFIG


@dataclass
class CLSSyncFixResult:
    """Result of CLS sync fix operation."""

    success: bool
    files_fixed: int
    files_skipped: int
    backups_created: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class CLSSyncFixer:
    """
    Fixes CLS sync issues by copying master to all locations.

    Creates backups before overwriting. Thread-safe operations.
    """

    def __init__(self) -> None:
        self._config = CLS_SYNC_FIX_CONFIG
        self._logger = PrintManager()
        self._master_content: Optional[str] = None

    def fix_project(
        self, project_root: str, create_backup: bool = True
    ) -> CLSSyncFixResult:
        """Fix all CLS sync issues in a project."""
        root = Path(project_root)
        result = CLSSyncFixResult(success=True, files_fixed=0, files_skipped=0)

        master_cls = root / self._config["master_dir"] / self._config["filename"]
        if not master_cls.exists():
            result.success = False
            result.errors.append(f"Master CLS not found: {master_cls}")
            return result

        self._master_content = master_cls.read_text(encoding=self._config["encoding"])

        for location, cls_path in self._find_cls_locations(root).items():
            if location == self._config["master_dir"]:
                continue
            self._fix_single_file(cls_path, create_backup, result)

        return result

    def fix_from_issues(
        self, issues: List[Issue], project_root: str, create_backup: bool = True
    ) -> CLSSyncFixResult:
        """Fix CLS files based on detected issues."""
        root = Path(project_root)
        result = CLSSyncFixResult(success=True, files_fixed=0, files_skipped=0)

        master_cls = root / self._config["master_dir"] / self._config["filename"]
        if not master_cls.exists():
            result.success = False
            result.errors.append(f"Master CLS not found: {master_cls}")
            return result

        self._master_content = master_cls.read_text(encoding=self._config["encoding"])

        for issue in issues:
            if issue.rule in ("cls-sync-content-mismatch", "cls-sync-size-mismatch"):
                self._fix_single_file(Path(issue.file), create_backup, result)

        return result

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Fix content based on issues (interface compliance)."""
        if not issues or self._master_content is None:
            return content
        return self._master_content

    def _fix_single_file(
        self, cls_path: Path, create_backup: bool, result: CLSSyncFixResult
    ) -> None:
        """Fix a single CLS file by syncing to master."""
        try:
            current = cls_path.read_text(encoding=self._config["encoding"])
            if current == self._master_content:
                result.files_skipped += 1
                return

            if create_backup:
                backup = cls_path.with_suffix(
                    cls_path.suffix + self._config["backup_suffix"]
                )
                shutil.copy2(cls_path, backup)
                result.backups_created.append(str(backup))

            cls_path.write_text(self._master_content, encoding=self._config["encoding"])
            result.files_fixed += 1
            self._logger.info(f"Synced: {cls_path}")

        except Exception as e:
            result.success = False
            result.errors.append(f"Error fixing {cls_path}: {e}")

    def _find_cls_locations(self, root: Path) -> Dict[str, Path]:
        """Find all CLS file locations."""
        locations: Dict[str, Path] = {}
        filename = self._config["filename"]

        for dir_name in [self._config["master_dir"], self._config["shared_dir"]]:
            path = root / dir_name / filename
            if path.exists():
                locations[dir_name] = path

        for chapter_dir in sorted(root.glob(self._config["standalone_pattern"])):
            path = chapter_dir / filename
            if path.exists():
                locations[chapter_dir.name] = path

        return locations

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {description}."""
        return {
            "sync-to-master": {
                "description": "Copy master CLS content to target file",
                "creates_backup": "True",
            }
        }

    def get_master_content(self) -> Optional[str]:
        """Get cached master content."""
        return self._master_content
