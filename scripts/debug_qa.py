"""Debug QA detection - show all remaining issues by type."""

import sys
import io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection import (
    BiDiDetector, CodeDetector, TableDetector, BibDetector
)

# Test directory
test_dir = Path(__file__).parent.parent / "test-data" / "CLS-examples"

print("=" * 60)
print("REMAINING ISSUES BY TYPE")
print("=" * 60)

detectors = {
    "bidi": BiDiDetector(),
    "code": CodeDetector(),
    "table": TableDetector(),
    "bib": BibDetector(),
}

all_issues = []
issues_by_rule = defaultdict(list)

for tex_file in test_dir.rglob("*.tex"):
    if "_patch" in tex_file.name or tex_file.suffix != ".tex":
        continue
    content = tex_file.read_text(encoding="utf-8", errors="replace")

    for detector_name, detector in detectors.items():
        issues = detector.detect(content, str(tex_file))
        for issue in issues:
            all_issues.append(issue)
            issues_by_rule[issue.rule].append(issue)

print(f"\nTotal issues: {len(all_issues)}")
print("\nIssues by rule:")
for rule, issues in sorted(issues_by_rule.items(), key=lambda x: -len(x[1])):
    print(f"  {rule}: {len(issues)}")
    # Show first example
    ex = issues[0]
    print(f"    Example: line {ex.line}, '{ex.content[:50] if ex.content else 'N/A'}...'")
    print(f"    File: {Path(ex.file).name}")
