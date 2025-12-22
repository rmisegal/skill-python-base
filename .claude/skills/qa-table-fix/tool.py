"""
Python tool for qa-table-fix skill.

Provides deterministic table fixing for Hebrew RTL LaTeX documents.
"""

from typing import List, Dict, Any

from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.infrastructure.fixing.table_fixer import TableFixer


def fix(content: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fix table issues in content.

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
            file=i.get("file", ""),
            line=i.get("line", 0),
            content=i.get("content", ""),
            severity=Severity(i.get("severity", "warning")),
            fix=i.get("fix"),
            context=i.get("context", {}),
        )
        for i in issues
    ]

    fixer = TableFixer()
    fixed_content = fixer.fix(content, issue_objects)

    return {
        "fixed_content": fixed_content,
        "fixes_applied": len(issues),
    }


def get_patterns() -> Dict[str, Dict[str, str]]:
    """Get supported fix patterns."""
    fixer = TableFixer()
    return fixer.get_patterns()


if __name__ == "__main__":
    # Example usage
    sample = r"\begin{tabular}{|c|c|}\hline\end{tabular}"
    issues = [{"rule": "table-plain-unstyled", "line": 1}]
    result = fix(sample, issues)
    print(f"Fixed content: {result['fixed_content']}")
