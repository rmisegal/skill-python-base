"""
Python tool for qa-bib-detect skill.

Entry point for LLM to invoke bibliography detection.
"""

from pathlib import Path
from typing import List, Dict, Any

from qa_engine.infrastructure.detection.bib_detector import BibDetector


def run_detection(file_path: str, content: str = None) -> List[Dict[str, Any]]:
    """
    Run bibliography detection on file.

    Args:
        file_path: Path to LaTeX file
        content: Optional content (reads file if not provided)

    Returns:
        List of issue dictionaries
    """
    detector = BibDetector()

    if content is None:
        path = Path(file_path)
        if not path.exists():
            return [{"error": f"File not found: {file_path}"}]
        content = path.read_text(encoding="utf-8")

    issues = detector.detect(content, file_path)

    return [
        {
            "rule": issue.rule,
            "file": issue.file,
            "line": issue.line,
            "content": issue.content,
            "severity": issue.severity.value,
            "fix": issue.fix,
        }
        for issue in issues
    ]


def get_rules() -> Dict[str, str]:
    """Get available detection rules."""
    detector = BibDetector()
    return detector.get_rules()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results = run_detection(sys.argv[1])
        for r in results:
            print(f"[{r['severity']}] {r['rule']}: {r['content']} (line {r['line']})")
