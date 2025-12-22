"""Python tool for qa-heb-math-detect skill.

Provides deterministic Hebrew-in-math detection for LaTeX documents.
"""
from typing import Any, Dict, List
from qa_engine.infrastructure.detection.heb_math_detector import HebMathDetector


def detect(content: str, file_path: str, offset: int = 0) -> List[Dict[str, Any]]:
    """Detect Hebrew-in-math issues in content.

    Args:
        content: LaTeX file content
        file_path: Path to the file (for reporting)
        offset: Line number offset for chunked processing

    Returns:
        List of issues as dictionaries
    """
    detector = HebMathDetector()
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


def get_rules() -> Dict[str, str]:
    """Get list of supported detection rules."""
    detector = HebMathDetector()
    return detector.get_rules()


if __name__ == "__main__":
    sample = r"""$P(\text{שפעת}) = 0.025$
$x_{מקסימום}$
\newcommand{\hebmath}[1]{\text{\texthebrew{#1}}}"""
    issues = detect(sample, "test.tex")
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  - {issue['rule']}: {issue['content'][:40]}...")
