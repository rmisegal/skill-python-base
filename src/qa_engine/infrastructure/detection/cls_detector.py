r"""
CLS (LaTeX class file) version detector.

Compares project CLS version against reference at C:\25D\CLS-examples.
Deterministic Python tool - no LLM needed for version comparison.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue, Severity

# Reference CLS location
REFERENCE_CLS_DIR = Path(r"C:\25D\CLS-examples")
REFERENCE_CLS_FILE = REFERENCE_CLS_DIR / "hebrew-academic-template.cls"


@dataclass
class CLSVersionInfo:
    """CLS version information."""

    version: str
    date: str
    description: str
    file_path: str

    def __str__(self) -> str:
        return f"v{self.version} ({self.date}) - {self.description}"


class CLSDetector(DetectorInterface):
    """
    Detects CLS version mismatches.

    Compares project's CLS file against reference directory.
    This is a blocking check - runs before other QA families.
    """

    def __init__(self, reference_cls: Optional[Path] = None) -> None:
        self._reference_cls = reference_cls or REFERENCE_CLS_FILE

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """
        Detect CLS version issues.

        Args:
            content: CLS file content from project
            file_path: Path to project's CLS file
            offset: Not used for CLS detection

        Returns:
            List of issues (empty if versions match)
        """
        issues: List[Issue] = []

        project_info = self._parse_version(content, file_path)
        if not project_info:
            issues.append(
                Issue(
                    rule="cls-version-parse-error",
                    file=file_path,
                    line=1,
                    content="Unable to parse CLS version",
                    severity=Severity.CRITICAL,
                    fix="Check CLS file format - version line missing",
                )
            )
            return issues

        reference_info = self._get_reference_version()
        if not reference_info:
            issues.append(
                Issue(
                    rule="cls-reference-missing",
                    file=str(self._reference_cls),
                    line=1,
                    content="Reference CLS file not found",
                    severity=Severity.CRITICAL,
                    fix=f"Ensure {self._reference_cls} exists",
                )
            )
            return issues

        if project_info.version != reference_info.version:
            issues.append(
                Issue(
                    rule="cls-version-mismatch",
                    file=file_path,
                    line=2,
                    content=f"Project: v{project_info.version}, Reference: v{reference_info.version}",
                    severity=Severity.WARNING,
                    fix=f"Update to {reference_info}",
                    context={
                        "project_version": project_info.version,
                        "reference_version": reference_info.version,
                        "reference_date": reference_info.date,
                        "reference_description": reference_info.description,
                        "reference_path": str(self._reference_cls),
                    },
                )
            )

        return issues

    def _parse_version(self, content: str, file_path: str) -> Optional[CLSVersionInfo]:
        """Parse version info from CLS content."""
        pattern = r"% Version (\d+\.\d+(?:\.\d+)?) - (.+)"
        date_pattern = r"% Date: (\d{4}-\d{2}-\d{2})"

        version_match = re.search(pattern, content)
        date_match = re.search(date_pattern, content)

        if not version_match:
            return None

        return CLSVersionInfo(
            version=version_match.group(1),
            date=date_match.group(1) if date_match else "unknown",
            description=version_match.group(2),
            file_path=file_path,
        )

    def _get_reference_version(self) -> Optional[CLSVersionInfo]:
        """Get version info from reference CLS file."""
        if not self._reference_cls.exists():
            return None

        content = self._reference_cls.read_text(encoding="utf-8")
        return self._parse_version(content, str(self._reference_cls))

    def get_rules(self) -> dict:
        """Return dict of rule_name -> description."""
        return {
            "cls-version-mismatch": "Project CLS version differs from reference",
            "cls-version-parse-error": "Unable to parse CLS version header",
            "cls-reference-missing": "Reference CLS file not found",
        }

    def get_reference_info(self) -> Optional[CLSVersionInfo]:
        """Get reference CLS version info (for LLM skill to read)."""
        return self._get_reference_version()

    def get_reference_content(self) -> Optional[str]:
        """Get full reference CLS content (for LLM to learn)."""
        if not self._reference_cls.exists():
            return None
        return self._reference_cls.read_text(encoding="utf-8")
