"""
Tool wrapper for CLS sync fixer skill.

Provides CLI interface for fixing CLS file inconsistencies within a project.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from qa_engine.infrastructure.fixing.cls_sync_fixer import CLSSyncFixer


def main(project_root: str, no_backup: bool = False) -> None:
    """
    Run CLS sync fix on a project.

    Args:
        project_root: Path to project root directory
        no_backup: If True, skip creating backup files
    """
    fixer = CLSSyncFixer()
    result = fixer.fix_project(project_root, create_backup=not no_backup)

    print("CLS Sync Fix Results:")
    print(f"  Success: {result.success}")
    print(f"  Files fixed: {result.files_fixed}")
    print(f"  Files skipped (already synced): {result.files_skipped}")

    if result.backups_created:
        print(f"\nBackups created ({len(result.backups_created)}):")
        for backup in result.backups_created:
            print(f"  - {backup}")

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")

    # Output as JSON for programmatic use
    print("\n--- JSON Output ---")
    output = {
        "success": result.success,
        "files_fixed": result.files_fixed,
        "files_skipped": result.files_skipped,
        "backups_created": result.backups_created,
        "errors": result.errors,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tool.py <project_root> [--no-backup]")
        sys.exit(1)

    project = sys.argv[1]
    skip_backup = "--no-backup" in sys.argv
    main(project, no_backup=skip_backup)
