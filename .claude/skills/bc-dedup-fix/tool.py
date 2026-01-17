"""
BC Dedup Fix Tool - Entry point for fixer skill.

Provides fix and get_patterns functions for Claude skill integration.
"""

from typing import Any, Dict, List, Optional

from bc_engine.dedup.fixer import DedupFixer
from qa_engine.domain.models.issue import Issue, Severity


def fix(
    content: str,
    issues: List[Dict[str, Any]],
    config_path: Optional[str] = None,
) -> str:
    """
    Apply fixes to content.

    Args:
        content: Original LaTeX content
        issues: List of issue dictionaries
        config_path: Path to bc_dedup.json

    Returns:
        Fixed content string
    """
    fixer = DedupFixer(config_path=config_path)

    # Convert dicts to Issue objects
    issue_objects = [
        Issue(
            rule=i["rule"],
            file=i.get("file", ""),
            line=i.get("line", 0),
            content=i.get("content", ""),
            severity=Severity(i.get("severity", "WARNING")),
            fix=i.get("fix"),
            context={
                "source_chapter": i.get("source_chapter", 0),
                "target_chapter": i.get("target_chapter", 0),
            },
        )
        for i in issues
    ]

    return fixer.fix(content, issue_objects)


def fix_file(
    file_path: str,
    issues: List[Dict[str, Any]],
    config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Apply fixes to a file.

    Args:
        file_path: Path to file to fix
        issues: List of issue dictionaries
        config_path: Path to bc_dedup.json

    Returns:
        Result dictionary
    """
    from pathlib import Path

    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": "File not found"}

    content = path.read_text(encoding="utf-8")
    fixed = fix(content, issues, config_path)

    if fixed != content:
        path.write_text(fixed, encoding="utf-8")
        return {"success": True, "fixes_applied": len(issues)}

    return {"success": True, "fixes_applied": 0}


def get_patterns() -> Dict[str, Dict[str, str]]:
    """
    Get supported fix patterns.

    Returns:
        Dictionary of pattern definitions
    """
    return DedupFixer.PATTERNS.copy()
