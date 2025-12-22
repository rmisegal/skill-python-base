"""
Python tool for qa-cls-version-fix skill.

Provides deterministic CLS copy and backup operations.
Reference: C:\25D\CLS-examples\hebrew-academic-template.cls
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from qa_engine.infrastructure.fixing.cls_fixer import CLSFixer


def fix_cls(project_cls_path: str, create_backup: bool = True) -> Dict[str, Any]:
    """
    Copy reference CLS to project location.

    Args:
        project_cls_path: Path where CLS should be copied
        create_backup: Whether to backup existing file (default True)

    Returns:
        Dict with success, message, backup_path, new_version
    """
    fixer = CLSFixer()
    result = fixer.fix_file(Path(project_cls_path), create_backup)

    return {
        "success": result.success,
        "message": result.message,
        "backup_path": result.backup_path,
        "new_version": result.new_version,
    }


def get_new_capabilities() -> List[str]:
    """
    Get list of new capabilities in reference CLS.

    Parses CHANGELOG from reference to extract NEW/FIXED entries.
    This info is passed to LLM skill for intelligent document updates.

    Returns:
        List of capability strings (e.g., "NEW: 'latin' environment")
    """
    fixer = CLSFixer()
    return fixer.get_new_capabilities()


def get_patterns() -> List[str]:
    """Get list of supported fix patterns."""
    fixer = CLSFixer()
    return fixer.get_patterns()


if __name__ == "__main__":
    # Example: List new capabilities
    print("New capabilities in reference CLS:")
    for cap in get_new_capabilities():
        print(f"  - {cap}")
