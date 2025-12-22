"""Python tool for qa-infra-scan skill."""
from pathlib import Path
from typing import Dict, List
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.detection.infra_scanner import (
    InfraScanner, REQUIRED_DIRS, FILE_RULES
)


def scan(project_path: str) -> dict:
    """
    Scan project structure and identify misplaced files.

    Args:
        project_path: Path to project root directory

    Returns:
        Dictionary with scan results in skill output format
    """
    scanner = InfraScanner(Path(project_path))
    result = scanner.scan()
    return scanner.to_dict(result)


def get_required_dirs() -> List[str]:
    """Return list of required directories."""
    return REQUIRED_DIRS.copy()


def get_file_rules() -> Dict[str, str]:
    """Return file categorization rules."""
    return FILE_RULES.copy()


if __name__ == "__main__":
    import json
    print("Required directories:", json.dumps(get_required_dirs(), indent=2))
    print("File rules:", json.dumps(get_file_rules(), indent=2))
