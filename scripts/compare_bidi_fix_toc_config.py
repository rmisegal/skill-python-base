"""
Compare: Original qa-BiDi-fix-toc-config (LLM-only) vs Python-backed skills

This demonstrates that qa-BiDi-fix-toc-config is a STRUCTURAL CLS FIX skill
that has NO Python-backed equivalent in skill-python-base.

The skill handles TOC (Table of Contents) BiDi counter configuration which
requires understanding LaTeX macro internals - best suited for LLM.
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("=" * 70)
print("COMPARISON: qa-BiDi-fix-toc-config (LLM-only)")
print("=" * 70)

# ============================================================
# SKILL FILE ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("SKILL FILE ANALYSIS")
print("=" * 70)

llm_skill = Path(r"C:\Users\gal-t\.claude\skills\qa-BiDi-fix-toc-config\skill.md")
llm_lines = len(llm_skill.read_text(encoding="utf-8").split("\n"))

print(f"\n1. ORIGINAL SKILL: qa-BiDi-fix-toc-config (LLM-only)")
print(f"   Location: {llm_skill.parent}")
print(f"   skill.md: {llm_lines} lines of fix patterns")
print(f"   tool.py: NONE (all work done by LLM)")
print(f"   Type: CLS STRUCTURAL FIXES (macro definitions)")

print(f"\n2. PYTHON-BACKED EQUIVALENT: NONE EXISTS")
print(f"   Status: NOT IMPLEMENTED in skill-python-base")
print(f"   Reason: Requires LaTeX macro understanding")

# ============================================================
# FIX PATTERNS IN ORIGINAL SKILL
# ============================================================
print("\n" + "=" * 70)
print("FIX PATTERNS IN ORIGINAL SKILL")
print("=" * 70)

print("""
┌──────────────────────────────────────────────────────────────────────────────┐
│ qa-BiDi-fix-toc-config (LLM-ONLY) - 3 CLS FIX PATTERNS                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Pattern 1: ADD MISSING \\thechapter DEFINITION                               │
│ ─────────────────────────────────────────────────────────────────────────────│
│ Problem:  TOC chapter numbers render reversed in RTL context                 │
│ Location: CLS file                                                           │
│ Fix:      Add \\renewcommand{\\thechapter}{\\textenglish{\\arabic{chapter}}} │
│                                                                              │
│ Pattern 2: REMOVE DOUBLE-WRAPPING FROM \\numberline                          │
│ ─────────────────────────────────────────────────────────────────────────────│
│ Problem:  \\numberline adds \\textenglish{} but counters already have it     │
│ Location: CLS file ~line 642                                                 │
│ Fix:      Remove \\textenglish{#1} from \\numberline redefinition            │
│                                                                              │
│ Pattern 3: ENSURE CONSISTENT COUNTER WRAPPERS                                │
│ ─────────────────────────────────────────────────────────────────────────────│
│ Problem:  Some counters have \\textenglish{}, others don't                   │
│ Location: CLS file counter definitions                                       │
│ Fix:      Add \\textenglish{} wrapper to all counter definitions             │
│           - \\thechapter                                                     │
│           - \\thesection                                                     │
│           - \\thesubsection                                                  │
│           - \\thesubsubsection                                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
""")

# ============================================================
# WHY NO PYTHON EQUIVALENT?
# ============================================================
print("\n" + "=" * 70)
print("WHY NO PYTHON EQUIVALENT?")
print("=" * 70)

print("""
┌──────────────────────────────────────────────────────────────────────────────┐
│ ANALYSIS: Can qa-BiDi-fix-toc-config be Python-backed?                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Pattern 1: Add \\thechapter                                                  │
│   Python Detection:  YES - regex can find missing definition                 │
│   Python Fix:        PARTIAL - can insert, but WHERE? Context needed         │
│   Verdict:           ⚠️ LLM better (knows CLS structure)                     │
│                                                                              │
│ Pattern 2: Remove \\numberline double-wrapping                               │
│   Python Detection:  YES - regex can find \\textenglish{#1}                  │
│   Python Fix:        NO - requires understanding if counters have wrappers   │
│   Verdict:           ❌ LLM REQUIRED (semantic understanding)                │
│                                                                              │
│ Pattern 3: Consistent counter wrappers                                       │
│   Python Detection:  PARTIAL - can find inconsistencies                      │
│   Python Fix:        NO - nested macro syntax is complex                     │
│   Verdict:           ❌ LLM REQUIRED (LaTeX macro expertise)                 │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ CONCLUSION: qa-BiDi-fix-toc-config should remain LLM-ONLY                    │
│                                                                              │
│ Reasons:                                                                     │
│ 1. Modifies CLS file macro definitions (\\renewcommand)                      │
│ 2. Requires understanding LaTeX expansion order                              │
│ 3. Must analyze counter format nesting (\\arabic{} inside \\textenglish{})   │
│ 4. Fix location depends on CLS file structure                                │
│ 5. Version bump requires semantic understanding                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
""")

# ============================================================
# RELATED PYTHON-BACKED SKILLS
# ============================================================
print("\n" + "=" * 70)
print("RELATED PYTHON-BACKED SKILLS (NOT EQUIVALENT)")
print("=" * 70)

print("""
┌────────────────────────────┬─────────────────────────────────────────────────┐
│ Python Skill               │ What it does vs qa-BiDi-fix-toc-config          │
├────────────────────────────┼─────────────────────────────────────────────────┤
│ qa-cls-version-detect      │ Compares CLS versions (not TOC fixes)           │
│ qa-cls-version-fix         │ Copies entire reference CLS (not patching)      │
│ qa-BiDi-fix-text           │ Wraps inline text (not CLS macros)              │
│ qa-BiDi-fix-sections       │ Section fixes (not TOC numberline)              │
├────────────────────────────┼─────────────────────────────────────────────────┤
│ NONE                       │ Patches specific CLS macro definitions          │
└────────────────────────────┴─────────────────────────────────────────────────┘

Alternative approach: Use qa-cls-version-fix to replace CLS with reference
that already has TOC fixes applied (v5.11.3+)
""")

# ============================================================
# LLM vs PYTHON RESPONSIBILITY
# ============================================================
print("\n" + "=" * 70)
print("LLM vs PYTHON RESPONSIBILITY")
print("=" * 70)

print("""
┌─────────────────────────────────┬─────────────────────┬─────────────────────┐
│ Task                            │ LLM-Only Skill      │ Python-Backed       │
├─────────────────────────────────┼─────────────────────┼─────────────────────┤
│ Find CLS file                   │ LLM (Glob tool)     │ N/A                 │
│ Parse \\thechapter definition   │ LLM (Read + logic)  │ N/A                 │
│ Analyze counter nesting         │ LLM (LaTeX expert)  │ N/A                 │
│ Detect double-wrapping          │ LLM (context)       │ N/A                 │
│ Determine fix location          │ LLM (CLS structure) │ N/A                 │
│ Insert \\renewcommand           │ LLM (Edit tool)     │ N/A                 │
│ Remove \\textenglish from line  │ LLM (Edit tool)     │ N/A                 │
│ Update CLS version number       │ LLM (Edit tool)     │ N/A                 │
│ Verify fix correctness          │ LLM (compile test)  │ N/A                 │
├─────────────────────────────────┼─────────────────────┼─────────────────────┤
│ CAN BE PYTHON-BACKED?           │ N/A                 │ ❌ NO               │
│ REASON                          │ N/A                 │ LaTeX macro         │
│                                 │                     │ understanding       │
└─────────────────────────────────┴─────────────────────┴─────────────────────┘
""")

# ============================================================
# EXAMPLE CLS FIX
# ============================================================
print("\n" + "=" * 70)
print("EXAMPLE: WHAT THE LLM SKILL DOES")
print("=" * 70)

print("""
BEFORE (problematic CLS v5.11.2):
─────────────────────────────────────────────────────────────────────────────
% Section numbering - always LTR
\\renewcommand{\\thesection}{\\textenglish{\\arabic{section}}}
\\renewcommand{\\thesubsection}{\\textenglish{\\arabic{section}.\\arabic{subsection}}}

% ... later in file ...

% Store original numberline and redefine for LTR numbers
\\let\\orig@numberline\\numberline
\\renewcommand{\\numberline}[1]{\\orig@numberline{\\textenglish{#1}}}
─────────────────────────────────────────────────────────────────────────────

AFTER (fixed CLS v5.11.3):
─────────────────────────────────────────────────────────────────────────────
% Chapter numbering - always LTR (v5.11.3 fix for TOC BiDi)
\\renewcommand{\\thechapter}{\\textenglish{\\arabic{chapter}}}

% Section numbering - always LTR
\\renewcommand{\\thesection}{\\textenglish{\\arabic{section}}}
\\renewcommand{\\thesubsection}{\\textenglish{\\arabic{section}.\\arabic{subsection}}}

% ... later in file ...

% Store original numberline - DO NOT add \\textenglish wrapper here
% because counter definitions already include \\textenglish{}
% Double-wrapping causes BiDi rendering issues in TOC
\\let\\orig@numberline\\numberline
% Keep original numberline behavior - section counters handle LTR
─────────────────────────────────────────────────────────────────────────────

WHY LLM IS NEEDED:
1. Knows to add \\thechapter BEFORE \\thesection (logical order)
2. Understands that double-wrapping causes issues
3. Adds explanatory comments for future maintainers
4. Updates version number appropriately
""")

# ============================================================
# RECOMMENDATION
# ============================================================
print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)

print("""
┌──────────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION: Keep qa-BiDi-fix-toc-config as LLM-ONLY                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ 1. This skill handles CLS macro modifications requiring LaTeX expertise      │
│                                                                              │
│ 2. Python alternative: Use qa-cls-version-fix to copy reference CLS          │
│    that already has TOC fixes applied (simpler, more reliable)               │
│                                                                              │
│ 3. Detection CAN be Python-backed:                                           │
│    - Add rule to detect missing \\thechapter with \\textenglish{}            │
│    - Add rule to detect \\numberline with \\textenglish{#1}                  │
│                                                                              │
│ 4. Fixing MUST remain LLM:                                                   │
│    - Requires understanding CLS structure                                    │
│    - Requires semantic knowledge of LaTeX macro expansion                    │
│    - Fix location is context-dependent                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

SUMMARY:
  qa-BiDi-fix-toc-config: 100% LLM-ONLY (no Python equivalent)
  Detection: Could add Python rules for detection phase
  Fixing: Must remain LLM (LaTeX macro expertise required)
""")
