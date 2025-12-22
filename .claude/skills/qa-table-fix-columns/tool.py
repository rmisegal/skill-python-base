"""Python tool for qa-table-fix-columns skill."""
from pathlib import Path
from typing import Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.table.fixing import TableColumnFixer


def fix_content(content: str, file_path: str = "") -> tuple:
    """
    Fix column order in tables in content string.

    Args:
        content: LaTeX content to fix
        file_path: Optional file path for reporting

    Returns:
        Tuple of (fixed_content, result_dict)
    """
    fixer = TableColumnFixer()
    fixed_content, result = fixer.fix_content(content, file_path)
    return fixed_content, fixer.to_dict(result)


def fix_file(file_path: str) -> dict:
    """
    Fix column order in tables in a file.

    Args:
        file_path: Path to LaTeX file to fix

    Returns:
        Dictionary with fix results
    """
    path = Path(file_path)
    fixer = TableColumnFixer()

    if not path.exists():
        return {"skill": "qa-table-fix-columns", "status": "ERROR",
                "error": f"File not found: {file_path}"}

    result = fixer.fix_file(path)
    return fixer.to_dict(result)


if __name__ == "__main__":
    import json
    # Demo with sample content
    sample = r"""
\begin{tabular}{|c|c|c|}
\hline
Name & Value & Unit \\
\hline
A & 1 & kg \\
B & 2 & m \\
\hline
\end{tabular}
"""
    fixed, result = fix_content(sample)
    print("Result:", json.dumps(result, indent=2))
    print("\nFixed content:")
    print(fixed)
