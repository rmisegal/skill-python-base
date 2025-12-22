"""
Python tool for qa-code-detect skill.

Provides deterministic code block issue detection for LaTeX documents.
"""

from typing import List, Dict, Any

from qa_engine.infrastructure.detection.code_detector import CodeDetector


def detect(content: str, file_path: str, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Detect code block issues in content.

    Args:
        content: LaTeX file content
        file_path: Path to the file (for reporting)
        offset: Line number offset for chunked processing

    Returns:
        List of issues as dictionaries
    """
    detector = CodeDetector()
    issues = detector.detect(content, file_path, offset)

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


def get_rules() -> List[str]:
    """Get list of supported detection rules."""
    detector = CodeDetector()
    return detector.get_rules()


if __name__ == "__main__":
    # Example usage
    sample = r"\begin{pythonbox}" + "\nprint('hello')\n" + r"\end{pythonbox}"
    issues = detect(sample, "test.tex")
    print(f"Found {len(issues)} issues")
