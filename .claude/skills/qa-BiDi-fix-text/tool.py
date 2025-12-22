"""
Python tool for qa-BiDi-fix-text skill.

Provides deterministic BiDi issue fixing for Hebrew-English LaTeX documents.
"""

from typing import List, Dict, Any

from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.infrastructure.fixing.bidi_fixer import BiDiFixer


def fix(content: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fix BiDi issues in content.

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

    fixer = BiDiFixer()
    fixed_content = fixer.fix(content, issue_objects)

    return {
        "fixed_content": fixed_content,
        "fixes_applied": len(issues),
    }


def get_patterns() -> List[str]:
    """Get list of supported fix patterns."""
    fixer = BiDiFixer()
    return fixer.get_patterns()


if __name__ == "__main__":
    # Example usage
    sample = "זה טקסט עם מספר 123 בעברית"
    issues = [{"rule": "bidi-numbers", "content": "123", "line": 1}]
    result = fix(sample, issues)
    print(f"Fixed content: {result['fixed_content']}")
