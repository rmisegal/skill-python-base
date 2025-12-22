"""
Python tool for insert_qa_skill.

Entry point for LLM to invoke skill creation.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.sdk import SkillCreator, SkillConfig, CreationResult


def create_skill(
    name: str,
    family: str,
    level: int,
    skill_type: str,
    description: str,
    rules: Optional[List[str]] = None,
    generate_python: bool = False,
    skills_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new QA skill.

    Args:
        name: Skill name (e.g., qa-bidi-detect-new)
        family: Parent family (e.g., BiDi, code, table)
        level: Skill level (1 or 2)
        skill_type: detection, fix, or orchestrator
        description: Brief description
        rules: List of detection rules
        generate_python: Whether to generate tool.py
        skills_root: Path to skills directory

    Returns:
        Creation result dictionary
    """
    if skills_root is None:
        skills_root = Path(__file__).parent.parent

    config = SkillConfig(
        name=name,
        family=family,
        level=level,
        skill_type=skill_type,
        description=description,
        rules=rules or [],
        generate_python=generate_python,
    )

    creator = SkillCreator(Path(skills_root))
    result = creator.create_skill(config)

    return {
        "success": result.success,
        "created_files": result.created_files,
        "updated_files": result.updated_files,
        "errors": result.errors,
    }


def validate_skill_name(name: str) -> Dict[str, Any]:
    """Validate a skill name follows conventions."""
    errors = []

    if not name.startswith("qa-"):
        errors.append("Must start with 'qa-'")

    parts = name.split("-")
    if len(parts) < 3:
        errors.append("Must have at least 3 parts: qa-{family}-{type}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


if __name__ == "__main__":
    # Example usage
    result = create_skill(
        name="qa-test-detect-example",
        family="test",
        level=2,
        skill_type="detection",
        description="Example detection skill",
        rules=["rule-1", "rule-2"],
        generate_python=True,
    )
    print(result)
