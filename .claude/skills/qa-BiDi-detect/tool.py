"""
Python tool for qa-BiDi-detect skill.

Provides deterministic BiDi issue detection for Hebrew-English LaTeX documents.
"""

from pathlib import Path
from typing import List, Dict, Any

from qa_engine.infrastructure.detection.bidi_detector import BiDiDetector


def detect(content: str, file_path: str, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Detect BiDi issues in content.

    Args:
        content: LaTeX file content
        file_path: Path to the file (for reporting)
        offset: Line number offset for chunked processing

    Returns:
        List of issues as dictionaries
    """
    detector = BiDiDetector()
    issues = detector.detect(content, file_path, offset)

    return [
        {
            "rule": issue.rule,
            "file_path": issue.file_path,
            "line": issue.line,
            "content": issue.content,
            "severity": issue.severity.value,
            "fix": issue.fix,
        }
        for issue in issues
    ]


def get_rules() -> List[str]:
    """Get list of supported detection rules."""
    detector = BiDiDetector()
    return detector.get_rules()


if __name__ == "__main__":
    # Example usage
    sample = "זה טקסט עם מספר 123 בעברית"
    issues = detect(sample, "test.tex")
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  - {issue['rule']}: {issue['content']} (line {issue['line']})")
