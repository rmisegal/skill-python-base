"""
Configuration serializer for JSON and YAML files.

Provides serialization for configuration resources.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigSerializer:
    """Serializes configuration data to JSON and YAML files."""

    def serialize(
        self, data: Dict[str, Any], format_type: str = "json"
    ) -> str:
        """Serialize data to string in specified format."""
        if format_type == "json":
            return self.to_json(data)
        elif format_type in ("yaml", "yml"):
            return self.to_yaml(data)
        raise ValueError(f"Unsupported format: {format_type}")

    def to_json(
        self, data: Dict[str, Any], indent: int = 2, ensure_ascii: bool = False
    ) -> str:
        """Serialize data to JSON string."""
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

    def to_yaml(
        self, data: Dict[str, Any], default_flow_style: bool = False
    ) -> str:
        """Serialize data to YAML string."""
        return yaml.dump(
            data,
            default_flow_style=default_flow_style,
            allow_unicode=True,
            sort_keys=False,
        )

    def write(
        self,
        data: Dict[str, Any],
        file_path: Path,
        format_type: Optional[str] = None,
    ) -> Path:
        """Write data to file. Format determined by extension if not specified."""
        if format_type is None:
            format_type = self._get_format_from_path(file_path)

        content = self.serialize(data, format_type)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def _get_format_from_path(self, file_path: Path) -> str:
        """Determine format from file extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            return "json"
        elif suffix in (".yaml", ".yml"):
            return "yaml"
        raise ValueError(f"Cannot determine format from extension: {suffix}")

    def write_json(
        self, data: Dict[str, Any], file_path: Path, indent: int = 2
    ) -> Path:
        """Write data to JSON file."""
        content = self.to_json(data, indent=indent)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def write_yaml(
        self, data: Dict[str, Any], file_path: Path
    ) -> Path:
        """Write data to YAML file."""
        content = self.to_yaml(data)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def update_file(
        self, file_path: Path, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing file with new values (shallow merge)."""
        from ..parsers.config_parser import ConfigParser

        parser = ConfigParser()
        existing = parser.parse(file_path) if file_path.exists() else {}
        merged = {**existing, **updates}
        self.write(merged, file_path)
        return merged

    def deep_update_file(
        self, file_path: Path, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing file with deep merge."""
        from ..parsers.config_parser import ConfigParser

        parser = ConfigParser()
        existing = parser.parse(file_path) if file_path.exists() else {}
        merged = parser.merge_configs(existing, updates)
        self.write(merged, file_path)
        return merged

    def set_value_in_file(
        self, file_path: Path, key_path: str, value: Any
    ) -> Dict[str, Any]:
        """Set a single value in file using dot-notation path."""
        from ..parsers.config_parser import ConfigParser

        parser = ConfigParser()
        data = parser.parse(file_path) if file_path.exists() else {}
        parser.set_value(data, key_path, value)
        self.write(data, file_path)
        return data
