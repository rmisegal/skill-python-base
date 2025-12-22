"""
Python tool for qa-typeset-detect skill.

Provides deterministic LaTeX log warning detection.
"""

from typing import List, Dict, Any

from qa_engine.infrastructure.detection.typeset_detector import TypesetDetector


def detect(content: str, file_path: str, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Detect typeset warnings in LaTeX log content.

    Args:
        content: LaTeX log file content
        file_path: Path to the log file (for reporting)
        offset: Line number offset

    Returns:
        List of issues as dictionaries
    """
    detector = TypesetDetector()
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
    detector = TypesetDetector()
    return detector.get_rules()


if __name__ == "__main__":
    # Example usage
    sample = r"Overfull \hbox (12.34567pt too wide) in paragraph at lines 42--45"
    issues = detect(sample, "main.log")
    print(f"Found {len(issues)} issues")
