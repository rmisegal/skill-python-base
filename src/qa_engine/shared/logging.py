"""
Logging module for QA Engine.

Provides PrintManager for console output and JsonLogger for
structured logging to files.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional, TextIO


class LogLevel(Enum):
    """Log severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class PrintManager:
    """
    Thread-safe singleton for console output.

    Provides consistent formatting and optional verbosity control.
    """

    _instance: Optional[PrintManager] = None
    _lock: Lock = Lock()

    def __new__(cls) -> PrintManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._verbose = False
        self._output: TextIO = sys.stdout
        self._initialized = True

    def set_verbose(self, verbose: bool) -> None:
        """Enable or disable verbose output."""
        self._verbose = verbose

    def info(self, message: str) -> None:
        """Print info message."""
        self._print(LogLevel.INFO, message)

    def debug(self, message: str) -> None:
        """Print debug message (only in verbose mode)."""
        if self._verbose:
            self._print(LogLevel.DEBUG, message)

    def warning(self, message: str) -> None:
        """Print warning message."""
        self._print(LogLevel.WARNING, message)

    def error(self, message: str) -> None:
        """Print error message."""
        self._print(LogLevel.ERROR, message)

    def _print(self, level: LogLevel, message: str) -> None:
        """Format and print message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with self._lock:
            print(f"[{timestamp}] {level.value}: {message}", file=self._output)

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None


class JsonLogger:
    """
    Thread-safe JSON file logger.

    Logs structured events in JSON format as per FR-301.
    """

    _instance: Optional[JsonLogger] = None
    _lock: Lock = Lock()

    def __new__(cls) -> JsonLogger:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._log_dir: Optional[Path] = None
        self._log_file: Optional[Path] = None
        self._min_level = LogLevel.INFO
        self._initialized = True

    def configure(
        self,
        log_dir: str | Path,
        min_level: str = "INFO",
    ) -> None:
        """Configure logger with directory and minimum level."""
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_file = self._log_dir / f"qa_{timestamp}.log"
        self._min_level = LogLevel[min_level.upper()]

    def log(
        self,
        level: LogLevel,
        event: str,
        agent_id: str = "system",
        **payload: Any,
    ) -> None:
        """Log structured event to file."""
        if not self._log_file:
            return

        if list(LogLevel).index(level) < list(LogLevel).index(self._min_level):
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "agent": agent_id,
            "event": event,
            "payload": payload,
        }

        with self._lock:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

    def log_event(self, event: str, agent_id: str, **data: Any) -> None:
        """Convenience method to log INFO event."""
        self.log(LogLevel.INFO, event, agent_id, **data)

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
