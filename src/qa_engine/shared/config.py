"""
Configuration management module.

Provides singleton ConfigManager for loading and accessing
QA system configuration from JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional


class ConfigError(Exception):
    """Raised when configuration loading or validation fails."""


class ConfigManager:
    """
    Thread-safe singleton for configuration management.

    Loads configuration from JSON file and provides typed access.
    """

    _instance: Optional[ConfigManager] = None
    _lock: Lock = Lock()

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "enabled_families": ["BiDi", "code", "table", "typeset"],
        "parallel_families": True,
        "batch_processing": {
            "enabled": True,
            "batch_size": 50,
            "chunk_lines": 1000,
            "max_workers": 4,
        },
        "coordination": {
            "heartbeat_interval": 30,
            "stale_timeout": 120,
            "lock_timeout": 60,
        },
        "logging": {
            "level": "INFO",
            "json_format": True,
            "log_dir": "qa-logs",
        },
    }

    def __new__(cls) -> ConfigManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._config_path: Optional[Path] = None
        self._initialized = True

    def load(self, config_path: str | Path) -> None:
        """Load configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self._config = self._merge_config(self.DEFAULT_CONFIG, loaded)
            self._config_path = path
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}")

    def _merge_config(
        self, default: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge override into default config."""
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict):
                if isinstance(value, dict):
                    result[key] = self._merge_config(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = self.get(key, default)
        return int(value) if value is not None else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(key, default)
        return bool(value) if value is not None else default

    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value."""
        value = self.get(key, default)
        return str(value) if value is not None else default

    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config.copy()

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
