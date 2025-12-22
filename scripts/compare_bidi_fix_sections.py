"""
Compare: Original qa-BiDi-fix-sections (LLM-only) vs Python-backed skills

This demonstrates the difference between:
1. qa-BiDi-fix-sections: Handles STRUCTURAL fixes (CLS, preamble, titleformat)
2. qa-BiDi-fix-text: Handles INLINE text wrapping (numbers, English, acronyms)

KEY FINDING: These skills handle DIFFERENT types of fixes!
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("=" * 70)
print("COMPARISON: qa-BiDi-fix-sections (LLM) vs qa-BiDi-fix-text (Python)")
print("=" * 70)

# ============================================================
# SKILL FILE ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("SKILL FILE ANALYSIS")
print("=" * 70)

llm_skill = Path(r"C:\Users\gal-t\.claude\skills\qa-BiDi-fix-sections\skill.md")
python_skill = Path(__file__).parent.parent / ".claude" / "skills" / "qa-BiDi-fix-text"

llm_lines = len(llm_skill.read_text(encoding="utf-8").split("\n"))
python_lines = len((python_skill / "skill.md").read_text(encoding="utf-8").split("\n"))
tool_lines = len((python_skill / "tool.py").read_text(encoding="utf-8").split("\n"))

print(f"\n1. ORIGINAL SKILL: qa-BiDi-fix-sections (LLM-only)")
print(f"   Location: {llm_skill.parent}")
print(f"   skill.md: {llm_lines} lines of LLM instructions")
print(f"   tool.py: NONE (all work done by LLM)")
print(f"   Type: STRUCTURAL fixes (CLS definitions, preamble commands)")

print(f"\n2. PYTHON SKILL: qa-BiDi-fix-text (Python-backed)")
print(f"   Location: {python_skill}")
print(f"   skill.md: {python_lines} lines (reference to Python)")
print(f"   tool.py: {tool_lines} lines (wrapper)")
print(f"   Type: INLINE fixes (text wrapping with \\en{{}}, \\num{{}})")

# ============================================================
# WHAT EACH SKILL FIXES
# ============================================================
print("\n" + "=" * 70)
print("PROBLEM TYPES COMPARISON")
print("=" * 70)

print("""
┌─────────────────────────────────────────────────────────────────────────┐
│ qa-BiDi-fix-sections (LLM-ONLY) - STRUCTURAL FIXES                      │
├─────────────────────────────────────────────────────────────────────────┤
│ Problem 1: Section Numbering Starts from 0                              │
│   Location: CLS file (~line 358)                                        │
│   Fix: Modify \\thehebrewsection definition with \\ifnum conditional    │
│                                                                         │
│ Problem 2: Section Numbers Render RTL (1.2 → 2.1)                       │
│   Location: Document preamble                                           │
│   Fix: \\renewcommand{\\thesection}{\\textenglish{...}}                 │
│                                                                         │
│ Problem 3: Standalone Chapter Wrong Number                              │
│   Location: Standalone .tex file                                        │
│   Fix: \\setcounter{chapter}{N-1} before \\chapter{}                    │
│                                                                         │
│ Problem 4: TOC Shows Wrong Numbers                                      │
│   Location: Document preamble                                           │
│   Fix: \\addtocontents{toc}{\\protect\\renewcommand...}                 │
│                                                                         │
│ Problem 5: titleformat Numbers Render RTL                               │
│   Location: After \\usepackage{titlesec}                                │
│   Fix: Wrap \\thesection in \\textenglish{} within \\titleformat        │
│                                                                         │
│ HOW IT WORKS: LLM reads instructions, finds relevant commands,          │
│ understands LaTeX structure, applies appropriate structural changes.    │
│ REQUIRES: Understanding LaTeX definitions, CLS file structure           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ qa-BiDi-fix-text (PYTHON-BACKED) - INLINE FIXES                         │
├─────────────────────────────────────────────────────────────────────────┤
│ Pattern 1: wrap-number                                                  │
│   Fix: 123 → \\num{123} or \\hebyear{2024}                             │
│                                                                         │
│ Pattern 2: wrap-english                                                 │
│   Fix: test → \\en{test}                                               │
│                                                                         │
│ Pattern 3: wrap-acronym                                                 │
│   Fix: API → \\en{API}                                                 │
│                                                                         │
│ HOW IT WORKS: Python regex finds unwrapped content, applies wrapper.    │
│ REQUIRES: Just pattern matching - no structural understanding needed.   │
└─────────────────────────────────────────────────────────────────────────┘
""")

# ============================================================
# LLM vs PYTHON RESPONSIBILITY
# ============================================================
print("\n" + "=" * 70)
print("LLM vs PYTHON RESPONSIBILITY")
print("=" * 70)

print("""
┌────────────────────────────┬────────────────────────┬────────────────────────┐
│ Task                       │ qa-BiDi-fix-sections   │ qa-BiDi-fix-text       │
│                            │ (LLM-ONLY)             │ (Python-backed)        │
├────────────────────────────┼────────────────────────┼────────────────────────┤
│ Understand CLS structure   │ LLM                    │ N/A (not needed)       │
│ Parse \\renewcommand       │ LLM                    │ N/A (not needed)       │
│ Modify macro definitions   │ LLM (Edit tool)        │ N/A (not needed)       │
│ Find \\titleformat cmds    │ LLM (Grep tool)        │ N/A (not needed)       │
│ Handle counter logic       │ LLM (LaTeX knowledge)  │ N/A (not needed)       │
├────────────────────────────┼────────────────────────┼────────────────────────┤
│ Find unwrapped numbers     │ N/A (different skill)  │ Python (regex)         │
│ Find unwrapped English     │ N/A (different skill)  │ Python (regex)         │
│ Apply inline wrappers      │ N/A (different skill)  │ Python (string ops)    │
├────────────────────────────┼────────────────────────┼────────────────────────┤
│ COMPLEXITY                 │ HIGH (LaTeX knowledge) │ LOW (pattern matching) │
│ DETERMINISTIC              │ Partially (judgement)  │ YES (100% regex)       │
│ CAN BE PYTHON-BACKED?      │ Partially (see below)  │ YES (fully)            │
└────────────────────────────┴────────────────────────┴────────────────────────┘
""")

# ============================================================
# PYTHON BACKING FEASIBILITY
# ============================================================
print("\n" + "=" * 70)
print("CAN qa-BiDi-fix-sections BE PYTHON-BACKED?")
print("=" * 70)

print("""
Analysis of each problem type:

