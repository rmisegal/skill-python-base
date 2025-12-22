"""
CLS sync detector for LaTeX projects.

Detects content inconsistencies between CLS file copies within a project.
Uses rules from cls_sync_rules.py - no hardcoded patterns.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from ...shared.logging import PrintManager
from .cls_sync_rules import CLS_CONFIG, CLS_SYNC_RULES


@dataclass
class CLSFileInfo:
    """Information about a CLS file."""

    path: Path
    size: int
    content: str


class CLSSyncDetector(DetectorInterface):
    """
    Detects CLS content mismatches within a project.

    Compares all CLS copies against master CLS file.
    Thread-safe, stateless detection.
    """

    def __init__(self) -> None:
        self._rules = CLS_SYNC_RULES
        self._config = CLS_CONFIG
        self._logger = PrintManager()
        self._master_content: Optional[str] = None

    def detect_project(self, project_root: str) -> List[Issue]:
        """Detect CLS sync issues across entire project."""
        root = Path(project_root)
        issues: List[Issue] = []

        cls_files = self._find_cls_files(root)
        if not cls_files:
            return issues

        master_info = cls_files.get(self._config["master_dir"])
        if not master_info:
            rule = self._rules["cls-sync-no-master"]
            issues.append(self._create_issue(
                "cls-sync-no-master", str(root / self._config["master_dir"]),
                1, rule["description"], rule
            ))
            return issues

        self._master_content = master_info.content

        for location, info in cls_files.items():
            if location == self._config["master_dir"]:
                continue
            issues.extend(self._compare_to_master(master_info, info, location))

        return issues

    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        """Detect sync issues for a single CLS file."""
        if self._master_content is None:
            return []

        issues: List[Issue] = []
        if content != self._master_content:
            diff_count = len(self._get_diff(self._master_content, content))
            rule = self._rules["cls-sync-content-mismatch"]
            issues.append(self._create_issue(
                "cls-sync-content-mismatch", file_path,
                self._find_first_diff_line(self._master_content, content),
                f"Content differs from master ({diff_count} diff lines)", rule,
                {"diff_lines": self._get_diff(self._master_content, content)[:10]}
            ))
        return issues

    def _compare_to_master(
        self, master: CLSFileInfo, other: CLSFileInfo, location: str
    ) -> List[Issue]:
        """Compare a CLS file against master."""
        issues: List[Issue] = []

        if other.content != master.content:
            diff_lines = self._get_diff(master.content, other.content)
            rule = self._rules["cls-sync-content-mismatch"]
            issues.append(self._create_issue(
                "cls-sync-content-mismatch", str(other.path),
                self._find_first_diff_line(master.content, other.content),
                f"Content differs from master ({len(diff_lines)} lines)", rule,
                {"location": location, "diff_lines": diff_lines[:10],
                 "master_size": master.size, "file_size": other.size}
            ))

        return issues

    def _find_cls_files(self, root: Path) -> Dict[str, CLSFileInfo]:
        """Find all CLS files in relevant directories."""
        cls_files: Dict[str, CLSFileInfo] = {}
        filename = self._config["filename"]

        for dir_name in [self._config["master_dir"], self._config["shared_dir"]]:
            cls_path = root / dir_name / filename
            if cls_path.exists():
                cls_files[dir_name] = self._read_cls_file(cls_path)

        for chapter_dir in sorted(root.glob(self._config["standalone_pattern"])):
            cls_path = chapter_dir / filename
            if cls_path.exists():
                cls_files[chapter_dir.name] = self._read_cls_file(cls_path)

        return cls_files

    def _read_cls_file(self, path: Path) -> CLSFileInfo:
        """Read a CLS file and return info."""
        content = path.read_text(encoding="utf-8")
        return CLSFileInfo(path=path, size=len(content.encode("utf-8")), content=content)

    def _create_issue(
        self, rule_name: str, file_path: str, line: int,
        content: str, rule: dict, context: dict = None
    ) -> Issue:
        """Create an Issue from rule definition."""
        return Issue(
            rule=rule_name, file=file_path, line=line, content=content,
            severity=rule["severity"], fix=rule["fix_template"],
            context=context or {}
        )

    def _get_diff(self, master: str, other: str) -> List[str]:
        """Get unified diff between master and other content."""
        return list(difflib.unified_diff(
            master.splitlines(keepends=True), other.splitlines(keepends=True),
            fromfile="master", tofile="file", lineterm=""
        ))

    def _find_first_diff_line(self, master: str, other: str) -> int:
        """Find line number of first difference."""
        for i, (m, o) in enumerate(
            zip(master.splitlines(), other.splitlines()), start=1
        ):
            if m != o:
                return i
        return max(len(master.splitlines()), len(other.splitlines()))

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
