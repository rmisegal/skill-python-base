"""Debug remaining bib-undefined-cite issues."""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection import BibDetector

# Test directory
test_dir = Path(__file__).parent.parent / "test-data" / "CLS-examples"

print("=" * 60)
print("REMAINING BIB-UNDEFINED-CITE ISSUES")
print("=" * 60)

detector = BibDetector()
all_issues = []

for tex_file in test_dir.rglob("*.tex"):
    if "_patch" in tex_file.name:
        continue
    content = tex_file.read_text(encoding="utf-8", errors="replace")
    issues = detector.detect(content, str(tex_file))
    undefined = [i for i in issues if i.rule == "bib-undefined-cite"]
    if undefined:
        print(f"\n{tex_file.name} ({len(undefined)} issues):")
        for issue in undefined[:5]:  # First 5 per file
            print(f"  Line {issue.line}: '{issue.content}'")
        all_issues.extend(undefined)

print(f"\n\nTotal: {len(all_issues)} undefined citations")
