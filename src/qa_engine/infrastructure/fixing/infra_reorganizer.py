"""
Infrastructure reorganizer for project files.

Moves misplaced files to correct directories.
Aligned with qa-infra-reorganize skill.md patterns.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MoveRecord:
    """Record of a file move operation."""
    file: str
    from_path: str
    to_path: str
    reason: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class ReorganizeResult:
    """Result of reorganization operation."""
    directories_created: List[str] = field(default_factory=list)
    files_moved: int = 0
    moves: List[MoveRecord] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class InfraReorganizer:
    """Reorganizes project files to correct directories."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize reorganizer with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def reorganize(self, misplaced_files: List[Dict]) -> ReorganizeResult:
        """
        Reorganize files based on scan results.

        Args:
            misplaced_files: List of dicts with file, current, target keys

        Returns:
            ReorganizeResult with operation details
        """
        result = ReorganizeResult()

        # Step 1: Create missing directories
        self._create_directories(misplaced_files, result)

        # Step 2: Move files
        for file_info in misplaced_files:
            self._move_file(file_info, result)

        return result

    def _create_directories(
        self, misplaced_files: List[Dict], result: ReorganizeResult
    ) -> None:
        """Create missing target directories."""
        targets = set()
        for f in misplaced_files:
            target = f.get("target", "").rstrip("/")
            if target and target != ".":
                targets.add(target)

        for target in sorted(targets):
            target_path = self.project_root / target
            if not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)
                result.directories_created.append(target + "/")

    def _move_file(self, file_info: Dict, result: ReorganizeResult) -> None:
        """Move a single file to its target directory."""
        filename = file_info.get("file", "")
        current = file_info.get("current", "./").rstrip("/")
        target = file_info.get("target", "").rstrip("/")
        reason = file_info.get("reason", "File type rule")

        if not filename or not target or target == ".":
            return

        # Build paths
        if current == "." or current == "./":
            source_path = self.project_root / filename
        else:
            source_path = self.project_root / current / filename

        target_path = self.project_root / target / filename

        # Safety check: never delete, only move
        if not source_path.exists():
            result.errors.append(f"Source not found: {source_path}")
            return

        # Handle naming conflicts with timestamp
        if target_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = target_path.stem
            suffix = target_path.suffix
            target_path = target_path.parent / f"{stem}_{timestamp}{suffix}"

        try:
            # Move file (preserves permissions)
            shutil.move(str(source_path), str(target_path))

            result.files_moved += 1
            result.moves.append(MoveRecord(
                file=filename,
                from_path=current + "/" if current != "." else "./",
                to_path=target + "/",
                reason=reason,
            ))
        except Exception as e:
            result.errors.append(f"Failed to move {filename}: {str(e)}")

    def to_dict(self, result: ReorganizeResult) -> Dict:
        """Convert result to dictionary format."""
        return {
            "skill": "qa-infra-reorganize",
            "status": "DONE" if not result.errors else "PARTIAL",
            "directories_created": result.directories_created,
            "files_moved": result.files_moved,
            "moves": [
                {
                    "file": m.file,
                    "from": m.from_path,
                    "to": m.to_path,
                    "reason": m.reason,
                }
                for m in result.moves
            ],
            "errors": result.errors if result.errors else None,
        }

    def generate_log(self, result: ReorganizeResult) -> str:
        """Generate move log in skill.md format."""
        lines = ["# Reorganization Log", ""]
        for move in result.moves:
            lines.extend([
                f"[{move.timestamp}] {move.file}",
                f"  FROM: {move.from_path}{move.file}",
                f"  TO: {move.to_path}{move.file}",
                f"  REASON: {move.reason}",
                "",
            ])
        return "\n".join(lines)
