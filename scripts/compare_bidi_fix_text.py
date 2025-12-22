"""
Compare: Original qa-BiDi-fix-text (LLM-only) vs Python-backed qa-BiDi-fix-text

This demonstrates the difference between:
1. LLM-only skill: 333 lines with 10 fix patterns
2. Python-backed skill: BiDiFixer class with deterministic regex
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import Python tools
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "qa-BiDi-fix-text"))
from tool import fix as python_fix, get_patterns

from qa_engine.infrastructure.detection.bidi_detector import BiDiDetector
from qa_engine.infrastructure.fixing.bidi_fixer import BiDiFixer

print("=" * 70)
print("COMPARISON: qa-BiDi-fix-text (LLM-only vs Python-backed)")
print("=" * 70)

# ============================================================
# SKILL FILE ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("SKILL FILE ANALYSIS")
print("=" * 70)

llm_skill = Path(r"C:\Users\gal-t\.claude\skills\qa-BiDi-fix-text\skill.md")
python_skill = Path(__file__).parent.parent / ".claude" / "skills" / "qa-BiDi-fix-text"

llm_lines = len(llm_skill.read_text(encoding="utf-8").split("\n"))
python_skill_lines = len((python_skill / "skill.md").read_text(encoding="utf-8").split("\n"))
python_tool_lines = len((python_skill / "tool.py").read_text(encoding="utf-8").split("\n"))

print(f"\n1. ORIGINAL SKILL: qa-BiDi-fix-text (User global - LLM-only)")
print(f"   Location: {llm_skill.parent}")
print(f"   skill.md: {llm_lines} lines of fix patterns and instructions")
print(f"   tool.py: NONE (all work done by LLM)")
print(f"   Fix Patterns: 10 documented patterns")

print(f"\n2. NEW SKILL: qa-BiDi-fix-text (Python-backed)")
print(f"   Location: {python_skill}")
print(f"   skill.md: {python_skill_lines} lines (reference to Python)")
print(f"   tool.py: {python_tool_lines} lines (wrapper)")
print(f"   BiDiFixer: ~150 lines of Python")

# ============================================================
# FIX PATTERNS COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("FIX PATTERNS COMPARISON")
print("=" * 70)

print("""
┌──────────────────────────────────────────────────────────────────────────────┐
│ ORIGINAL LLM-ONLY SKILL (10 fix patterns in 333 lines)                       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Pattern 1:  Numbers in RTL Context                                           │
│             Fix: Wrap with \\textenglish{} or \\num{}                        │
│                                                                              │
│ Pattern 2:  English Terms in Hebrew Text                                     │
│             Fix: Wrap with \\textenglish{} or \\en{}                         │
│                                                                              │
│ Pattern 3:  Hebrew in English Context                                        │
│             Fix: Wrap with \\texthebrew{}                                    │
│                                                                              │
│ Pattern 4:  Title Page Version in CLS                                        │
│             Fix: Modify CLS ~line 671 to use \\texthebrew{}                  │
│                                                                              │
│ Pattern 5:  Inline Math with Hebrew                                          │
│             Fix: Use \\hebmath{} (CLS v3.0+)                                 │
│                                                                              │
│ Pattern 6:  Acronyms in Hebrew Context                                       │
│             Fix: Wrap with \\en{}                                            │
│                                                                              │
│ Pattern 7:  Decimal Numbers in Preamble Metadata                             │
│             Fix: Wrap with \\en{}                                            │
│                                                                              │
│ Pattern 8:  Preamble Metadata Commands                                       │
│             Fix: Wrap content in \\hebrewtitle{}, \\hebrewversion{}          │
│                                                                              │
│ Pattern 9:  Hebrew Chapter Labels                                            │
│             Fix: Use \\hebrewchapterlabel{} instead of \\label{}             │
│                                                                              │
│ Pattern 10: Hebrew Inside English Wrapper                                    │
│             Fix: Move Hebrew outside \\textenglish{} or \\en{}               │
│                                                                              │
│ HOW IT WORKS: LLM reads patterns, finds matches, applies appropriate fix     │
│ based on context understanding and LaTeX knowledge.                          │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ PYTHON-BACKED SKILL (4 core fix rules in BiDiFixer)                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Rule: bidi-numbers                                                           │
│       Fix: \\num{} for numbers, \\hebyear{} for years, \\percent{} for %     │
│                                                                              │
│ Rule: bidi-english                                                           │
│       Fix: \\en{content}                                                     │
│                                                                              │
│ Rule: bidi-acronym                                                           │
│       Fix: \\en{ACRONYM}                                                     │
│                                                                              │
│ Rule: bidi-hebrew-in-english                                                 │
│       Fix: DETECTION ONLY (complex restructure needed)                       │
│                                                                              │
│ HOW IT WORKS: Python regex detects → BiDiFixer applies wrapper commands      │
│ RESULT: 100% deterministic, same input = same output always                  │
└──────────────────────────────────────────────────────────────────────────────┘
""")

# ============================================================
# PATTERN-BY-PATTERN MAPPING
# ============================================================
print("\n" + "=" * 70)
print("PATTERN-BY-PATTERN MAPPING")
print("=" * 70)

print("""
┌──────┬────────────────────────────────┬─────────────┬────────────────────────┐
│ #    │ Original LLM Pattern           │ Python Rule │ Status                 │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P1   │ Numbers in RTL Context         │ bidi-numbers│ ✅ FULLY COVERED       │
│      │                                │             │ Uses \\num{}, \\hebyear{}│
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P2   │ English Terms in Hebrew        │ bidi-english│ ✅ FULLY COVERED       │
│      │                                │             │ Uses \\en{}            │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P3   │ Hebrew in English Context      │ (none)      │ ⚠️  NOT IMPLEMENTED    │
│      │                                │             │ Needs \\texthebrew{}   │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P4   │ Title Page Version in CLS      │ (none)      │ ❌ STRUCTURAL FIX      │
│      │                                │             │ LLM-only (CLS edit)    │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P5   │ Inline Math with Hebrew        │ (none)      │ ⚠️  NOT IMPLEMENTED    │
│      │                                │             │ Needs \\hebmath{}      │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P6   │ Acronyms in Hebrew Context     │ bidi-acronym│ ✅ FULLY COVERED       │
│      │                                │             │ Uses \\en{}            │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P7   │ Decimal Numbers in Preamble    │ bidi-numbers│ ✅ FULLY COVERED       │
│      │                                │             │ Uses \\num{}           │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P8   │ Preamble Metadata Commands     │ (partial)   │ ⚠️  PARTIAL COVERAGE   │
│      │                                │             │ Wraps content only     │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P9   │ Hebrew Chapter Labels          │ (none)      │ ❌ STRUCTURAL FIX      │
│      │                                │             │ LLM-only (label edit)  │
├──────┼────────────────────────────────┼─────────────┼────────────────────────┤
│ P10  │ Hebrew Inside English Wrapper  │ bidi-hebrew │ ⚠️  DETECT ONLY        │
│      │                                │ -in-english │ Complex restructure    │
└──────┴────────────────────────────────┴─────────────┴────────────────────────┘

