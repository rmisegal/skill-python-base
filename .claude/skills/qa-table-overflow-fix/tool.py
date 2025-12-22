"""Python tool for qa-table-overflow-fix skill."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.table.fixing import TableOverflowFixer


def fix_content(
    content: str, file_path: str = "", issues: Optional[List[Dict]] = None
) -> tuple:
    """
    Fix overflow issues in tables in content string.

    Args:
        content: LaTeX content to fix
        file_path: Optional file path for reporting
        issues: Optional list of detected issues to fix

    Returns:
        Tuple of (fixed_content, result_dict)
    """
    fixer = TableOverflowFixer()
    fixed_content, result = fixer.fix_content(content, file_path, issues)
    return fixed_content, fixer.to_dict(result)


def fix_file(file_path: str) -> dict:
    """
    Fix overflow issues in tables in a file.

    Args:
        file_path: Path to LaTeX file to fix

    Returns:
        Dictionary with fix results
    """
    path = Path(file_path)
    fixer = TableOverflowFixer()

    if not path.exists():
        return {"skill": "qa-table-overflow-fix", "status": "ERROR",
                "error": f"File not found: {file_path}"}

    result = fixer.fix_file(path)
    return fixer.to_dict(result)


if __name__ == "__main__":
    import json
    # Demo with sample content
    sample = r"""
\begin{hebrewtable}[htbp]
\caption{Wide table example}
\begin{rtltabular}{|c|c|c|c|c|}
\hline
A & B & C & D & E \\
\hline
1 & 2 & 3 & 4 & 5 \\
\hline
\end{rtltabular}
\end{hebrewtable}
"""
    fixed, result = fix_content(sample)
    print("Result:", json.dumps(result, indent=2))
    print("\nFixed content:")
    print(fixed)
