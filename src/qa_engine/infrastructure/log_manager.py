"""
Log Manager for QA execution logs.

Handles versioned log files with FIFO rotation (max 10 files).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

# Log file pattern: qa-execution-{version}.log
LOG_PATTERN = re.compile(r"qa-execution-(\d+)\.log$")
MAX_LOG_FILES = 10
LOG_PREFIX = "qa-execution"
LOG_EXTENSION = ".log"


class LogManager:
    """Manages QA execution log files with FIFO rotation."""

    def __init__(self, log_dir: Path):
        """Initialize with log directory."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def get_existing_logs(self) -> List[Path]:
        """Get list of existing log files sorted by version (oldest first)."""
        logs = []
        for f in self.log_dir.iterdir():
            if f.is_file() and LOG_PATTERN.match(f.name):
                logs.append(f)
        return sorted(logs, key=lambda p: self._get_version(p))

    def _get_version(self, path: Path) -> int:
        """Extract version number from log filename."""
        match = LOG_PATTERN.match(path.name)
        return int(match.group(1)) if match else 0

    def get_next_version(self) -> int:
        """Get next version number for new log file."""
        logs = self.get_existing_logs()
        if not logs:
            return 1
        return self._get_version(logs[-1]) + 1

    def get_log_path(self, version: Optional[int] = None) -> Path:
        """Get path for log file with given or next version."""
        ver = version if version is not None else self.get_next_version()
        return self.log_dir / f"{LOG_PREFIX}-{ver}{LOG_EXTENSION}"

    def rotate_logs(self) -> List[Path]:
        """
        Remove oldest logs if exceeding MAX_LOG_FILES.

        Returns list of deleted log paths.
        """
        logs = self.get_existing_logs()
        deleted = []
        while len(logs) >= MAX_LOG_FILES:
            oldest = logs.pop(0)
            oldest.unlink()
            deleted.append(oldest)
        return deleted

    def clear_logs(self) -> int:
        """
        Delete all log files.

        Returns count of deleted files.
        """
        logs = self.get_existing_logs()
        for log in logs:
            log.unlink()
        return len(logs)

    def save_with_rotation(self, content: str) -> Path:
        """
        Save content to new versioned log file with FIFO rotation.

        Returns path to saved log file.
        """
        self.rotate_logs()
        version = self.get_next_version()
        log_path = self.get_log_path(version)
        log_path.write_text(content, encoding="utf-8")
        return log_path

    def get_latest_log(self) -> Optional[Path]:
        """Get path to most recent log file, or None if no logs exist."""
        logs = self.get_existing_logs()
        return logs[-1] if logs else None

    def get_log_count(self) -> int:
        """Get count of existing log files."""
        return len(self.get_existing_logs())