┌─────────────────────────────────────┬─────────────┬──────────────────────────┐
│ Problem                             │ Python-able │ Reason                   │
├─────────────────────────────────────┼─────────────┼──────────────────────────┤
│ P1: \\thehebrewsection definition   │ PARTIALLY   │ Can detect pattern, but  │
│                                     │             │ fix requires judgment    │
├─────────────────────────────────────┼─────────────┼──────────────────────────┤
│ P2: \\renewcommand{\\thesection}    │ YES         │ Regex can find & wrap    │
│     without \\textenglish{}         │             │ with \\textenglish{}     │
├─────────────────────────────────────┼─────────────┼──────────────────────────┤
│ P3: Standalone \\setcounter         │ NO          │ Requires understanding   │
│                                     │             │ which chapter number     │
├─────────────────────────────────────┼─────────────┼──────────────────────────┤
│ P4: TOC \\addtocontents             │ PARTIALLY   │ Can detect missing, but  │
│                                     │             │ insertion needs context  │
├─────────────────────────────────────┼─────────────┼──────────────────────────┤
│ P5: \\titleformat without wrapper   │ YES         │ Regex can find & wrap    │
│                                     │             │ \\thesection in \\textenglish│
└─────────────────────────────────────┴─────────────┴──────────────────────────┘

CONCLUSION:
- Problems 2 and 5 CAN be fully Python-backed (regex find & replace)
- Problems 1, 3, 4 require LLM judgment (context-dependent decisions)
- qa-BiDi-fix-sections remains a HYBRID skill: Python detection + LLM fixing
""")

# ============================================================
# CURRENT PYTHON DETECTION
# ============================================================
print("\n" + "=" * 70)
print("CURRENT PYTHON DETECTION FOR SECTION ISSUES")
print("=" * 70)

from qa_engine.infrastructure.detection.bidi_rules import BIDI_RULES

section_rules = {k: v for k, v in BIDI_RULES.items() if "section" in k.lower()}
print(f"\nSection-related rules in bidi_rules.py: {len(section_rules)}")
for name, rule in section_rules.items():
    print(f"\n  Rule: {name}")
    print(f"    Description: {rule['description']}")
    print(f"    Pattern: {rule['pattern'][:60]}...")

# ============================================================
# RECOMMENDATION
# ============================================================
print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)

print("""
The qa-BiDi-fix-sections skill and qa-BiDi-fix-text skill handle
DIFFERENT TYPES of fixes:

1. qa-BiDi-fix-sections → STRUCTURAL (macro definitions, counters)
   - Best handled by LLM with LaTeX knowledge
   - Can benefit from Python DETECTION but needs LLM for FIXING

2. qa-BiDi-fix-text → INLINE (content wrapping)
   - Fully Python-backed (100% deterministic regex)
   - No LLM needed for fixing logic

TO CREATE A PYTHON-BACKED qa-BiDi-fix-sections:

Option A: Partial Python backing
  - Python tool detects issues (regex patterns)
  - Python applies simple fixes (P2, P5)
  - LLM handles complex fixes (P1, P3, P4)

Option B: Keep as LLM-only with improved detection
  - Use Python detection for finding issues
  - LLM applies all fixes with context awareness
""")
