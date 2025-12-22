"""
Analyze a single example file to see detailed issues.
"""

import sys
import io
from pathlib import Path

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection import (
    BiDiDetector,
    TableDetector,
    CodeDetector,
    BibDetector,
)


def analyze_file(file_path: str):
    """Analyze a single file and show detailed issues."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")

    detectors = {
        "BiDi": BiDiDetector(),
        "Table": TableDetector(),
        "Code": CodeDetector(),
        "Bib": BibDetector(),
    }

    print(f"\n{'=' * 60}")
    print(f"ANALYZING: {path.name}")
    print(f"{'=' * 60}")
    print(f"Total lines: {len(lines)}")

    all_issues = []
    for name, detector in detectors.items():
        issues = detector.detect(content, str(path))
        all_issues.extend(issues)
        print(f"\n{name} Detector: {len(issues)} issues")

        # Show first 10 issues with context
        for issue in issues[:10]:
            line_num = issue.line
            if 1 <= line_num <= len(lines):
                line_content = lines[line_num - 1].strip()[:80]
                print(f"  Line {line_num}: {issue.rule}")
                print(f"    Content: {line_content}")
                if issue.fix:
                    print(f"    Fix: {issue.fix}")

    # Group by rule
    print(f"\n{'-' * 60}")
    print("Summary by Rule:")
    rule_counts = {}
    for issue in all_issues:
        rule_counts[issue.rule] = rule_counts.get(issue.rule, 0) + 1

    for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
        print(f"  {rule}: {count}")

    print(f"\nTotal: {len(all_issues)} issues")


if __name__ == "__main__":
    test_file = (
        Path(__file__).parent.parent
        / "test-data"
        / "CLS-examples"
        / "examples"
        / "beginner_example.tex"
    )
    analyze_file(str(test_file))
