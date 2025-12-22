"""Image fixer for LaTeX documents."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List
from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue
from .image_patterns import IMAGE_PATTERNS


class ImageFixer(FixerInterface):
    """Fixes image-related issues in LaTeX source."""

    def __init__(self) -> None:
        self._patterns = IMAGE_PATTERNS

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content based on provided issues."""
        if not issues:
            return content
        issues_by_rule: Dict[str, List[Issue]] = {}
        for issue in issues:
            issues_by_rule.setdefault(issue.rule, []).append(issue)
        for pattern_def in self._patterns.values():
            for rule in pattern_def.get("applies_to", []):
                if rule in issues_by_rule:
                    content = self._apply_pattern(content, pattern_def)
        return content

    def _apply_pattern(self, content: str, pattern_def: Dict) -> str:
        find, replace = pattern_def["find"], pattern_def.get("replace")
        if pattern_def.get("replace_func") == "lowercase_filename":
            return self._lowercase_filenames(content, find)
        return re.sub(find, replace, content) if replace else content

    def _lowercase_filenames(self, content: str, pattern: str) -> str:
        def replacer(m: re.Match) -> str:
            return f"\\includegraphics{m.group(1) or ''}{{{m.group(2).lower()}}}"
        return re.sub(pattern, replacer, content)

    def add_graphicspath(self, content: str, paths: List[str] = None) -> str:
        """Add graphicspath command to preamble."""
        if "\\graphicspath" in content:
            return content
        paths = paths or ["images/", "../images/", "figures/"]
        paths_str = "".join(f"{{{p}}}" for p in paths)
        cmd = f"\\graphicspath{{{paths_str}}}\n"
        # Try inserting before \begin{document}
        if "\\begin{document}" in content:
            return re.sub(r"(\\begin\{document\})", cmd.replace("\\", "\\\\") + "\n" + r"\1", content)
        # For preamble files without \begin{document}, insert after last \usepackage or \usetikzlibrary
        for marker in [r"\\usetikzlibrary\{[^}]+\}", r"\\usepackage(\[[^\]]*\])?\{[^}]+\}"]:
            matches = list(re.finditer(marker, content))
            if matches:
                pos = matches[-1].end()
                return content[:pos] + "\n\n" + cmd + content[pos:]
        # Fallback: append at end
        return content.rstrip() + "\n\n" + cmd

    def fix_preamble_graphicspath(self, preamble_path: Path, project_root: Path = None) -> bool:
        """Auto-detect image dirs and add graphicspath to preamble file."""
        if not preamble_path.exists():
            return False
        content = preamble_path.read_text(encoding="utf-8")
        if "\\graphicspath" in content:
            return False
        paths = self._detect_image_paths(preamble_path, project_root)
        if not paths:
            return False
        fixed = self.add_graphicspath(content, paths)
        if fixed != content:
            preamble_path.write_text(fixed, encoding="utf-8")
            return True
        return False

    def _detect_image_paths(self, preamble_path: Path, project_root: Path = None) -> List[str]:
        """Scan project to find directories containing images."""
        root = project_root or preamble_path.parent.parent
        image_dirs = set()
        for ext in (".png", ".jpg", ".jpeg", ".pdf"):
            for img in root.rglob(f"*{ext}"):
                try:
                    rel = img.parent.relative_to(root)
                    image_dirs.add(str(rel).replace("\\", "/") + "/")
                    rel_up = Path("..") / rel
                    image_dirs.add(str(rel_up).replace("\\", "/") + "/")
                except ValueError:
                    pass
        priority = ["../images/figures/", "../images/", "images/figures/", "figures/", "images/"]
        result = [p for p in priority if p in image_dirs]
        result.extend(sorted(d for d in image_dirs if d not in result))
        return result[:6]

    def fix_image_path(self, content: str, old_path: str, new_path: str) -> str:
        """Replace specific image path."""
        pattern = rf"\\includegraphics(\[[^\]]*\])?\{{{re.escape(old_path)}\}}"
        return re.sub(pattern, rf"\\includegraphics\1{{{new_path}}}", content)

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern definitions."""
        return {name: {"find": p.get("find", ""), "replace": p.get("replace", ""),
                       "description": p.get("description", "")} for name, p in self._patterns.items()}
