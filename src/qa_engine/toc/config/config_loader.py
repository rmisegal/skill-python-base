"""
Configuration loader for TOC detection.

Loads all configuration from JSON files - no hardcoded data.
Singleton pattern ensures configs are loaded once.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Pattern


class TOCConfigLoader:
    """Loads and caches TOC detection configuration from JSON files."""

    _instance: Optional[TOCConfigLoader] = None
    _config_dir: Path = Path(__file__).parent

    def __new__(cls) -> TOCConfigLoader:
        """Singleton pattern - only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize configuration loader."""
        if self._initialized:
            return
        self._rules: Dict[str, Any] = {}
        self._patterns: Dict[str, Any] = {}
        self._fixer_mapping: Dict[str, Any] = {}
        self._compiled_patterns: Dict[str, Pattern] = {}
        self._load_all_configs()
        self._initialized = True

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON configuration file."""
        filepath = self._config_dir / filename
        if not filepath.exists():
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_all_configs(self) -> None:
        """Load all configuration files."""
        self._rules = self._load_json("toc_rules_config.json")
        self._patterns = self._load_json("toc_patterns.json")
        self._fixer_mapping = self._load_json("toc_fixer_mapping.json")
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        if "toc_entry_patterns" in self._patterns:
            for name, pattern in self._patterns["toc_entry_patterns"].items():
                self._compiled_patterns[name] = re.compile(pattern)
        if "numbering_patterns" in self._patterns:
            for name, pattern in self._patterns["numbering_patterns"].items():
                self._compiled_patterns[f"num_{name}"] = re.compile(pattern)

    def get_rules_by_category(self, category: str) -> Dict[str, Any]:
        """Get all rules for a specific category."""
        category_map = {
            "numbering": "numbering_rules",
            "bidi_number": "bidi_number_rules",
            "parenthetical": "parenthetical_rules",
            "bidi_text": "bidi_text_rules",
            "alignment": "alignment_rules",
            "structure": "structure_rules",
            "validation": "validation_rules",
        }
        key = category_map.get(category, category)
        return self._rules.get(key, {})

    def get_all_rules(self) -> Dict[str, Any]:
        """Get all rules combined."""
        all_rules = {}
        for key in self._rules:
            if key not in ("metadata", "severity_levels"):
                all_rules.update(self._rules[key])
        return all_rules

    def get_pattern(self, name: str) -> Optional[Pattern]:
        """Get a compiled regex pattern by name."""
        return self._compiled_patterns.get(name)

    def get_raw_pattern(self, category: str, name: str) -> Optional[str]:
        """Get a raw pattern string."""
        cat = self._patterns.get(category, {})
        return cat.get(name)

    def get_fixer_for_rule(self, rule_name: str) -> Dict[str, Any]:
        """Get fixer information for a specific rule."""
        mapping = self._fixer_mapping.get("rule_to_fixer", {})
        return mapping.get(rule_name, {"fixer": None, "skill": None, "manual": True})

    def get_severity_level(self, level: str) -> str:
        """Get severity level description."""
        levels = self._rules.get("severity_levels", {})
        return levels.get(level, "Unknown severity")

    def get_unicode_range(self, name: str) -> str:
        """Get a unicode range pattern."""
        ranges = self._patterns.get("unicode_ranges", {})
        return ranges.get(name, "")

    @property
    def total_rules(self) -> int:
        """Get total number of rules."""
        meta = self._rules.get("metadata", {})
        return meta.get("total_rules", 0)

    def reload(self) -> None:
        """Force reload all configurations."""
        self._compiled_patterns.clear()
        self._load_all_configs()
