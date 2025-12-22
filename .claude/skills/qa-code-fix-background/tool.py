"""
Python tool for qa-code-fix-background skill.

Provides deterministic code block background overflow fixing.
"""

from typing import List, Dict, Any

from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.infrastructure.fixing.code_fixer import CodeFixer


def fix(content: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fix code block background overflow issues.

    Args:
        content: LaTeX file content
        issues: List of issues from detector (as dictionaries)

    Returns:
        Dictionary with fixed_content and fix count
    """
    # Convert dict issues to Issue objects
    issue_objects = [
        Issue(
            rule=i["rule"],
            file_path=i.get("file_path", ""),
            line=i.get("line", 0),
            content=i.get("content", ""),
            severity=Severity(i.get("severity", "warning")),
            fix=i.get("fix"),
        )
        for i in issues
    ]

    fixer = CodeFixer()
    fixed_content = fixer.fix(content, issue_objects)

    return {
        "fixed_content": fixed_content,
        "fixes_applied": len(issues),
    }


def get_patterns() -> List[str]:
    """Get list of supported fix patterns."""
    fixer = CodeFixer()
    return fixer.get_patterns()
