"""
Compare qa-code-fix-encoding skill with Python EncodingFixer.

This script tests both approaches on the same input file.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, "C:/25D/Richman/skill-python-base/src")

from pathlib import Path
from qa_engine.infrastructure.fixing.encoding_fixer import EncodingFixer

# Read test file
test_file = Path("C:/25D/Richman/skill-python-base/tests/encoding_test_sample.tex")
content = test_file.read_text(encoding="utf-8")

# Run Python fixer
fixer = EncodingFixer()
fixed_content, changes = fixer.fix_content(content, "auto")

# Generate report
report = []
report.append("=" * 60)
report.append("ENCODING FIX COMPARISON REPORT")
report.append("=" * 60)

report.append("\n## Changes Made by Python Fixer:")
for i, change in enumerate(changes, 1):
    report.append(f"  {i}. {change}")

report.append(f"\nTotal changes: {len(changes)}")

# Check what patterns are supported
patterns = fixer.get_patterns()
report.append("\n## TEXT PATTERNS (Python Fixer):")
for name, p in patterns["text"].items():
    report.append(f"  - {name}: {p['description']}")

report.append("\n## CODE PATTERNS (Python Fixer):")
for name, p in patterns["code"].items():
    report.append(f"  - {name}: {p['description']}")

# Gap analysis
report.append("\n## GAP ANALYSIS")
report.append("Patterns from skill.md NOT in Python fixer:")

skill_only_patterns = {
    "U+2212 Mathematical Minus": ("\u2212", "U+002D (-)"),
    "U+2013 En Dash": ("\u2013", "U+002D (-)"),
    "U+2014 Em Dash": ("\u2014", "U+002D (-)"),
    "U+2018 Left Single Quote": ("\u2018", "U+0027 (')"),
    "U+2019 Right Single Quote": ("\u2019", "U+0027 (')"),
    "U+201C Left Double Quote": ("\u201c", 'U+0022 (")'),
    "U+201D Right Double Quote": ("\u201d", 'U+0022 (")'),
}

for name, (char, replacement) in skill_only_patterns.items():
    if char in content:
        if char in fixed_content:
            report.append(f"  [GAP] {name} -> {replacement} - NOT FIXED by Python")
        else:
            report.append(f"  [OK] {name} -> {replacement} - Fixed by Python")
    else:
        report.append(f"  [N/A] {name} - Not in test file")

# Save outputs
output_file = Path("C:/25D/Richman/skill-python-base/tests/encoding_test_python_output.tex")
output_file.write_text(fixed_content, encoding="utf-8")

report_file = Path("C:/25D/Richman/skill-python-base/tests/encoding_comparison_report.txt")
report_file.write_text("\n".join(report), encoding="utf-8")

print(f"Python output saved to: {output_file}")
print(f"Report saved to: {report_file}")
print("\n" + "\n".join(report))
