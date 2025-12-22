"""Python tool for qa-infra-backup skill."""
from pathlib import Path
from typing import Dict, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.backup import ProjectBackupUtility


def create_backup(
    project_path: str,
    backup_parent_dir: Optional[str] = None
) -> dict:
    """
    Create timestamped backup of entire project.

    Args:
        project_path: Path to project directory to backup
        backup_parent_dir: Optional custom backup location (defaults to parent of project)

    Returns:
        Dictionary with backup result details
    """
    backup_parent = Path(backup_parent_dir) if backup_parent_dir else None
    utility = ProjectBackupUtility(backup_parent_dir=backup_parent)
    result = utility.create_backup(Path(project_path))
    return result.to_dict()


def get_operations() -> Dict[str, str]:
    """Return dict of operation_name -> description."""
    return {
        "create-timestamped-backup": "Generate backup_YYYYMMDD_HHMMSS folder",
        "preserve-permissions": "Copy with shutil.copy2 preserving permissions",
        "preserve-timestamps": "Preserve file modification times",
        "include-hidden-files": "Copy all files including hidden ones",
        "verify-file-count": "Compare file counts for backup integrity",
    }


if __name__ == "__main__":
    # Test the tool
    import json
    print("Operations:", json.dumps(get_operations(), indent=2))