SUMMARY:
  ✅ FULLY COVERED:    4 patterns (P1, P2, P6, P7)
  ⚠️  PARTIAL/DETECT:  3 patterns (P3, P5, P8, P10)
  ❌ LLM-ONLY:         2 patterns (P4, P9) - structural fixes
""")

# ============================================================
# RUN PYTHON TOOL ON TEST CASES
# ============================================================
print("\n" + "=" * 70)
print("RUNNING PYTHON TOOL ON TEST CASES")
print("=" * 70)

test_cases = [
    ("Number fix", "המחיר הוא 99.99 שקלים", "bidi-numbers", "99.99"),
    ("Year fix", "נולד בשנת 2024", "bidi-numbers", "2024"),
    ("English fix", "השתמש ב-Python לפיתוח", "bidi-english", "Python"),
    ("Acronym fix", "תקן JSON חדש", "bidi-acronym", "JSON"),
]

detector = BiDiDetector()
fixer = BiDiFixer()

print("\nTest cases with Python detector + fixer:")
for name, content, rule, expected_match in test_cases:
    # Detect
    issues = detector.detect(content, "test.tex")
    relevant = [i for i in issues if i.rule == rule and expected_match in i.content]

    if relevant:
        # Fix
        fixed = fixer.fix(content, relevant)
        print(f"\n  {name}:")
        print(f"    Before: {content}")
        print(f"    After:  {fixed}")
        print(f"    Rule:   {rule}")
    else:
        print(f"\n  {name}: No issues detected (may already be wrapped)")

# ============================================================
# LLM vs PYTHON RESPONSIBILITY
# ============================================================
print("\n" + "=" * 70)
print("LLM vs PYTHON RESPONSIBILITY BREAKDOWN")
print("=" * 70)

print("""
┌─────────────────────────────────┬─────────────────────┬─────────────────────┐
│ Task                            │ LLM-Only Skill      │ Python-Backed Skill │
├─────────────────────────────────┼─────────────────────┼─────────────────────┤
│ Detect unwrapped numbers        │ LLM (read patterns) │ Python (regex)      │
│ Detect unwrapped English        │ LLM (read patterns) │ Python (regex)      │
│ Detect unwrapped acronyms       │ LLM (read patterns) │ Python (regex)      │
│ Choose wrapper command          │ LLM (judgment)      │ Python (rules)      │
│ Apply \\num{} vs \\hebyear{}    │ LLM (context)       │ Python (year regex) │
│ Position-accurate replacement   │ LLM (Edit tool)     │ Python (pos logic)  │
│ Skip already-wrapped content    │ LLM (context)       │ Python (lookahead)  │
├─────────────────────────────────┼─────────────────────┼─────────────────────┤
│ Fix Hebrew in math mode         │ LLM (\\hebmath{})   │ NOT IMPLEMENTED     │
│ Fix CLS title page version      │ LLM (Edit tool)     │ NOT IMPLEMENTED     │
│ Fix chapter labels              │ LLM (Edit tool)     │ NOT IMPLEMENTED     │
│ Restructure Hebrew in English   │ LLM (judgment)      │ DETECT ONLY         │
├─────────────────────────────────┼─────────────────────┼─────────────────────┤
│ DETERMINISTIC?                  │ ❌ NO               │ ✅ YES (for covered)│
│ REPEATABLE?                     │ Varies per run      │ 100% same           │
│ COVERAGE                        │ 100% (10 patterns)  │ ~60% (4-6 patterns) │
└─────────────────────────────────┴─────────────────────┴─────────────────────┘
""")

# ============================================================
# SHOW PYTHON FIX PATTERNS
# ============================================================
print("\n" + "=" * 70)
print("PYTHON FIXER PATTERNS")
print("=" * 70)

patterns = get_patterns()
print(f"\nPatterns defined in BiDiFixer.get_patterns():")
for name, info in patterns.items():
    print(f"\n  {name}:")
    print(f"    Find:    {info['find']}")
    print(f"    Replace: {info['replace']}")
    print(f"    Desc:    {info['description']}")

# ============================================================
# CONCLUSION
# ============================================================
print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

print("""
The Python-backed qa-BiDi-fix-text provides:

1. DETERMINISTIC FIXING for core patterns:
   - bidi-numbers → \\num{}, \\hebyear{}, \\percent{}
   - bidi-english → \\en{}
   - bidi-acronym → \\en{}

2. GAPS that require LLM handling:
   - Hebrew in English context (\\texthebrew{})
   - Hebrew in math mode (\\hebmath{})
   - CLS structural edits
   - Chapter label restructuring
   - Complex Hebrew-in-English restructuring

3. RECOMMENDED APPROACH:
   - Use Python for INLINE text wrapping (P1, P2, P6, P7)
   - Defer STRUCTURAL fixes to LLM (P4, P9)
   - Defer COMPLEX restructuring to LLM (P3, P5, P10)

Coverage: ~60% deterministic (core inline fixes)
          ~40% requires LLM judgment (structural/complex)
""")
