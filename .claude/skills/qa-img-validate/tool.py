"""Python tool for qa-img-validate skill."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.validation import ImageValidator


def validate_content(
    content: str, before_issues: List[Dict] = None, source_dir: str = None
) -> dict:
    """
    Full validation: record before state and validate after.

    Args:
        content: LaTeX content to validate
        before_issues: List of issues detected before fixes
        source_dir: Source directory for image path resolution

    Returns:
        Validation result dict
    """
    validator = ImageValidator()
    dir_path = Path(source_dir) if source_dir else None
    result = validator.validate_content(content, before_issues, dir_path)
    return validator.to_dict(result)


def validate_after_fixes(content: str, source_dir: str = None) -> dict:
    """
    Validate images in content (assumes before state already recorded).

    Args:
        content: LaTeX content to validate
        source_dir: Source directory for image path resolution

    Returns:
        Validation result dict
    """
    validator = ImageValidator()
    dir_path = Path(source_dir) if source_dir else None
    result = validator.validate_after_fixes(content, dir_path)
    return validator.to_dict(result)


def record_and_validate(
    content: str, initial_issues: List[Dict], source_dir: str = None
) -> dict:
    """
    Record initial issues and validate current state.

    Args:
        content: LaTeX content to validate
        initial_issues: Issues detected before any fixes
        source_dir: Source directory for image path resolution

    Returns:
        Validation result dict with before/after comparison
    """
    validator = ImageValidator()
    dir_path = Path(source_dir) if source_dir else None
    validator.record_before_state(initial_issues)
    result = validator.validate_after_fixes(content, dir_path)
    return validator.to_dict(result)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding='utf-8')

    # Demo: Validate content with simulated before/after
    sample = r"""
\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{images/diagram1.png}
\caption{System architecture}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.6\textwidth]{images/chart.pdf}
\caption{Performance results}
\end{figure}
"""
    # Simulate issues detected before fixes
    before_issues = [
        {"rule": "img-missing-file", "line": 4, "content": "diagram1.png"},
        {"rule": "img-missing-file", "line": 10, "content": "chart.pdf"},
    ]

    result = validate_content(sample, before_issues)
    print("Validation Result:", json.dumps(result, indent=2))
