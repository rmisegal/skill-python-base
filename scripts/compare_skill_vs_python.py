"""
Compare Skill mechanism vs Direct Python detection for qa-bib-detect.

This demonstrates:
1. What the skill tool.py does (LLM entry point)
2. What the Python BibDetector does (deterministic detection)
3. Verify they produce identical results
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the skill's tool
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "qa-bib-detect"))
from tool import run_detection as skill_run_detection, get_rules as skill_get_rules

# Import the Python module directly
from qa_engine.infrastructure.detection.bib_detector import BibDetector

print("=" * 70)
print("COMPARISON: Skill Tool vs Python Module for qa-bib-detect")
print("=" * 70)

# Test file
test_file = Path(__file__).parent.parent / "test-data" / "CLS-examples" / "examples" / "advanced_example.tex"
content = test_file.read_text(encoding="utf-8", errors="replace")

print(f"\nTest file: {test_file.name}")
print(f"Content size: {len(content)} chars")

# ============================================================
# Method 1: Using the Skill's tool.py (LLM entry point)
# ============================================================
print("\n" + "=" * 70)
print("METHOD 1: Skill Tool (tool.py - LLM invokes this)")
print("=" * 70)

skill_results = skill_run_detection(str(test_file), content)
print(f"\nSkill detected {len(skill_results)} issues:")
for r in skill_results[:5]:
    print(f"  [{r['severity']}] {r['rule']}: line {r['line']}, '{r['content'][:40]}...'")
if len(skill_results) > 5:
    print(f"  ... and {len(skill_results) - 5} more")

# ============================================================
# Method 2: Direct Python module (BibDetector)
# ============================================================
print("\n" + "=" * 70)
print("METHOD 2: Direct Python Module (BibDetector)")
print("=" * 70)

detector = BibDetector()
python_results = detector.detect(content, str(test_file))
print(f"\nPython detected {len(python_results)} issues:")
for issue in python_results[:5]:
    print(f"  [{issue.severity.value}] {issue.rule}: line {issue.line}, '{issue.content[:40]}...'")
if len(python_results) > 5:
    print(f"  ... and {len(python_results) - 5} more")

# ============================================================
# Verification: Are they identical?
# ============================================================
print("\n" + "=" * 70)
print("VERIFICATION: Are results identical?")
print("=" * 70)

# Convert python results to same format as skill
python_as_dicts = [
    {
        "rule": i.rule,
        "file": i.file,
        "line": i.line,
        "content": i.content,
        "severity": i.severity.value,
        "fix": i.fix,
    }
    for i in python_results
]

if len(skill_results) == len(python_as_dicts):
    all_match = True
    for s, p in zip(skill_results, python_as_dicts):
        if s != p:
            all_match = False
            print(f"\nMismatch found:")
            print(f"  Skill:  {s}")
            print(f"  Python: {p}")

    if all_match:
        print("\n✓ IDENTICAL - Skill tool and Python module produce same results!")
else:
    print(f"\n✗ DIFFERENT - Count mismatch: Skill={len(skill_results)}, Python={len(python_as_dicts)}")

# ============================================================
# Show available rules
# ============================================================
print("\n" + "=" * 70)
print("AVAILABLE DETECTION RULES")
print("=" * 70)

rules = skill_get_rules()
for rule_name, description in rules.items():
    print(f"  {rule_name}: {description}")
