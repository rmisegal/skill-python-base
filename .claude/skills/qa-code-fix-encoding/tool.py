"""
Python tool for qa-code-fix-encoding.

Fixes character encoding issues in LaTeX documents.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.fixing.encoding_fixer import EncodingFixer


def run_fix(
    file_path: str,
    content: Optional[str] = None,
    context: str = "text",
) -> Dict[str, Any]:
    """
    Fix encoding issues in file.

    Args:
        file_path: Path to file
        content: Optional content (reads file if not provided)
        context: 'text' or 'code' for different replacement rules

    Returns:
        Dict with fixed content and changes made
    """
    if content is None:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        content = path.read_text(encoding="utf-8")

    fixer = EncodingFixer()
    fixed, changes = fixer.fix_content(content, context)

    return {
        "success": True,
        "fixed_content": fixed,
        "changes": changes,
        "total_fixes": len(changes),
    }


def get_patterns() -> Dict[str, Dict[str, str]]:
    """Get available fix patterns."""
    fixer = EncodingFixer()
    return fixer.get_patterns()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = run_fix(sys.argv[1])
        print(f"Fixed {result.get('total_fixes', 0)} issues")
