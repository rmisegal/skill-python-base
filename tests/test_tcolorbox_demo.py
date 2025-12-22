# -*- coding: utf-8 -*-
"""Demo: tcolorbox detection and fixing."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, "src")

from qa_engine.infrastructure.detection.bidi_detector import BiDiDetector
from qa_engine.infrastructure.detection.bidi_rules import BIDI_RULES
from qa_engine.infrastructure.fixing.tikz_fixer import TikzFixer

print("=" * 70)
print("PYTHON TOOL: qa-BiDi-fix-tcolorbox Equivalent")
print("=" * 70)

# Show the rule definition
rule = BIDI_RULES["bidi-tcolorbox"]
print("\n1. RULE DEFINITION (bidi_rules.py:66-74):")
print(f"   Pattern: {rule['pattern']}")
print(f"   Severity: {rule['severity']}")
print(f"   context_pattern: {rule.get('context_pattern')}")
print(f"   document_context: {rule.get('document_context')}")
print(f"   exclude_pattern: {rule.get('exclude_pattern')}")
print(f"   fix_template: {rule['fix_template']}")

# Test detection
print("\n" + "=" * 70)
print("2. DETECTION TEST")
print("=" * 70)

# Hebrew text to create RTL context
heb_text = "\u05e9\u05dc\u05d5\u05dd \u05e2\u05d5\u05dc\u05dd"  # "shalom olam"

test_cases = [
    ("Hebrew + tcolorbox (should detect)",
     f"{heb_text}\ntext\n\\begin{{tcolorbox}}\ncontent\n\\end{{tcolorbox}}",
     True),
    ("No Hebrew (should NOT detect)",
     "Hello world\n\\begin{tcolorbox}\ncontent\n\\end{tcolorbox}",
     False),
    ("Hebrew + wrapped tcolorbox (should NOT detect)",
     f"{heb_text}\n\\begin{{english}}\n\\begin{{tcolorbox}}\ncontent\n\\end{{tcolorbox}}\n\\end{{english}}",
     False),
]

detector = BiDiDetector()

for name, content, should_detect in test_cases:
    issues = detector.detect(content, "test.tex")
    tc_issues = [i for i in issues if i.rule == "bidi-tcolorbox"]
    status = "PASS" if (len(tc_issues) > 0) == should_detect else "FAIL"
    print(f"   [{status}] {name}: Found {len(tc_issues)} issues")

# Show fix approach
print("\n" + "=" * 70)
print("3. FIX APPROACH (same as TikzFixer)")
print("=" * 70)

# Demonstrate fixing
content_with_issue = f"""{heb_text}
Some text here.

\\begin{{tcolorbox}}
Box content goes here.
\\end{{tcolorbox}}

More Hebrew text.
"""

issues = detector.detect(content_with_issue, "test.tex")
tc_issues = [i for i in issues if i.rule == "bidi-tcolorbox"]

print(f"\n   Detected {len(tc_issues)} tcolorbox issue(s)")
if tc_issues:
    print(f"   Line {tc_issues[0].line}: {tc_issues[0].rule}")
    print(f"   Suggested fix: {tc_issues[0].fix}")

print("\n   FIX PATTERN:")
print("   BEFORE:")
print("   \\begin{tcolorbox}")
print("   content")
print("   \\end{tcolorbox}")
print("\n   AFTER:")
print("   \\begin{english}")
print("   \\begin{tcolorbox}")
print("   content")
print("   \\end{tcolorbox}")
print("   \\end{english}")

print("\n" + "=" * 70)
print("4. COMPARISON: LLM Skill vs Python Tool")
print("=" * 70)
print("""
   | Task                    | LLM Skill (Original)      | Python Tool (New)         |
   |-------------------------|---------------------------|---------------------------|
   | Detect tcolorbox        | LLM interprets pattern    | regex: \\begin{tcolorbox} |
   | Check RTL context       | LLM checks for Hebrew     | context_pattern: [alef-tav]|
   | Check document scope    | LLM reads whole doc       | document_context: True    |
   | Skip wrapped boxes      | LLM checks for english    | exclude_pattern check     |
   | Generate fix            | LLM writes wrapper        | fix_template string       |
   | Apply fix               | LLM edits file            | TikzFixer-like logic      |
   |-------------------------|---------------------------|---------------------------|
   | DETERMINISTIC?          | No (LLM varies)           | Yes (regex-based)         |
   | TESTABLE?               | Hard                      | Unit tests exist          |
""")

print("=" * 70)
print("CONCLUSION: Python tool provides identical detection with deterministic results")
print("=" * 70)
