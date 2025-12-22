"""Python tool for qa-infra-validate skill."""
from pathlib import Path
from typing import Dict, List
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.detection.infra_validator import (
    InfraValidator, REQUIRED_DIRS, VALID_EXTENSIONS
)


def validate(project_path: str, expected_file_count: int = 0) -> dict:
    """
    Validate project structure after reorganization.

    Args:
        project_path: Path to project root directory
        expected_file_count: Expected file count for comparison (0 to skip)

    Returns:
        Dictionary with validation results and PASS/FAIL verdict
    """
    validator = InfraValidator(Path(project_path))
    result = validator.validate(expected_file_count)
    return validator.to_dict(result)


def get_required_dirs() -> List[str]:
    """Return list of required directories."""
    return REQUIRED_DIRS.copy()


def get_valid_extensions() -> Dict[str, set]:
    """Return valid file extensions per directory."""
    return {k: v.copy() for k, v in VALID_EXTENSIONS.items()}


if __name__ == "__main__":
    import json
    print("Required directories:", json.dumps(get_required_dirs(), indent=2))
    print("Valid extensions:", {k: list(v) for k, v in get_valid_extensions().items()})
