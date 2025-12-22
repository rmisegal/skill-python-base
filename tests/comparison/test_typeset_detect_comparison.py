"""
Comparison test for qa-typeset-detect skill vs Python tool.

Verifies that Python implementation covers all skill.md v1.5 detection criteria.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.typeset.detection import (
    LogWarningDetector, TikzDetector, ItemsepDetector, FullTypesetDetector
)

# Test content samples from skill.md patterns

# Log file samples - use raw strings for backslashes
LOG_OVERFULL_HBOX = r"Overfull \hbox (4.90633pt too wide) in paragraph at lines 162--163"
LOG_OVERFULL_HBOX_CRITICAL = r"Overfull \hbox (15.5pt too wide) in paragraph at lines 100--101"
LOG_UNDERFULL_HBOX = r"Underfull \hbox (badness 10000) in paragraph at lines 45--46"
LOG_UNDERFULL_VBOX = r"Underfull \vbox (badness 10000) has occurred while \output is active"
LOG_OVERFULL_VBOX = r"Overfull \vbox (10.0pt too high) has occurred"
LOG_UNDEFINED_REF = r"LaTeX Warning: Reference `tab:python-libraries' on page 27 undefined on input line 185."
LOG_UNDEFINED_CITATION = r"LaTeX Warning: Citation `smith2020' on page 5 undefined on input line 42."
LOG_FLOAT_TOO_LARGE = r"LaTeX Warning: Float too large for page by 165.89464pt on input line 141."
LOG_FLOAT_SMALL = r"LaTeX Warning: Float too large for page by 30.0pt on input line 50."
LOG_LATEX_ERROR = r"! LaTeX Error: Some unknown error."
LOG_KNOWN_ISSUE = r"! LaTeX Error: \begin{pythonbox} on input line 318 ended by \end{python}."
LOG_PACKAGE_ERROR = r"! Package tcolorbox Error: Some error message."

# TikZ samples
TIKZ_UNSAFE = r"""\begin{tikzpicture}
\draw (0,0) -- (5,5);
\end{tikzpicture}"""

TIKZ_SAFE_RESIZEBOX = r"""\resizebox{\textwidth}{!}{%
\begin{tikzpicture}
\draw (0,0) -- (5,5);
\end{tikzpicture}%
}"""

TIKZ_SAFE_SCALE = r"""\begin{tikzpicture}[scale=0.8]
\draw (0,0) -- (5,5);
\end{tikzpicture}"""

TIKZ_LARGE_COORDS = r"""\begin{tikzpicture}
\draw (15,0) -- (20,10);
\end{tikzpicture}"""

# Itemsep samples
LIST_UNSAFE = r"""\begin{itemize}
\item Item 1
\item Item 2
\end{itemize}"""

LIST_SAFE_NOITEMSEP = r"""\begin{itemize}[noitemsep]
\item Item 1
\item Item 2
\end{itemize}"""

LIST_SAFE_NOSEP = r"""\begin{itemize}[nosep]
\item Item 1
\item Item 2
\end{itemize}"""


def run_comparison():
    """Run comparison tests."""
    log_detector = LogWarningDetector()
    tikz_detector = TikzDetector()
    itemsep_detector = ItemsepDetector()
    full_detector = FullTypesetDetector()
    results = []

    # Test 1: Step 2 - Parse Log File - Overfull hbox
    results.append(("Step 2: Overfull hbox Detection", [
        ("detects overfull hbox",
         len(log_detector.detect_log_content(LOG_OVERFULL_HBOX, "t.log").overfull_hbox) == 1),
        ("extracts overflow amount (4.9pt)",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX, "t.log").overfull_hbox[0].amount_pt == 4.90633),
        ("extracts line numbers",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX, "t.log").overfull_hbox[0].lines == [162, 163]),
        ("severity WARNING for 1-10pt",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX, "t.log").overfull_hbox[0].severity == "WARNING"),
        ("severity CRITICAL for >10pt",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX_CRITICAL, "t.log").overfull_hbox[0].severity == "CRITICAL"),
    ]))

    # Test 2: Step 2 - Parse Log File - Underfull hbox
    results.append(("Step 2: Underfull hbox Detection", [
        ("detects underfull hbox",
         len(log_detector.detect_log_content(LOG_UNDERFULL_HBOX, "t.log").underfull_hbox) == 1),
        ("extracts badness value",
         log_detector.detect_log_content(LOG_UNDERFULL_HBOX, "t.log").underfull_hbox[0].badness == 10000),
        ("severity WARNING for badness 10000",
         log_detector.detect_log_content(LOG_UNDERFULL_HBOX, "t.log").underfull_hbox[0].severity == "WARNING"),
    ]))

    # Test 3: Step 2 - Parse Log File - Vbox
    results.append(("Step 2: Vbox Detection", [
        ("detects underfull vbox",
         len(log_detector.detect_log_content(LOG_UNDERFULL_VBOX, "t.log").underfull_vbox) == 1),
        ("extracts context (output active)",
         "page break" in log_detector.detect_log_content(LOG_UNDERFULL_VBOX, "t.log").underfull_vbox[0].context),
        ("detects overfull vbox",
         len(log_detector.detect_log_content(LOG_OVERFULL_VBOX, "t.log").overfull_vbox) == 1),
        ("overfull vbox always CRITICAL",
         log_detector.detect_log_content(LOG_OVERFULL_VBOX, "t.log").overfull_vbox[0].severity == "CRITICAL"),
    ]))

    # Test 4: Step 2 - Undefined references (v1.1)
    results.append(("Step 2: Undefined Reference Detection (v1.1)", [
        ("detects undefined reference",
         len(log_detector.detect_log_content(LOG_UNDEFINED_REF, "t.log").undefined_references) == 1),
        ("extracts reference name",
         log_detector.detect_log_content(LOG_UNDEFINED_REF, "t.log").undefined_references[0].reference == "tab:python-libraries"),
        ("extracts page number",
         log_detector.detect_log_content(LOG_UNDEFINED_REF, "t.log").undefined_references[0].page == 27),
        ("extracts input line",
         log_detector.detect_log_content(LOG_UNDEFINED_REF, "t.log").undefined_references[0].input_line == 185),
        ("severity CRITICAL",
         log_detector.detect_log_content(LOG_UNDEFINED_REF, "t.log").undefined_references[0].severity == "CRITICAL"),
    ]))

    # Test 5: Step 2 - Undefined citations (v1.1)
    results.append(("Step 2: Undefined Citation Detection (v1.1)", [
        ("detects undefined citation",
         len(log_detector.detect_log_content(LOG_UNDEFINED_CITATION, "t.log").undefined_citations) == 1),
        ("extracts citation key",
         log_detector.detect_log_content(LOG_UNDEFINED_CITATION, "t.log").undefined_citations[0].citation == "smith2020"),
        ("severity CRITICAL",
         log_detector.detect_log_content(LOG_UNDEFINED_CITATION, "t.log").undefined_citations[0].severity == "CRITICAL"),
    ]))

    # Test 6: Step 2 - Float too large (v1.2)
    results.append(("Step 2: Float Too Large Detection (v1.2)", [
        ("detects float too large",
         len(log_detector.detect_log_content(LOG_FLOAT_TOO_LARGE, "t.log").float_too_large) == 1),
        ("extracts overflow amount",
         log_detector.detect_log_content(LOG_FLOAT_TOO_LARGE, "t.log").float_too_large[0].overflow_pt == 165.89464),
        ("extracts input line",
         log_detector.detect_log_content(LOG_FLOAT_TOO_LARGE, "t.log").float_too_large[0].input_line == 141),
        ("severity CRITICAL for >50pt",
         log_detector.detect_log_content(LOG_FLOAT_TOO_LARGE, "t.log").float_too_large[0].severity == "CRITICAL"),
        ("severity WARNING for <=50pt",
         log_detector.detect_log_content(LOG_FLOAT_SMALL, "t.log").float_too_large[0].severity == "WARNING"),
    ]))

    # Test 7: Step 2 - LaTeX/Package errors (v1.3)
    results.append(("Step 2: Error Detection (v1.3)", [
        ("detects unknown LaTeX error",
         len(log_detector.detect_log_content(LOG_LATEX_ERROR, "t.log").latex_errors) == 1),
        ("unknown error severity CRITICAL",
         log_detector.detect_log_content(LOG_LATEX_ERROR, "t.log").latex_errors[0].severity == "CRITICAL"),
        ("known issue classified as INFO",
         len(log_detector.detect_log_content(LOG_KNOWN_ISSUE, "t.log").known_issues) == 1),
        ("known issue not in errors",
         len(log_detector.detect_log_content(LOG_KNOWN_ISSUE, "t.log").latex_errors) == 0),
        ("detects package error",
         len(log_detector.detect_log_content(LOG_PACKAGE_ERROR, "t.log").package_errors) == 1),
        ("package error severity WARNING",
         log_detector.detect_log_content(LOG_PACKAGE_ERROR, "t.log").package_errors[0].severity == "WARNING"),
    ]))

    # Test 8: Step 3 - TikZ source analysis (v1.4)
    results.append(("Step 3: TikZ Source Analysis (v1.4)", [
        ("detects unconstrained tikzpicture",
         len(tikz_detector.detect_in_content(TIKZ_UNSAFE, "t.tex")) == 1),
        ("unconstrained is WARNING",
         tikz_detector.detect_in_content(TIKZ_UNSAFE, "t.tex")[0].severity == "WARNING"),
        ("safe with resizebox",
         len(tikz_detector.detect_in_content(TIKZ_SAFE_RESIZEBOX, "t.tex")) == 0),
        ("safe with scale option",
         len(tikz_detector.detect_in_content(TIKZ_SAFE_SCALE, "t.tex")) == 0),
        ("large coordinates CRITICAL",
         tikz_detector.detect_in_content(TIKZ_LARGE_COORDS, "t.tex")[0].severity == "CRITICAL"),
        ("large coordinates issue type",
         tikz_detector.detect_in_content(TIKZ_LARGE_COORDS, "t.tex")[0].issue == "large_coordinates"),
    ]))

    # Test 9: Itemsep detection (v1.5)
    results.append(("Itemsep Detection (v1.5)", [
        ("detects itemize without noitemsep",
         len(itemsep_detector.detect_in_content(LIST_UNSAFE, "t.tex")) == 1),
        ("safe with noitemsep",
         len(itemsep_detector.detect_in_content(LIST_SAFE_NOITEMSEP, "t.tex")) == 0),
        ("safe with nosep",
         len(itemsep_detector.detect_in_content(LIST_SAFE_NOSEP, "t.tex")) == 0),
        ("check_raggedbottom works",
         itemsep_detector.check_raggedbottom(r"\raggedbottom") is True),
        ("check_book_class works",
         itemsep_detector.check_book_class(r"\documentclass{book}") is True),
    ]))

    # Test 10: Severity Classification
    results.append(("Severity Classification", [
        ("overfull hbox >10pt -> CRITICAL",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX_CRITICAL, "t.log").overfull_hbox[0].severity == "CRITICAL"),
        ("overfull hbox 1-10pt -> WARNING",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX, "t.log").overfull_hbox[0].severity == "WARNING"),
        ("underfull hbox badness 10000 -> WARNING",
         log_detector.detect_log_content(LOG_UNDERFULL_HBOX, "t.log").underfull_hbox[0].severity == "WARNING"),
        ("overfull vbox any -> CRITICAL",
         log_detector.detect_log_content(LOG_OVERFULL_VBOX, "t.log").overfull_vbox[0].severity == "CRITICAL"),
        ("undefined reference -> CRITICAL",
         log_detector.detect_log_content(LOG_UNDEFINED_REF, "t.log").undefined_references[0].severity == "CRITICAL"),
        ("float too large >50pt -> CRITICAL",
         log_detector.detect_log_content(LOG_FLOAT_TOO_LARGE, "t.log").float_too_large[0].severity == "CRITICAL"),
        ("float too large <=50pt -> WARNING",
         log_detector.detect_log_content(LOG_FLOAT_SMALL, "t.log").float_too_large[0].severity == "WARNING"),
        ("TikZ no constraint -> WARNING",
         tikz_detector.detect_in_content(TIKZ_UNSAFE, "t.tex")[0].severity == "WARNING"),
        ("TikZ large coords -> CRITICAL",
         tikz_detector.detect_in_content(TIKZ_LARGE_COORDS, "t.tex")[0].severity == "CRITICAL"),
    ]))

    # Test 11: Verdict Logic
    results.append(("Verdict Logic", [
        ("FAIL on CRITICAL",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX_CRITICAL, "t.log").verdict == "FAIL"),
        ("WARNING on WARNING only",
         log_detector.detect_log_content(LOG_OVERFULL_HBOX, "t.log").verdict == "WARNING"),
        ("PASS on INFO only",
         log_detector.detect_log_content("Overfull \\hbox (0.5pt too wide) in paragraph at lines 10--11", "t.log").verdict == "PASS"),
    ]))

    # Test 12: Triggers
    results.append(("Triggers", [
        ("triggers hbox fix on hbox issues",
         "qa-typeset-fix-hbox" in log_detector.detect_log_content(LOG_OVERFULL_HBOX, "t.log").triggers),
        ("triggers refs fix on undefined refs",
         "qa-typeset-fix-refs" in log_detector.detect_log_content(LOG_UNDEFINED_REF, "t.log").triggers),
        ("triggers float fix on float issues",
         "qa-typeset-fix-float" in log_detector.detect_log_content(LOG_FLOAT_TOO_LARGE, "t.log").triggers),
        ("triggers vbox fix on vbox issues",
         "qa-typeset-fix-vbox" in log_detector.detect_log_content(LOG_UNDERFULL_VBOX, "t.log").triggers),
    ]))

    # Test 13: Output Format
    result = log_detector.detect_log_content(LOG_OVERFULL_HBOX, "test.log")
    output = full_detector.to_dict(result)
    results.append(("Output Format Compliance", [
        ("skill field", output.get("skill") == "qa-typeset-detect"),
        ("status field", output.get("status") == "DONE"),
        ("verdict field", "verdict" in output),
        ("log_file field", "log_file" in output),
        ("warnings object", "warnings" in output),
        ("warnings.overfull_hbox array", "overfull_hbox" in output["warnings"]),
        ("warnings.underfull_hbox array", "underfull_hbox" in output["warnings"]),
        ("warnings.overfull_vbox array", "overfull_vbox" in output["warnings"]),
        ("warnings.underfull_vbox array", "underfull_vbox" in output["warnings"]),
        ("warnings.undefined_references array", "undefined_references" in output["warnings"]),
        ("warnings.undefined_citations array", "undefined_citations" in output["warnings"]),
        ("warnings.float_too_large array", "float_too_large" in output["warnings"]),
        ("warnings.known_issues array", "known_issues" in output["warnings"]),
        ("warnings.tikz_overflow_risk array", "tikz_overflow_risk" in output["warnings"]),
        ("summary object", "summary" in output),
        ("summary.total", "total" in output.get("summary", {})),
        ("summary.critical", "critical" in output.get("summary", {})),
        ("summary.warnings", "warnings" in output.get("summary", {})),
        ("triggers array", "triggers" in output),
    ]))

    # Test 14: Detection Rules
    rules = full_detector.get_rules()
    results.append(("Detection Rules", [
        ("rule: overfull_hbox_critical", "overfull_hbox_critical" in rules),
        ("rule: overfull_hbox_warning", "overfull_hbox_warning" in rules),
        ("rule: underfull_hbox_warning", "underfull_hbox_warning" in rules),
        ("rule: overfull_vbox_critical", "overfull_vbox_critical" in rules),
        ("rule: undefined_ref_critical", "undefined_ref_critical" in rules),
        ("rule: float_large_critical", "float_large_critical" in rules),
        ("rule: tikz_no_constraint_warning", "tikz_no_constraint_warning" in rules),
        ("rule: tikz_large_coords_critical", "tikz_large_coords_critical" in rules),
    ]))

    return results


def print_results(results):
    """Print comparison results."""
    print("=" * 70)
    print("qa-typeset-detect: Skill vs Python Tool Comparison")
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
