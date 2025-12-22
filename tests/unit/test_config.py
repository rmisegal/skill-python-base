"""
Tests for shared/config module.
"""

import json
import tempfile
from pathlib import Path

import pytest
from qa_engine.shared.config import ConfigError, ConfigManager


class TestConfigManager:
    """Tests for ConfigManager singleton."""

    def setup_method(self):
        """Reset singleton before each test."""
        ConfigManager.reset()

    def test_singleton_pattern(self):
        """Test that ConfigManager is a singleton."""
        cm1 = ConfigManager()
        cm2 = ConfigManager()
        assert cm1 is cm2

    def test_default_config(self):
        """Test default configuration values."""
        cm = ConfigManager()
        assert cm.get("version") == "1.0.0"
        assert "BiDi" in cm.get("enabled_families")

    def test_get_with_default(self):
        """Test get with default value."""
        cm = ConfigManager()
        assert cm.get("nonexistent", "default") == "default"

    def test_get_dot_notation(self):
        """Test get with dot notation for nested values."""
        cm = ConfigManager()
        assert cm.get("batch_processing.enabled") is True
        assert cm.get("batch_processing.chunk_lines") == 1000

    def test_get_int(self):
        """Test get_int method."""
        cm = ConfigManager()
        assert cm.get_int("batch_processing.max_workers") == 4
        assert cm.get_int("nonexistent", 99) == 99

    def test_get_bool(self):
        """Test get_bool method."""
        cm = ConfigManager()
        assert cm.get_bool("parallel_families") is True
        assert cm.get_bool("nonexistent", False) is False

    def test_get_str(self):
        """Test get_str method."""
        cm = ConfigManager()
        assert cm.get_str("logging.level") == "INFO"
        assert cm.get_str("nonexistent", "default") == "default"

    def test_load_valid_config(self):
        """Test loading valid config file."""
        config = {
            "version": "2.0.0",
            "enabled_families": ["BiDi"],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            config_path = f.name

        try:
            cm = ConfigManager()
            cm.load(config_path)
            assert cm.get("version") == "2.0.0"
            # Default values should be preserved
            assert cm.get("batch_processing.enabled") is True
        finally:
            Path(config_path).unlink()

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises ConfigError."""
        cm = ConfigManager()
        with pytest.raises(ConfigError):
            cm.load("/nonexistent/path/config.json")

    def test_load_invalid_json(self):
        """Test loading invalid JSON raises ConfigError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("invalid json {")
            config_path = f.name

        try:
            cm = ConfigManager()
            with pytest.raises(ConfigError):
                cm.load(config_path)
        finally:
            Path(config_path).unlink()

    def test_config_property(self):
        """Test config property returns copy."""
        cm = ConfigManager()
        config = cm.config
        config["test"] = "modified"
        assert "test" not in cm.config
