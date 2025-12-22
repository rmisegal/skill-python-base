"""
BC Configuration manager.

Thread-safe singleton for BC pipeline configuration,
following the same pattern as qa_engine.shared.config.ConfigManager.
"""

import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class BCConfigError(Exception):
    """BC configuration error."""

    pass


class BCConfigManager:
    """Thread-safe singleton for BC configuration management."""

    _instance: Optional["BCConfigManager"] = None
    _lock: threading.Lock = threading.Lock()

    # Default configuration matching bc_pipeline.json structure
    DEFAULT_CONFIG: Dict[str, Any] = {
        "version": "1.0.0",
        "orchestration": {
            "max_workers": 4,
            "batch_size": 50,
            "heartbeat_interval": 30,
            "stale_timeout": 120,
            "lock_timeout": 60,
        },
        "logging": {"level": "INFO", "json_format": True, "log_dir": "bc-logs"},
        "validators": {},
        "output_gate": {
            "require_zero_critical": True,
            "require_zero_warning": False,
            "max_retries_per_skill": 3,
        },
        "performance": {"parallel_validation": True, "cache_compiled_patterns": True},
    }

    def __new__(cls) -> "BCConfigManager":
        """Thread-safe singleton instantiation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._config: Dict[str, Any] = cls.DEFAULT_CONFIG.copy()
                    instance._config_path: Optional[Path] = None
                    instance._initialized = True
                    cls._instance = instance
        return cls._instance

    def load(self, config_path: str | Path) -> None:
        """Load configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            raise BCConfigError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            override = json.load(f)

        self._config = self._merge_config(self.DEFAULT_CONFIG.copy(), override)
        self._config_path = path

    def _merge_config(self, default: Dict, override: Dict) -> Dict:
        """Deep merge override into default config."""
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_validator_config(self, validator_name: str) -> Dict[str, Any]:
        """Get configuration for a specific validator."""
        return self.get(f"validators.{validator_name}", {})

    @property
    def config(self) -> Dict[str, Any]:
        """Get full config dictionary."""
        return self._config.copy()

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance for testing."""
        with cls._lock:
            cls._instance = None
