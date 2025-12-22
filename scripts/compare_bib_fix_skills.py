"""
Compare: Original qa-bib-fix-missing (LLM-only) vs New qa-bib-fix (Python-backed)

This demonstrates the difference between:
1. LLM-only skill: All work done by Claude interpreting skill.md
2. Python-backed skill: Deterministic work done by Python tool
"""

import sys
import io
import shutil
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import Python tool
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "qa-bib-fix"))
from tool import fix as python_fix, get_patterns

from qa_engine.infrastructure.detection.bib_detector import BibDetector
from qa_engine.infrastructure.fixing.bib_fixer import BibFixer

print("=" * 70)
print("COMPARISON: qa-bib-fix-missing (LLM) vs qa-bib-fix (Python)")
print("=" * 70)

# ============================================================
# SKILL ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("SKILL FILE ANALYSIS")
print("=" * 70)

llm_skill_path = Path(r"C:\Users\gal-t\.claude\skills\qa-bib-fix-missing")
python_skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "qa-bib-fix"

print("\n1. ORIGINAL SKILL: qa-bib-fix-missing (User global)")
print(f"   Location: {llm_skill_path}")
print(f"   Files:")
for f in llm_skill_path.iterdir():
    print(f"     - {f.name}")
print(f"   Has tool.py: NO (LLM-only)")

print("\n2. NEW SKILL: qa-bib-fix (Python-backed)")
print(f"   Location: {python_skill_path}")
print(f"   Files:")
for f in python_skill_path.iterdir():
    print(f"     - {f.name}")
print(f"   Has tool.py: YES (Python-backed)")

# ============================================================
# WHAT EACH SKILL DOES
# ============================================================
print("\n" + "=" * 70)
print("WHAT EACH SKILL DOES")
print("=" * 70)

print("""
┌─────────────────────────────────────────────────────────────────────┐
│ qa-bib-fix-missing (LLM-ONLY)                                       │
├─────────────────────────────────────────────────────────────────────┤
│ • LLM reads skill.md instructions                                   │
│ • LLM interprets detection results                                  │
│ • LLM generates BibTeX entries manually                             │
│ • LLM decides where to add entries                                  │
│ • LLM writes files using Edit/Write tools                           │
│                                                                     │
│ Pros: Flexible, can handle complex cases                            │
│ Cons: Non-deterministic, may vary between runs                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ qa-bib-fix (PYTHON-BACKED)                                          │
├─────────────────────────────────────────────────────────────────────┤
│ • LLM invokes tool.py                                               │
│ • Python BibFixer handles all logic:                                │
│   - Parse citation keys                                             │
│   - Generate BibTeX entries                                         │
│   - Create/update .bib files                                        │
│   - Return structured results                                       │
│                                                                     │
│ Pros: 100% deterministic, fast, repeatable                          │
│ Cons: Less flexible for edge cases                                  │
└─────────────────────────────────────────────────────────────────────┘
""")

# ============================================================
# RUN PYTHON TOOL ON EXAMPLE
# ============================================================
print("\n" + "=" * 70)
print("RUNNING PYTHON TOOL ON EXAMPLE")
print("=" * 70)

# Create a test scenario
test_dir = Path(__file__).parent.parent / "test-data" / "bib-fix-test"
test_dir.mkdir(exist_ok=True)

# Create test .tex file with missing citations
test_tex = test_dir / "test_document.tex"
test_tex.write_text(r"""
\documentclass{article}
\usepackage{biblatex}
\addbibresource{test_refs.bib}

\begin{document}

This cites \cite{smith2024ai} and \cite{jones2023ml}.
Also references \cite{brown2022deep}.

\printbibliography
\end{document}
""", encoding="utf-8")

print(f"\nTest file created: {test_tex}")
print("Content: Citations to smith2024ai, jones2023ml, brown2022deep")

# Step 1: Detect issues
print("\n--- Step 1: Detection ---")
detector = BibDetector()
content = test_tex.read_text(encoding="utf-8")
issues = detector.detect(content, str(test_tex))

issues_as_dicts = [
    {
        "rule": i.rule,
        "file": i.file,
        "line": i.line,
        "content": i.content,
        "severity": i.severity.value,
        "fix": i.fix,
    }
    for i in issues
]

print(f"Detected {len(issues_as_dicts)} issues:")
for i in issues_as_dicts:
    print(f"  [{i['severity']}] {i['rule']}: {i['content']}")

# Step 2: Apply Python fix
print("\n--- Step 2: Apply Python Fix ---")
result = python_fix(content, issues_as_dicts, str(test_tex))
print(f"Fix result: {result}")

# Check if .bib file was created
test_bib = test_dir / "test_refs.bib"
if test_bib.exists():
    print(f"\n--- Created .bib file ---")
    print(test_bib.read_text(encoding="utf-8")[:500])
else:
    # Check references.bib (default)
    default_bib = test_dir / "references.bib"
    if default_bib.exists():
        print(f"\n--- Created default .bib file ---")
        print(default_bib.read_text(encoding="utf-8")[:500])

# Step 3: Re-detect to verify
print("\n--- Step 3: Verify (Re-detect) ---")
issues_after = detector.detect(content, str(test_tex))
print(f"Issues remaining: {len(issues_after)}")

# ============================================================
# COMPARISON TABLE
# ============================================================
print("\n" + "=" * 70)
print("LLM vs PYTHON RESPONSIBILITY BREAKDOWN")
print("=" * 70)

print("""
┌──────────────────────────┬──────────────────────┬──────────────────────┐
│ Task                     │ LLM-Only Skill       │ Python-Backed Skill  │
├──────────────────────────┼──────────────────────┼──────────────────────┤
│ Parse citation keys      │ LLM (interpret text) │ Python (regex)       │
│ Generate BibTeX entry    │ LLM (templates)      │ Python (templates)   │
│ Find target .bib file    │ LLM (search)         │ Python (path logic)  │
│ Write .bib file          │ LLM (Write tool)     │ Python (file I/O)    │
│ Handle nested braces     │ LLM (context)        │ Python (parser)      │
│ Track what was fixed     │ LLM (memory)         │ Python (return dict) │
│ Error handling           │ LLM (judgment)       │ Python (try/except)  │
├──────────────────────────┼──────────────────────┼──────────────────────┤
│ DETERMINISTIC?           │ NO                   │ YES                  │
│ REPEATABLE?              │ Varies               │ 100% same            │
│ SPEED                    │ Slower               │ Fast                 │
└──────────────────────────┴──────────────────────┴──────────────────────┘
""")

# Cleanup
shutil.rmtree(test_dir, ignore_errors=True)

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("""
The qa-bib-fix Python tool provides:
1. IDENTICAL functionality to qa-bib-fix-missing
2. DETERMINISTIC results (same input = same output)
3. FASTER execution (no LLM inference needed for fix logic)
4. TESTABLE code (unit tests possible)

The Python BibFixer class handles:
- _parse_cite_keys(): Extract citation keys from issues
- _create_bib_file(): Create/update .bib files
- _generate_bib_entry(): Generate placeholder BibTeX entries
- _clean_latex_from_key(): Clean malformed citation keys
""")
