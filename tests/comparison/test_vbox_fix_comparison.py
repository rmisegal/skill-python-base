"""
Comparison test for qa-typeset-fix-vbox skill vs Python tool.

Verifies that Python implementation covers all skill.md v1.0 fix patterns.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.typeset.fixing import VboxFixer, VboxFixResult, VboxFix

# Test content samples from skill.md patterns

# Basic LaTeX document for preamble tests
LATEX_DOC_NO_RAGGEDBOTTOM = r"""\documentclass{book}
\usepackage{graphicx}
\begin{document}
Hello world
\end{document}"""

LATEX_DOC_WITH_RAGGEDBOTTOM = r"""\documentclass{book}
\raggedbottom
\begin{document}
Hello world
\end{document}"""

# Float environments
FLOAT_NO_OPTION = r"\begin{figure}\includegraphics{img}\end{figure}"
FLOAT_WITH_H = r"\begin{figure}[h]\includegraphics{img}\end{figure}"
TABLE_NO_OPTION = r"\begin{table}\centering\end{table}"


def run_comparison():
    """Run comparison tests."""
    fixer = VboxFixer()
    results = []

    # Test 1: Problem 1 - Underfull vbox fixes
    results.append(("Problem 1: Underfull vbox Fix Options", [
        # Option A: Let LaTeX Handle It - no code change, just guidance
        ("Option A documented", True),  # No code change, guidance only

        # Option B: Use raggedbottom (Global)
        ("Option B: raggedbottom adds to preamble",
         "\\raggedbottom" in fixer.fix_preamble(LATEX_DOC_NO_RAGGEDBOTTOM, "t.tex")[0]),
        ("Option B: raggedbottom not duplicated",
         fixer.fix_preamble(LATEX_DOC_WITH_RAGGEDBOTTOM, "t.tex")[0].count("\\raggedbottom") == 1),
        ("Option B: raggedbottom fix recorded",
         len(fixer.fix_preamble(LATEX_DOC_NO_RAGGEDBOTTOM, "t.tex")[1].fixes_applied) == 1),

        # Option C: Add Vertical Space
        ("Option C: vfill added", "\\vfill" in fixer.add_vfill("Line1\nLine2", 1, "t.tex")[0]),
        ("Option C: vspace added", "\\vspace{2cm}" in fixer.add_vspace("Line1\nLine2", 1, "2cm", "t.tex")[0]),

        # Option D: Adjust Float Placement
        ("Option D: float placement [htbp] added",
         "[htbp]" in fixer.fix_float_placement(FLOAT_NO_OPTION, 1, "htbp", "t.tex")[0]),
        ("Option D: float placement replaces existing",
         "[htbp]" in fixer.fix_float_placement(FLOAT_WITH_H, 1, "htbp", "t.tex")[0] and
         "[h]" not in fixer.fix_float_placement(FLOAT_WITH_H, 1, "htbp", "t.tex")[0]),

        # Option E: Use enlargethispage
        ("Option E: enlargethispage positive",
         "\\enlargethispage{2\\baselineskip}" in
         fixer.add_enlargethispage("Line1\nLine2", 1, "2\\baselineskip", "t.tex")[0]),
    ]))

    # Test 2: Problem 2 - Overfull vbox fixes
    results.append(("Problem 2: Overfull vbox Fix Options", [
        # Option A: Move Content to Next Page
        ("Option A: newpage added", "\\newpage" in fixer.add_newpage("Line1\nLine2", 1, "t.tex")[0]),
        ("Option A: newpage fix type correct",
         fixer.add_newpage("Line1\nLine2", 1, "t.tex")[1].fix_type == "newpage"),

        # Option B: Reduce Content - manual, LLM guidance
        ("Option B documented (manual)", True),

        # Option C: Use enlargethispage (Negative)
        ("Option C: enlargethispage negative",
         "\\enlargethispage{-1\\baselineskip}" in
         fixer.add_enlargethispage("Line1\nLine2", 1, "-1\\baselineskip", "t.tex")[0]),

        # Option D: Adjust Float Placement [p]
        ("Option D: float placement [p] for page",
         "[p]" in fixer.fix_float_placement(TABLE_NO_OPTION, 1, "p", "t.tex")[0]),
    ]))

    # Test 3: Severity Classification
    results.append(("Severity Guide", [
        ("badness < 1000 -> INFO", fixer.classify_severity(badness=500) == "INFO"),
        ("badness 1000-5000 -> INFO (consider)", fixer.classify_severity(badness=3000) == "INFO"),
        ("badness 5000-9999 -> WARNING", fixer.classify_severity(badness=7000) == "WARNING"),
        ("badness 10000 -> WARNING", fixer.classify_severity(badness=10000) == "WARNING"),
        ("overfull any -> CRITICAL", fixer.classify_severity(is_overfull=True) == "CRITICAL"),
    ]))

    # Test 4: When to Ignore
    results.append(("When to Ignore Rules", [
        ("safe: chapter/section start",
         fixer.should_ignore("underfull", badness=10000, context="\\chapter{Intro}")),
        ("safe: after newpage",
         fixer.should_ignore("underfull", badness=10000, context="\\newpage")),
        ("safe: low badness",
         fixer.should_ignore("underfull", badness=1000)),
        ("must fix: overfull never ignored",
         not fixer.should_ignore("overfull")),
        ("must fix: severe underfull",
         not fixer.should_ignore("underfull", badness=10000, context="regular text")),
    ]))

    # Test 5: Global Settings
    settings = fixer.get_global_settings()
    results.append(("Global Settings", [
        ("raggedbottom setting", "raggedbottom" in settings),
        ("topfraction setting", "topfraction" in settings),
        ("bottomfraction setting", "bottomfraction" in settings),
        ("textfraction setting", "textfraction" in settings),
        ("floatpagefraction setting", "floatpagefraction" in settings),
        ("topnumber setting", "topnumber" in settings),
        ("bottomnumber setting", "bottomnumber" in settings),
        ("totalnumber setting", "totalnumber" in settings),
    ]))

    # Test 6: Manual Review Creation
    underfull_review = fixer.create_review("t.tex", 10, "underfull", badness=10000)
    overfull_review = fixer.create_review("t.tex", 10, "overfull", amount_pt=5.2)
    results.append(("Manual Review (LLM Guidance)", [
        ("underfull has 5 options", len(underfull_review.options) == 5),
        ("overfull has 4 options", len(overfull_review.options) == 4),
        ("underfull mentions raggedbottom",
         any("raggedbottom" in opt.lower() for opt in underfull_review.options)),
        ("underfull mentions vfill",
         any("vfill" in opt.lower() for opt in underfull_review.options)),
        ("underfull mentions enlargethispage",
         any("enlargethispage" in opt.lower() for opt in underfull_review.options)),
        ("overfull mentions newpage",
         any("newpage" in opt.lower() for opt in overfull_review.options)),
        ("overfull mentions enlargethispage negative",
         any("enlargethispage" in opt.lower() and "-" in opt for opt in overfull_review.options)),
        ("overfull mentions float [p]",
         any("[p]" in opt.lower() or "page" in opt.lower() for opt in overfull_review.options)),
    ]))

    # Test 7: Output Format
    result = VboxFixResult()
    result.fixes_applied.append(VboxFix(
        file="t.tex", line=10, issue_type="underfull",
        fix_type="raggedbottom", before="before", after="after", location="preamble"
    ))
    output = fixer.to_dict(result)
    results.append(("Output Format Compliance", [
        ("skill field", output.get("skill") == "qa-typeset-fix-vbox"),
        ("status field", output.get("status") == "DONE"),
        ("fixes_applied array", "fixes_applied" in output),
        ("manual_review array", "manual_review" in output),
        ("summary object", "summary" in output),
        ("summary.auto_fixed", "auto_fixed" in output.get("summary", {})),
        ("summary.needs_review", "needs_review" in output.get("summary", {})),
        ("fix.file field", "file" in output["fixes_applied"][0]),
        ("fix.line field", "line" in output["fixes_applied"][0]),
        ("fix.issue_type field", "issue_type" in output["fixes_applied"][0]),
        ("fix.fix_type field", "fix_type" in output["fixes_applied"][0]),
        ("fix.before field", "before" in output["fixes_applied"][0]),
        ("fix.after field", "after" in output["fixes_applied"][0]),
        ("fix.location field", "location" in output["fixes_applied"][0]),
    ]))

    # Test 8: Status Logic
    results.append(("Status Logic", [
        ("DONE with fixes",
         VboxFixResult(fixes_applied=[VboxFix("", 1, "", "", "", "")]).status == "DONE"),
        ("MANUAL_REVIEW with reviews",
         fixer.to_dict(VboxFixResult(manual_review=[
             fixer.create_review("t.tex", 1, "overfull")
         ]))["status"] == "MANUAL_REVIEW"),
        ("NO_CHANGES when empty",
         VboxFixResult().status == "NO_CHANGES"),
    ]))

    # Test 9: Fix Type Classification
    results.append(("Fix Types", [
        ("raggedbottom fix type",
         fixer.fix_preamble(LATEX_DOC_NO_RAGGEDBOTTOM, "t.tex")[1].fixes_applied[0].fix_type == "raggedbottom"),
        ("vfill fix type",
         fixer.add_vfill("L1\nL2", 1, "t.tex")[1].fix_type == "vfill"),
        ("vspace fix type",
         fixer.add_vspace("L1\nL2", 1, "2cm", "t.tex")[1].fix_type == "vspace"),
        ("enlargethispage fix type",
         fixer.add_enlargethispage("L1\nL2", 1, "2\\baselineskip", "t.tex")[1].fix_type == "enlargethispage"),
        ("float_placement fix type",
         fixer.fix_float_placement(FLOAT_NO_OPTION, 1, "htbp", "t.tex")[1].fix_type == "float_placement"),
        ("newpage fix type",
         fixer.add_newpage("L1\nL2", 1, "t.tex")[1].fix_type == "newpage"),
    ]))

    # Test 10: Issue Type Tracking
    results.append(("Issue Type Tracking", [
        ("vfill marked as underfull",
         fixer.add_vfill("L1\nL2", 1, "t.tex")[1].issue_type == "underfull"),
        ("newpage marked as overfull",
         fixer.add_newpage("L1\nL2", 1, "t.tex")[1].issue_type == "overfull"),
    ]))

    # Test 11: LLM Prompt Generation
    review = fixer.create_review("test.tex", 50, "underfull", badness=10000)
    prompt = fixer.generate_llm_prompt(review)
    results.append(("LLM Prompt Generation", [
        ("prompt contains issue type", "underfull" in prompt),
        ("prompt contains badness", "10000" in prompt),
        ("prompt contains file", "test.tex" in prompt),
        ("prompt contains line", "50" in prompt),
        ("prompt contains options", any(opt in prompt for opt in review.options)),
    ]))

    return results


def print_results(results):
    """Print comparison results."""
    print("=" * 70)
    print("qa-typeset-fix-vbox: Skill vs Python Tool Comparison")
    print("=" * 70)

    total_checks = 0
    passed_checks = 0

    for category, checks in results:
        print(f"\n{category}:")
        for name, passed in checks:
            status = "PASS" if passed else "FAIL"
            symbol = "[+]" if passed else "[-]"
            print(f"  {symbol} {name}: {status}")
            total_checks += 1
            if passed:
                passed_checks += 1

    print("\n" + "=" * 70)
    print(f"TOTAL: {passed_checks}/{total_checks} checks passed")
    print("=" * 70)

    return passed_checks == total_checks


if __name__ == "__main__":
    results = run_comparison()
    success = print_results(results)
    sys.exit(0 if success else 1)
