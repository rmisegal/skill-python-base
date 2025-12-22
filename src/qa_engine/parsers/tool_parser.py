"""
Tool parser for parsing tool.py files into Tool objects.

Extracts function definitions, imports, and docstrings from Python files.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.models import (
    Tool,
    ToolType,
    DetectorTool,
    FixerTool,
    RuleDefinition,
    PatternDefinition,
)
from ..domain.models.definitions import Severity


class ToolParser:
    """Parses tool.py files into Tool objects."""

    def parse(self, file_path: Path) -> Tool:
        """Parse a tool.py file into a Tool object."""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        imports = self._extract_imports(tree)
        functions = self._extract_functions(tree)
        docstring = self._extract_module_docstring(tree)
        tool_type = self._determine_tool_type(file_path, functions)

        return self._create_tool(
            file_path, tool_type, imports, functions, docstring, content
        )

    def _extract_imports(self, tree: ast.Module) -> List[str]:
        """Extract import statements from AST."""
        imports: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = ", ".join(a.name for a in node.names)
                imports.append(f"from {module} import {names}")
        return imports

    def _extract_functions(self, tree: ast.Module) -> Dict[str, Dict[str, Any]]:
        """Extract function definitions with docstrings and arguments."""
        functions: Dict[str, Dict[str, Any]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node) or ""
                args = [arg.arg for arg in node.args.args]
                functions[node.name] = {
                    "docstring": docstring,
                    "args": args,
                    "lineno": node.lineno,
                }
        return functions

    def _extract_module_docstring(self, tree: ast.Module) -> str:
        """Extract module-level docstring."""
        return ast.get_docstring(tree) or ""

    def _determine_tool_type(
        self, file_path: Path, functions: Dict[str, Dict[str, Any]]
    ) -> ToolType:
        """Determine tool type from file name or function names."""
        name = file_path.stem.lower()
        if "detect" in name or "run_detection" in functions:
            return ToolType.DETECTOR
        if "fix" in name or "apply_fix" in functions or "fix" in functions:
            return ToolType.FIXER
        return ToolType.UTILITY

    def _create_tool(
        self,
        path: Path,
        tool_type: ToolType,
        imports: List[str],
        functions: Dict[str, Dict[str, Any]],
        docstring: str,
        content: str,
    ) -> Tool:
        """Create appropriate Tool subclass from parsed data."""
        tool_id = path.stem
        name = path.stem.replace("_", "-")
        description = docstring.split("\n")[0] if docstring else ""

        base_kwargs = {
            "id": tool_id,
            "name": name,
            "description": description,
            "path": path,
            "tool_type": tool_type,
            "module_path": str(path),
            "imports": imports,
        }

        if tool_type == ToolType.DETECTOR:
            entry_func = "run_detection" if "run_detection" in functions else "detect"
            rules = self._extract_rules_from_content(content)
            return DetectorTool(
                **base_kwargs,
                entry_function=entry_func,
                rules=rules,
                detector_class=self._find_class_name(content, "Detector"),
            )
        elif tool_type == ToolType.FIXER:
            entry_func = "apply_fix" if "apply_fix" in functions else "fix"
            patterns = self._extract_patterns_from_content(content)
            return FixerTool(
                **base_kwargs,
                entry_function=entry_func,
                patterns=patterns,
                fixer_class=self._find_class_name(content, "Fixer"),
            )

        return Tool(**base_kwargs, entry_function="run")

    def _find_class_name(self, content: str, suffix: str) -> str:
        """Find class name ending with given suffix."""
        pattern = rf"class\s+(\w*{suffix})\s*[:\(]"
        match = re.search(pattern, content)
        return match.group(1) if match else ""

    def _extract_rules_from_content(
        self, content: str
    ) -> Dict[str, RuleDefinition]:
        """Extract rule definitions from tool content."""
        rules: Dict[str, RuleDefinition] = {}
        # Look for RULES dict or similar patterns
        pattern = r'["\'](\w+[-_]\w+)["\']:\s*\{[^}]*["\']pattern["\']:\s*r?["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content):
            rule_id = match.group(1)
            regex_pattern = match.group(2)
            rules[rule_id] = RuleDefinition(
                id=rule_id,
                description=f"Rule: {rule_id}",
                pattern=regex_pattern,
                severity=Severity.WARNING,
            )
        return rules

    def _extract_patterns_from_content(
        self, content: str
    ) -> Dict[str, PatternDefinition]:
        """Extract pattern definitions from tool content."""
        patterns: Dict[str, PatternDefinition] = {}
        # Look for PATTERNS dict or similar
        pattern = r'["\'](\w+[-_]\w+)["\']:\s*\{[^}]*["\']find["\']:\s*r?["\']([^"\']+)["\'][^}]*["\']replace["\']:\s*r?["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content):
            pat_id = match.group(1)
            find = match.group(2)
            replace = match.group(3)
            patterns[pat_id] = PatternDefinition(
                id=pat_id,
                description=f"Pattern: {pat_id}",
                find=find,
                replace=replace,
            )
        return patterns
