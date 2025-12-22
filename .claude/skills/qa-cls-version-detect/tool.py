"""
Python tool for qa-cls-version-detect skill.

Provides deterministic CLS version comparison.
Reference: C:\25D\CLS-examples\hebrew-academic-template.cls
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from qa_engine.infrastructure.detection.cls_detector import CLSDetector


def detect(content: str, file_path: str) -> List[Dict[str, Any]]:
    """
    Detect CLS version issues.

    Args:
        content: Project CLS file content
        file_path: Path to project's CLS file

    Returns:
        List of issues as dictionaries
    """
    detector = CLSDetector()
    issues = detector.detect(content, file_path)

    return [
        {
            "rule": issue.rule,
            "file_path": issue.file,
            "line": issue.line,
            "content": issue.content,
            "severity": issue.severity.value,
            "fix": issue.fix,
            "context": issue.context,
        }
        for issue in issues
    ]


def get_reference_info() -> Optional[Dict[str, str]]:
    """
    Get reference CLS version info.

    Returns:
        Dict with version, date, description, file_path
    """
    detector = CLSDetector()
    info = detector.get_reference_info()

    if info:
        return {
            "version": info.version,
            "date": info.date,
            "description": info.description,
            "file_path": info.file_path,
        }
    return None


def get_reference_content() -> Optional[str]:
    """
    Get full reference CLS content for LLM to learn.

    Returns:
        Full CLS file content as string
    """
    detector = CLSDetector()
    return detector.get_reference_content()


def get_rules() -> Dict[str, str]:
    """Get list of supported detection rules."""
    detector = CLSDetector()
    return detector.get_rules()


if __name__ == "__main__":
    # Example: Check reference info
    info = get_reference_info()
    if info:
        print(f"Reference CLS: v{info['version']} ({info['date']})")
        print(f"Description: {info['description']}")
