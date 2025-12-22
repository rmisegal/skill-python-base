"""Python tool for qa-mdframed-fix skill."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.typeset.fixing import MdframedFixer


def fix_file(file_path: str, line_numbers: Optional[List[int]] = None) -> dict:
    """
    Fix mdframed page break issues in a file.

    Args:
        file_path: Path to LaTeX file to fix
        line_numbers: Specific line numbers to fix (None for all)

    Returns:
        Dictionary with fix results
    """
    fixer = MdframedFixer()
    result = fixer.fix_file(Path(file_path), line_numbers)
    return fixer.to_dict(result)


def fix_content(content: str, line_numbers: Optional[List[int]] = None) -> tuple:
    """
    Fix mdframed page break issues in content string.

    Args:
        content: LaTeX content to fix
        line_numbers: Specific line numbers to fix (None for all)

    Returns:
        Tuple of (fixed_content, result_dict)
    """
    fixer = MdframedFixer()
    fixed, result = fixer.fix_content(content, line_numbers)
    return fixed, fixer.to_dict(result)


def get_strategies() -> Dict[str, str]:
    """Return available fix strategies."""
    return {
        "vspace": r"\vspace{1em} - Default spacing before box",
        "vspace_long": r"\vspace{1.5em} - After long paragraph",
        "nopagebreak": r"\nopagebreak - After heading",
        "combined": r"\vspace{1em}\nopagebreak - Both together",
        "clearpage": r"\clearpage - Force new page",
    }


if __name__ == "__main__":
    import json
    print("Strategies:", json.dumps(get_strategies(), indent=2))
