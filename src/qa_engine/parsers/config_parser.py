"""
Configuration parser for JSON and YAML files.

Provides parsing and schema validation for configuration resources.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConfigParser:
    """Parses JSON and YAML configuration files."""

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a configuration file based on extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            return self.parse_json(file_path)
        elif suffix in (".yaml", ".yml"):
            return self.parse_yaml(file_path)
        raise ValueError(f"Unsupported file format: {suffix}")

    def parse_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse a JSON configuration file."""
        content = file_path.read_text(encoding="utf-8")
        return json.loads(content)

    def parse_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Parse a YAML configuration file."""
        content = file_path.read_text(encoding="utf-8")
        return yaml.safe_load(content) or {}

    def parse_string(self, content: str, format_type: str) -> Dict[str, Any]:
        """Parse configuration from string content."""
        if format_type == "json":
            return json.loads(content)
        elif format_type in ("yaml", "yml"):
            return yaml.safe_load(content) or {}
        raise ValueError(f"Unsupported format: {format_type}")

    def validate_schema(
        self, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[str]:
        """Validate data against JSON schema. Returns list of errors."""
        errors: List[str] = []

        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Check property types
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                prop_schema = properties[field]
                type_errors = self._validate_type(field, value, prop_schema)
                errors.extend(type_errors)

        return errors

    def _validate_type(
        self, field: str, value: Any, prop_schema: Dict[str, Any]
    ) -> List[str]:
        """Validate a single field's type."""
        errors: List[str] = []
        expected_type = prop_schema.get("type")

        if expected_type is None:
            return errors

        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        python_type = type_map.get(expected_type)
        if python_type and not isinstance(value, python_type):
            errors.append(
                f"Field '{field}' expected {expected_type}, got {type(value).__name__}"
            )

        # Check enum constraints
        if "enum" in prop_schema and value not in prop_schema["enum"]:
            errors.append(
                f"Field '{field}' must be one of: {prop_schema['enum']}"
            )

        # Check pattern constraints for strings
        if expected_type == "string" and "pattern" in prop_schema:
            import re
            if not re.match(prop_schema["pattern"], str(value)):
                errors.append(
                    f"Field '{field}' does not match pattern: {prop_schema['pattern']}"
                )

        return errors

    def merge_configs(
        self, base: Dict[str, Any], overlay: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries."""
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def get_value(
        self, data: Dict[str, Any], key_path: str, default: Any = None
    ) -> Any:
        """Get value using dot-notation path."""
        keys = key_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set_value(
        self, data: Dict[str, Any], key_path: str, value: Any
    ) -> Dict[str, Any]:
        """Set value using dot-notation path."""
        keys = key_path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        return data
