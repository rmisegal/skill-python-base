"""Project backup utility for full project backups."""
from __future__ import annotations
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class BackupResult:
    """Result of project backup operation."""

    success: bool
    name: str
    path: str
    size_bytes: int
    file_count: int
    original_file_count: int
    verified: bool
    message: str
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def size_mb(self) -> str:
        """Return human-readable size in MB."""
        return f"{self.size_bytes / (1024 * 1024):.2f} MB"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "skill": "qa-infra-backup",
            "status": "DONE" if self.success else "FAILED",
            "backup": {
                "name": self.name,
                "path": self.path,
                "size": self.size_mb,
                "files": self.file_count,
                "verified": self.verified,
            },
            "message": self.message,
            "error": self.error,
        }


class ProjectBackupUtility:
    """Creates complete project backups before reorganization."""

    def __init__(self, backup_parent_dir: Optional[Path] = None) -> None:
        """Initialize with optional custom backup location."""
        self._backup_parent = backup_parent_dir

    def create_backup(self, project_path: Path) -> BackupResult:
        """
        Create timestamped backup of entire project.

        Args:
            project_path: Path to project directory to backup

        Returns:
            BackupResult with operation status and details
        """
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            return self._error_result(f"Project path not found: {project_path}")
        if not project_path.is_dir():
            return self._error_result(f"Project path is not a directory: {project_path}")

        # Generate backup name and path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_parent = self._backup_parent or project_path.parent
        backup_path = backup_parent / backup_name

        # Count original files
        original_count = self._count_files(project_path)

        # Copy project to backup location
        try:
            shutil.copytree(
                project_path,
                backup_path,
                dirs_exist_ok=False,
                copy_function=shutil.copy2,  # Preserves timestamps
            )
        except Exception as e:
            return self._error_result(f"Backup copy failed: {e}")

        # Verify backup
        backup_count = self._count_files(backup_path)
        verified = backup_count == original_count
        backup_size = self._get_dir_size(backup_path)

        return BackupResult(
            success=verified,
            name=backup_name,
            path=str(backup_path),
            size_bytes=backup_size,
            file_count=backup_count,
            original_file_count=original_count,
            verified=verified,
            message=f"Backup created: {backup_name}" if verified else "Backup verification failed",
        )

    def _count_files(self, directory: Path) -> int:
        """Count all files in directory including hidden files."""
        count = 0
        for root, _, files in os.walk(directory):
            count += len(files)
        return count

    def _get_dir_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes."""
        total = 0
        for root, _, files in os.walk(directory):
            for f in files:
                fp = Path(root) / f
                if fp.exists():
                    total += fp.stat().st_size
        return total

    def _error_result(self, message: str) -> BackupResult:
        """Create error BackupResult."""
        return BackupResult(
            success=False,
            name="",
            path="",
            size_bytes=0,
            file_count=0,
            original_file_count=0,
            verified=False,
            message="Backup failed",
            error=message,
        )
