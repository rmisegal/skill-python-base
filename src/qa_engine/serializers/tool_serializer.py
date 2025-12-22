"""
Tool serializer for writing Tool objects to tool.py files.

Generates Python source code with proper structure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.models import Tool, DetectorTool, FixerTool, ToolType


class ToolSerializer:
    """Serializes Tool objects to tool.py files."""

    def serialize(self, tool: Tool) -> str:
        """Serialize a Tool object to Python source code."""
        parts: List[str] = []

        # Module docstring
        parts.append(self._generate_docstring(tool))

        # Imports
        parts.append(self._generate_imports(tool))

        # Type-specific content
        if isinstance(tool, DetectorTool):
            parts.append(self._generate_detector_content(tool))
        elif isinstance(tool, FixerTool):
            parts.append(self._generate_fixer_content(tool))
        else:
            parts.append(self._generate_utility_content(tool))

        return "\n\n".join(filter(None, parts)) + "\n"

    def write(self, tool: Tool, file_path: Optional[Path] = None) -> Path:
        """Write tool to file. Uses tool.path if file_path not provided."""
        path = file_path or tool.path
        if not path:
            raise ValueError("No file path specified for tool")
        content = self.serialize(tool)
        path.write_text(content, encoding="utf-8")
        return path

    def _generate_docstring(self, tool: Tool) -> str:
        """Generate module docstring."""
        return f'"""\n{tool.name}: {tool.description}\n\nAuto-generated tool module.\n"""'

    def _generate_imports(self, tool: Tool) -> str:
        """Generate import statements."""
        base_imports = [
            "from __future__ import annotations", "",
            "import re", "from pathlib import Path",
            "from typing import Any, Dict, List, Optional",
        ]
        if isinstance(tool, DetectorTool):
            base_imports.append("from qa_engine.domain.models import Issue, Severity")
        elif isinstance(tool, FixerTool):
            base_imports.append("from qa_engine.domain.models import Issue")
        for imp in tool.imports:  # Add custom imports
            if imp not in base_imports:
                base_imports.append(imp)
        return "\n".join(base_imports)

    def _generate_detector_content(self, tool: DetectorTool) -> str:
        """Generate detector tool content."""
        lines: List[str] = []

        # Rules dictionary
        if tool.rules:
            lines.append("# Detection rules")
            lines.append("RULES = {")
            for rule_id, rule in tool.rules.items():
                lines.append(f'    "{rule_id}": {{')
                lines.append(f'        "pattern": r"{rule.pattern}",')
                lines.append(f'        "description": "{rule.description}",')
                lines.append(f'        "severity": "{rule.severity.value}",')
                lines.append("    },")
            lines.append("}")
            lines.append("")

        # Detector class
        class_name = tool.detector_class or "Detector"
        lines.extend([
            f"class {class_name}:",
            '    """Detection tool implementation."""',
            "",
            "    def __init__(self, rules: Dict[str, Any] = None):",
            "        self.rules = rules or RULES",
            "",
            "    def run_detection(",
            "        self, content: str, file_path: str",
            "    ) -> List[Issue]:",
            '        """Run detection on content."""',
            "        issues: List[Issue] = []",
            "        lines = content.splitlines()",
            "",
            "        for rule_id, rule in self.rules.items():",
            "            pattern = re.compile(rule['pattern'])",
            "            for i, line in enumerate(lines, 1):",
            "                if pattern.search(line):",
            "                    issues.append(Issue(",
            "                        rule_id=rule_id,",
            "                        file_path=file_path,",
            "                        line_number=i,",
            "                        message=rule['description'],",
            "                        severity=Severity(rule['severity']),",
            "                    ))",
            "",
            "        return issues",
        ])

        # Entry function
        lines.extend([
            "",
            "",
            "def run_detection(content: str, file_path: str) -> List[Issue]:",
            '    """Entry point for detection."""',
            f"    detector = {class_name}()",
            "    return detector.run_detection(content, file_path)",
        ])

        return "\n".join(lines)

    def _generate_fixer_content(self, tool: FixerTool) -> str:
        """Generate fixer tool content."""
        lines: List[str] = []

        # Patterns dictionary
        if tool.patterns:
            lines.append("# Fix patterns")
            lines.append("PATTERNS = {")
            for pat_id, pattern in tool.patterns.items():
                lines.append(f'    "{pat_id}": {{')
                lines.append(f'        "find": r"{pattern.find}",')
                lines.append(f'        "replace": r"{pattern.replace}",')
                lines.append(f'        "description": "{pattern.description}",')
                lines.append("    },")
            lines.append("}")
            lines.append("")

        # Fixer class
        class_name = tool.fixer_class or "Fixer"
        lines.extend([
            f"class {class_name}:",
            '    """Fixer tool implementation."""',
            "",
            "    def __init__(self, patterns: Dict[str, Any] = None):",
            "        self.patterns = patterns or PATTERNS",
            "",
            "    def fix(self, content: str, issues: List[Issue] = None) -> str:",
            '        """Apply fixes to content."""',
            "        result = content",
            "        for pat_id, pattern in self.patterns.items():",
            "            result = re.sub(",
            "                pattern['find'], pattern['replace'], result",
            "            )",
            "        return result",
        ])

        # Entry function
        lines.extend([
            "",
            "",
            "def fix(content: str, issues: List[Issue] = None) -> str:",
            '    """Entry point for fixing."""',
            f"    fixer = {class_name}()",
            "    return fixer.fix(content, issues)",
        ])

        return "\n".join(lines)

    def _generate_utility_content(self, tool: Tool) -> str:
        """Generate utility tool content."""
        return f'''
def run(**kwargs) -> Any:
    """Entry point for {tool.name}."""
    # TODO: Implement tool logic
    return {{"status": "success"}}
'''
