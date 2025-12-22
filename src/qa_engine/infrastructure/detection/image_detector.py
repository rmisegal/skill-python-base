"""
Image detector for source-level validation.

Implements FR-406 from PRD - detects image/figure issues in LaTeX source.
PDF-level validation (rendered images) requires LLM.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .image_rules import IMAGE_RULES


class ImageDetector(DetectorInterface):
    """
    Detects image issues at source level.

    Source-level detection (Python):
    - Missing image files
    - Wrong paths/extensions
    - Placeholder boxes
    - Empty figure environments

    PDF-level validation (LLM only):
    - Verify image renders in PDF
    - Detect empty boxes visually
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize detector with optional project root for file checks."""
        self._rules = IMAGE_RULES
        self._project_root = project_root or Path.cwd()

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """Detect image issues in content."""
        issues: List[Issue] = []
        lines = content.split("\n")
        source_dir = Path(file_path).parent if file_path else self._project_root

        for rule_name, rule_def in self._rules.items():
            # Handle document-context rules
            if rule_def.get("document_context"):
                issues.extend(self._check_document_rule(
                    rule_name, rule_def, content, file_path, offset
                ))
                continue

            # Line-by-line detection
            for line_num, line in enumerate(lines, start=1):
                if line.strip().startswith("%"):
                    continue

                issues.extend(self._check_line(
                    rule_name, rule_def, line, line_num + offset,
                    file_path, source_dir
                ))

        return issues

    def _check_document_rule(
        self, rule_name: str, rule_def: Dict,
        content: str, file_path: str, offset: int
    ) -> List[Issue]:
        """Check document-wide rules."""
        issues = []
        pattern = re.compile(rule_def["pattern"])
        neg_pattern = rule_def.get("negative_pattern")

        if pattern.search(content):
            if neg_pattern and not re.search(neg_pattern, content):
                issues.append(self._create_issue(
                    rule_name, rule_def, "Document", file_path, 1 + offset
                ))
        return issues

    def _check_line(
        self, rule_name: str, rule_def: Dict, line: str,
        line_num: int, file_path: str, source_dir: Path
    ) -> List[Issue]:
        """Check single line against rule."""
        issues = []
        pattern = re.compile(rule_def["pattern"])

        for match in pattern.finditer(line):
            # Context check
            ctx = rule_def.get("context_pattern")
            if ctx and not re.search(ctx, line):
                continue

            # File existence check
            if rule_def.get("check_file_exists"):
                img_path = match.group(1) if match.lastindex else match.group(0)
                if not self._image_exists(img_path, source_dir):
                    issues.append(self._create_issue(
                        rule_name, rule_def, img_path, file_path, line_num,
                        {"image_path": img_path}
                    ))
            else:
                content = match.group(1) if match.lastindex else match.group(0)
                issues.append(self._create_issue(
                    rule_name, rule_def, content, file_path, line_num
                ))

        return issues

    def _image_exists(self, img_path: str, source_dir: Path) -> bool:
        """Check if image file exists."""
        # Try common locations
        search_paths = [
            source_dir / img_path,
            source_dir / "images" / img_path,
            source_dir / "figures" / img_path,
            self._project_root / img_path,
            self._project_root / "images" / img_path,
        ]
        # Add common extensions if not specified
        if not Path(img_path).suffix:
            for ext in [".png", ".jpg", ".jpeg", ".pdf"]:
                search_paths.extend([p.with_suffix(ext) for p in search_paths])

        return any(p.exists() for p in search_paths)

    def _create_issue(
        self, rule_name: str, rule_def: Dict, content: str,
        file_path: str, line_num: int, context: Dict = None
    ) -> Issue:
        """Create issue from match."""
        return Issue(
            rule=rule_name,
            file=file_path,
            line=line_num,
            content=str(content)[:50],
            severity=rule_def["severity"],
            fix=rule_def.get("fix_template", ""),
            context=context or {},
        )

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
