"""
Configuration management for deduplication engine.

Loads settings from JSON config file with no hardcoded values.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


class DedupConfigError(Exception):
    """Raised when configuration loading or validation fails."""


class DedupConfig:
    """
    Thread-safe configuration manager for dedup engine.

    All settings loaded from external JSON config file.
    """

    _instance: Optional[DedupConfig] = None
    _lock: Lock = Lock()

    def __new__(cls) -> DedupConfig:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._initialized = True

    def load(self, config_path: str | Path) -> None:
        """Load configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            raise DedupConfigError(f"Config file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            self._config_path = path
            self._validate()
        except json.JSONDecodeError as e:
            raise DedupConfigError(f"Invalid JSON in config: {e}")

    def _validate(self) -> None:
        """Validate required configuration keys exist."""
        required = ["chunk_size", "similarity_threshold", "max_workers"]
        missing = [k for k in required if k not in self._config]
        if missing:
            raise DedupConfigError(f"Missing required config keys: {missing}")

    @property
    def chunk_size(self) -> int:
        """Lines per chunk for processing."""
        return self._config.get("chunk_size", 50)

    @property
    def similarity_threshold(self) -> float:
        """Minimum similarity score to consider duplicate (0.0-1.0)."""
        return self._config.get("similarity_threshold", 0.75)

    @property
    def max_workers(self) -> int:
        """Maximum parallel workers for comparison."""
        return self._config.get("max_workers", 4)

    @property
    def chapter_pattern(self) -> str:
        """Glob pattern for chapter files."""
        return self._config.get("chapter_pattern", "chapters/chapter*.tex")

    @property
    def min_chunk_words(self) -> int:
        """Minimum words for a chunk to be compared."""
        return self._config.get("min_chunk_words", 20)

    @property
    def llm_prompt_template(self) -> str:
        """Template for LLM semantic comparison."""
        return self._config.get("llm_prompt_template", "")

    @property
    def rewrite_prompt_template(self) -> str:
        """Template for LLM rewrite with chapterref."""
        return self._config.get("rewrite_prompt_template", "")

    @property
    def excluded_environments(self) -> List[str]:
        """LaTeX environments to exclude from comparison."""
        return self._config.get("excluded_environments", [])

    @property
    def balance_threshold(self) -> float:
        """Max chapter size ratio for balance check."""
        return self._config.get("balance_threshold", 2.0)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
