"""Python tool for qa-table-fix-alignment skill."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.fixing import TableAlignmentFixer


def fix_content(content: str, issues: Optional[List[Dict]] = None) -> tuple:
    """
    Fix table cell alignment issues in content string.

    Args:
        content: LaTeX content to fix
        issues: Optional list of specific issues to fix

    Returns:
        Tuple of (fixed_content, result_dict)
    """
    fixer = TableAlignmentFixer()
    fixed_content, result = fixer.fix_content(content, issues)
    return fixed_content, fixer.to_dict(result)


def fix_file(file_path: str, issues: Optional[List[Dict]] = None) -> dict:
    """
    Fix table cell alignment issues in a file.

    Args:
        file_path: Path to LaTeX file to fix
        issues: Optional list of specific issues to fix

    Returns:
        Dictionary with fix results
    """
    path = Path(file_path)
    if not path.exists():
        return {"skill": "qa-table-fix-alignment", "status": "ERROR",
                "error": f"File not found: {file_path}"}

    content = path.read_text(encoding="utf-8")
    fixed_content, result = fix_content(content, issues)

    if result["cells_fixed"] > 0:
        path.write_text(fixed_content, encoding="utf-8")

    return result


if __name__ == "__main__":
    import json
    # Demo with sample content
    sample = r"""
\begin{tabular}{|c|c|}
\hline
Header1 & Header2 \\
\hline
English & More text \\
\hline
\end{tabular}
"""
    fixed, result = fix_content(sample)
    print("Result:", json.dumps(result, indent=2))
    print("\nFixed content:")
    print(fixed)
