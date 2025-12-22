"""
Tool wrapper for CLS sync detector skill.

Provides CLI interface for detecting CLS file inconsistencies within a project.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from qa_engine.infrastructure.detection.cls_sync_detector import CLSSyncDetector


def main(project_root: str) -> None:
    """
    Run CLS sync detection on a project.

    Args:
        project_root: Path to project root directory
    """
    detector = CLSSyncDetector()
    issues = detector.detect_project(project_root)

    if not issues:
        print("No CLS sync issues found. All CLS files are identical.")
        return

    print(f"Found {len(issues)} CLS sync issue(s):\n")

    for issue in issues:
        print(f"[{issue.severity.name}] {issue.rule}")
        print(f"  File: {issue.file}")
        print(f"  Line: {issue.line}")
        print(f"  Issue: {issue.content}")
        print(f"  Fix: {issue.fix}")
        if issue.context and "diff_lines" in issue.context:
            print("  Diff preview:")
            for line in issue.context["diff_lines"][:10]:
                print(f"    {line.rstrip()}")
        print()

    # Output as JSON for programmatic use
    print("\n--- JSON Output ---")
    output = {
        "total_issues": len(issues),
        "issues": [
            {
                "rule": i.rule,
                "file": i.file,
                "line": i.line,
                "content": i.content,
                "severity": i.severity.name,
                "fix": i.fix,
            }
            for i in issues
        ],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tool.py <project_root>")
        sys.exit(1)
    main(sys.argv[1])
