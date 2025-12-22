"""
Python tool for qa-toc-config-detect.

Provides deterministic TOC configuration detection for CLS files.
Detection only - fixing remains LLM-only due to LaTeX macro complexity.
"""

from pathlib import Path
from typing import List, Dict, Any

from qa_engine.infrastructure.detection.toc_detector import TOCDetector


def run_detection(file_path: str, content: str = None) -> List[Dict[str, Any]]:
    """
    Run TOC configuration detection on a CLS file.

    Args:
        file_path: Path to CLS file
        content: Optional content (if not provided, reads from file)

    Returns:
        List of issue dictionaries
    """
    if content is None:
        path = Path(file_path)
        if not path.exists():
            return [{"error": f"File not found: {file_path}"}]
        content = path.read_text(encoding="utf-8", errors="replace")

    detector = TOCDetector()
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
    detector = TOCDetector()
    return detector.get_rules()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results = run_detection(sys.argv[1])
        print(f"Found {len(results)} issues:")
        for r in results:
            print(f"  [{r.get('severity', 'unknown')}] {r.get('rule')}: line {r.get('line')}")
    else:
        print("Usage: python tool.py <cls_file>")
        print("\nAvailable rules:")
        for name, desc in get_rules().items():
            print(f"  {name}: {desc}")
