"""
Unit tests for DedupConfig.

Tests configuration loading and validation.
"""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from bc_engine.dedup.config import DedupConfig, DedupConfigError


class TestDedupConfig:
    """Tests for DedupConfig class."""

    def setup_method(self):
        """Reset singleton before each test."""
        DedupConfig.reset()

    def test_singleton_pattern(self):
        """Config should be a singleton."""
        config1 = DedupConfig()
        config2 = DedupConfig()
        assert config1 is config2

    def test_load_valid_config(self, tmp_path):
        """Should load valid JSON config."""
        config_data = {
            "chunk_size": 100,
            "similarity_threshold": 0.8,
            "max_workers": 8,
            "chapter_pattern": "ch/*.tex",
        }
        config_file = tmp_path / "test_config.json"
        config_file.write_text(json.dumps(config_data))

        config = DedupConfig()
        config.load(config_file)

        assert config.chunk_size == 100
        assert config.similarity_threshold == 0.8
        assert config.max_workers == 8
        assert config.chapter_pattern == "ch/*.tex"

    def test_load_missing_file(self):
        """Should raise error for missing file."""
        config = DedupConfig()
        with pytest.raises(DedupConfigError, match="not found"):
            config.load("/nonexistent/path.json")

    def test_load_invalid_json(self, tmp_path):
        """Should raise error for invalid JSON."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{ invalid json }")

        config = DedupConfig()
        with pytest.raises(DedupConfigError, match="Invalid JSON"):
            config.load(config_file)

    def test_missing_required_keys(self, tmp_path):
        """Should raise error for missing required keys."""
        config_data = {"chunk_size": 50}  # Missing others
        config_file = tmp_path / "partial.json"
        config_file.write_text(json.dumps(config_data))

        config = DedupConfig()
        with pytest.raises(DedupConfigError, match="Missing required"):
            config.load(config_file)

    def test_default_values(self, tmp_path):
        """Should use defaults for optional keys."""
        config_data = {
            "chunk_size": 50,
            "similarity_threshold": 0.75,
            "max_workers": 4,
        }
        config_file = tmp_path / "minimal.json"
        config_file.write_text(json.dumps(config_data))

        config = DedupConfig()
        config.load(config_file)

        assert config.min_chunk_words == 20  # Default
        assert config.balance_threshold == 2.0  # Default

    def test_get_method(self, tmp_path):
        """Should get arbitrary config values."""
        config_data = {
            "chunk_size": 50,
            "similarity_threshold": 0.75,
            "max_workers": 4,
            "custom_key": "custom_value",
        }
        config_file = tmp_path / "custom.json"
        config_file.write_text(json.dumps(config_data))

        config = DedupConfig()
        config.load(config_file)

        assert config.get("custom_key") == "custom_value"
        assert config.get("missing_key", "default") == "default"
