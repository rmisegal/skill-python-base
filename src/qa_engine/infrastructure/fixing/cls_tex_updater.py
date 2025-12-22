"""
CLS TeX file updater - updates .tex files to use new CLS capabilities.

Deterministic pattern replacements for common CLS upgrade scenarios.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

# Patterns to replace when upgrading CLS
CLS_UPGRADE_PATTERNS: Dict[str, Tuple[str, str]] = {
    # Hebrew in math - use \hebmath instead of manual \text
    "hebmath": (
        r"\\text\{([א-ת]+)\}",
        r"\\hebmath{\1}",
    ),
    # Hebrew footnote - use \hebfoot
    "hebfoot": (
        r"\\footnote\{\\texthebrew\{([^}]+)\}\}",
        r"\\hebfoot{\1}",
    ),
    # Hebrew title - use \hebtitle
    "hebtitle": (
        r"\\title\{\\texthebrew\{([^}]+)\}\}",
        r"\\hebtitle{\1}",
    ),
}

# Packages that CLS now provides (can be removed from preamble)
REDUNDANT_PACKAGES = [
    "biblatex",
    "csquotes",
    "geometry",
    "fancyhdr",
]


@dataclass
class TexUpdateResult:
    """Result of updating a .tex file."""
    file_path: str
    patterns_applied: List[str] = field(default_factory=list)
    packages_removed: List[str] = field(default_factory=list)
    documentclass_updated: bool = False


@dataclass
class CLSTexUpdateReport:
    """Report of all .tex file updates."""
    files_updated: int = 0
    total_changes: int = 0
    results: List[TexUpdateResult] = field(default_factory=list)


class CLSTexUpdater:
    """Updates .tex files to use new CLS capabilities."""

    def __init__(self, cls_name: str = "hebrew-academic-template") -> None:
        self._cls_name = cls_name

    def update_project(self, project_path: Path) -> CLSTexUpdateReport:
        """Update all .tex files in project."""
        report = CLSTexUpdateReport()
        tex_files = list(project_path.rglob("*.tex"))

        for tex_file in tex_files:
            result = self.update_file(tex_file)
            if result.patterns_applied or result.packages_removed or result.documentclass_updated:
                report.files_updated += 1
                report.total_changes += (
                    len(result.patterns_applied)
                    + len(result.packages_removed)
                    + (1 if result.documentclass_updated else 0)
                )
                report.results.append(result)

        return report

    def update_file(self, tex_file: Path) -> TexUpdateResult:
        """Update a single .tex file."""
        result = TexUpdateResult(file_path=str(tex_file))
        content = tex_file.read_text(encoding="utf-8")
        original = content

        # Update documentclass if needed
        content, updated = self._update_documentclass(content)
        result.documentclass_updated = updated

        # Apply pattern replacements
        for name, (find, replace) in CLS_UPGRADE_PATTERNS.items():
            if re.search(find, content):
                content = re.sub(find, replace, content)
                result.patterns_applied.append(name)

        # Remove redundant packages
        content, removed = self._remove_redundant_packages(content)
        result.packages_removed = removed

        # Write back if changed
        if content != original:
            tex_file.write_text(content, encoding="utf-8")

        return result

    def _update_documentclass(self, content: str) -> Tuple[str, bool]:
        """Update documentclass to use new CLS."""
        pattern = r"\\documentclass(\[[^\]]*\])?\{[^}]+\}"
        match = re.search(pattern, content)
        if not match or self._cls_name in match.group(0):
            return content, False

        options = match.group(1) or ""
        new_class = f"\\documentclass{options}{{{self._cls_name}}}"
        # Use lambda to avoid backslash interpretation issues
        content = re.sub(pattern, lambda m: new_class, content, count=1)
        return content, True

    def _remove_redundant_packages(self, content: str) -> Tuple[str, List[str]]:
        """Remove packages now provided by CLS."""
        removed = []
        for pkg in REDUNDANT_PACKAGES:
            pattern = rf"\\usepackage(\[[^\]]*\])?\{{{pkg}\}}\n?"
            if re.search(pattern, content):
                content = re.sub(pattern, "", content)
                removed.append(pkg)
        return content, removed

    def get_patterns(self) -> Dict[str, Tuple[str, str]]:
        """Return available upgrade patterns."""
        return CLS_UPGRADE_PATTERNS.copy()
