"""
Python tool for qa-bib-fix skill.

Creates missing .bib files and adds placeholder BibTeX entries.
"""

from typing import List, Dict, Any

from qa_engine.domain.models.issue import Issue, Severity
from qa_engine.infrastructure.fixing.bib_fixer import BibFixer


def fix(
    content: str,
    issues: List[Dict[str, Any]],
    file_path: str,
) -> Dict[str, Any]:
    """
    Fix bibliography issues.

    Args:
        content: LaTeX file content
        issues: List of issues from detector (as dictionaries)
        file_path: Path to the .tex file (needed to locate .bib files)

    Returns:
        Dictionary with fix results
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

    fixer = BibFixer()
    fixer.fix_with_context(content, issue_objects, file_path)

    # Count different fix types
    missing_files = sum(1 for i in issues if i["rule"] == "bib-missing-file")
    undefined_cites = sum(1 for i in issues if i["rule"] == "bib-undefined-cite")

    return {
        "bib_files_created": missing_files,
        "entries_added": undefined_cites,
        "fixes_applied": len(issues),
    }


def get_patterns() -> Dict[str, Dict[str, str]]:
    """Get supported fix patterns."""
    fixer = BibFixer()
    return fixer.get_patterns()


if __name__ == "__main__":
    # Example usage
    sample = r"\addbibresource{refs.bib}\cite{test2024}"
    issues = [
        {"rule": "bib-missing-file", "content": "refs.bib", "line": 1},
        {"rule": "bib-undefined-cite", "content": "test2024", "line": 1},
    ]
    result = fix(sample, issues, "/tmp/test.tex")
    print(f"Result: {result}")
