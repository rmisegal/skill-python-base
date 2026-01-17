"""
BC Dedup Detect Tool - Entry point for detection skill.

Provides detect and get_rules functions for Claude skill integration.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from bc_engine.dedup.detector import DedupDetector


def detect(
    project_path: str,
    config_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Detect duplicates across all chapters.

    Args:
        project_path: Root path of book project
        config_path: Path to bc_dedup.json

    Returns:
        List of issue dictionaries
    """
    detector = DedupDetector(
        project_path=project_path,
        config_path=config_path,
    )

    issues = detector.detect_project()

    return [
        {
            "rule": issue.rule,
            "file": issue.file,
            "line": issue.line,
            "content": issue.content[:100] if issue.content else "",
            "severity": issue.severity.value,
            "fix": issue.fix,
            "context": issue.context,
        }
        for issue in issues
    ]


def detect_file(
    content: str,
    file_path: str,
    config_path: Optional[str] = None,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Detect issues in a single file.

    Args:
        content: File content
        file_path: Path to file
        config_path: Path to bc_dedup.json
        offset: Line offset

    Returns:
        List of issue dictionaries
    """
    detector = DedupDetector(config_path=config_path)
    issues = detector.detect(content, file_path, offset)

    return [
        {
            "rule": issue.rule,
            "file": issue.file,
            "line": issue.line,
            "content": issue.content,
            "severity": issue.severity.value,
            "fix": issue.fix,
        }
        for issue in issues
    ]


def get_rules() -> Dict[str, str]:
    """
    Get supported detection rules.

    Returns:
        Dictionary of rule names to descriptions
    """
    return DedupDetector.RULES.copy()
