"""Python tool for qa-section-orphan-fix skill."""
from pathlib import Path
from typing import List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.typeset.fixing import SectionOrphanFixer


def fix_file(file_path: str, line_numbers: Optional[List[int]] = None) -> dict:
    """
    Fix section orphan issues in a LaTeX file.

    Args:
        file_path: Path to LaTeX file to fix
        line_numbers: Optional list of specific line numbers to fix

    Returns:
        Dictionary with fix results
    """
    fixer = SectionOrphanFixer()
    result = fixer.fix_file(Path(file_path), line_numbers)
    return fixer.to_dict(result)


def fix_content(content: str, line_numbers: Optional[List[int]] = None,
                file_path: str = "input.tex") -> tuple:
    """
    Fix section orphan issues in content string.

    Args:
        content: LaTeX content to fix
        line_numbers: Optional list of specific line numbers to fix
        file_path: Optional file path for reporting

    Returns:
        Tuple of (fixed_content, result_dict)
    """
    fixer = SectionOrphanFixer()
    fixed_content, result = fixer.fix_content(content, line_numbers, file_path)
    return fixed_content, fixer.to_dict(result)


if __name__ == "__main__":
    import json
    # Demo with sample content
    sample = r"""\section{Test Section}
Content goes here.
"""
    fixed, result = fix_content(sample)
    print("Result:", json.dumps(result, indent=2))
    print("\nFixed content:")
    print(fixed)
