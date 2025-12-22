"""Debug bidi-numbers detection and fixing."""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection import BiDiDetector
from qa_engine.infrastructure.fixing import BiDiFixer

# Test file with number issues
test_file = Path(__file__).parent.parent / "test-data" / "CLS-examples" / "examples" / "image_example.tex"
content = test_file.read_text(encoding="utf-8", errors="replace")
lines = content.split("\n")

print("=" * 60)
print("DEBUG BIDI-NUMBERS")
print("=" * 60)

# Run detection
detector = BiDiDetector()
issues = detector.detect(content, str(test_file))

# Filter to bidi-numbers
number_issues = [i for i in issues if i.rule == "bidi-numbers"]
print(f"\nFound {len(number_issues)} bidi-numbers issues:")

for issue in number_issues:
    print(f"\n  Line {issue.line}: '{issue.content}'")
    print(f"  Match position: {issue.context.get('match_start')}")
    if 1 <= issue.line <= len(lines):
        line = lines[issue.line - 1]
        pos = issue.context.get('match_start', 0)
        print(f"  Context: ...{line[max(0,pos-20):min(len(line),pos+20)]}...")

# Try fixing
print("\n" + "=" * 60)
print("APPLYING FIXES")
print("=" * 60)

fixer = BiDiFixer()
fixed = fixer.fix(content, number_issues)

if fixed != content:
    print("\nContent WAS modified!")
    orig_lines = content.split("\n")
    fixed_lines = fixed.split("\n")
    for i, (o, f) in enumerate(zip(orig_lines, fixed_lines)):
        if o != f:
            print(f"\nLine {i+1}:")
            print(f"  BEFORE: {o}")
            print(f"  AFTER:  {f}")
else:
    print("\nContent was NOT modified!")
