"""Python tool for qa-section-orphan-detect skill."""
from pathlib import Path
from typing import Dict
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.typeset.detection import SectionOrphanDetector


def detect_in_file(file_path: str) -> dict:
    """
    Detect section orphan issues in a LaTeX file.

    Args:
        file_path: Path to LaTeX file to analyze

    Returns:
        Dictionary with detection results
    """
    detector = SectionOrphanDetector()
    result = detector.detect_in_file(Path(file_path))
    return detector.to_dict(result)


def detect_in_content(content: str, file_path: str = "input.tex") -> dict:
    """
    Detect section orphan issues in content string.

    Args:
        content: LaTeX content to analyze
        file_path: Optional file path for reporting

    Returns:
        Dictionary with detection results
    """
    detector = SectionOrphanDetector()
    result = detector.detect_in_content(content, file_path)
    return detector.to_dict(result)


def get_rules() -> Dict[str, str]:
    """Return detection rules."""
    detector = SectionOrphanDetector()
    return detector.get_rules()


if __name__ == "__main__":
    import json
    print("Detection rules:", json.dumps(get_rules(), indent=2))
