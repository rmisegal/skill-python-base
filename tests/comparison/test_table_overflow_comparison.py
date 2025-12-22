"""
Comparison test for qa-table-overflow-detect skill vs TableOverflowDetector Python tool.

Verifies that Python implementation covers all skill.md detection criteria.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.table.detection.table_overflow_detector import (
    TableOverflowDetector, OverflowDetectResult
)

# Test content samples from skill.md patterns

# UNSAFE patterns (no width constraint)
UNSAFE_5_COLS = r"""
\begin{rtltabular}{|c|c|c|c|c|}
\hline
A & B & C & D & E \\
\hline
\end{rtltabular}
"""

UNSAFE_6_COLS = r"""
\begin{tabular}{|l|l|l|l|l|l|}
\hline
A & B & C & D & E & F \\
\hline
\end{tabular}
"""

UNSAFE_4_COLS = r"""
\begin{tabular}{|c|c|c|c|}
\hline
A & B & C & D \\
\hline
\end{tabular}
"""

# SAFE patterns (width constrained)
SAFE_RESIZEBOX = r"""
\resizebox{\textwidth}{!}{%
\begin{rtltabular}{|c|c|c|c|c|}
\hline
A & B & C & D & E \\
\hline
\end{rtltabular}%
}
"""

SAFE_TABULARX = r"""
\begin{tabularx}{\textwidth}{|X|X|X|X|X|}
\hline
A & B & C & D & E \\
\hline
\end{tabularx}
"""

SAFE_3_COLS = r"""
\begin{tabular}{|c|c|c|}
\hline
A & B & C \\
\hline
\end{tabular}
"""


def run_comparison():
    """Run comparison tests."""
    detector = TableOverflowDetector()
    results = []

    # Test 1: Step 1 - Find Table Environments
    results.append(("Step 1: Find Table Environments", [
        ("detects rtltabular",
         detector.detect_content(UNSAFE_5_COLS, "test.tex").total_tables == 1),
        ("detects tabular",
         detector.detect_content(UNSAFE_6_COLS, "test.tex").total_tables == 1),
        ("detects tabularx",
         detector.detect_content(SAFE_TABULARX, "test.tex").total_tables == 1),
    ]))

    # Test 2: Step 2 - Check for Resizebox Wrapper
    results.append(("Step 2: Check for Resizebox Wrapper", [
        ("detects resizebox wrapper",
         detector.detect_content(SAFE_RESIZEBOX, "test.tex").tables[0].has_resizebox),
        ("detects missing resizebox",
         not detector.detect_content(UNSAFE_5_COLS, "test.tex").tables[0].has_resizebox),
        ("tabularx with textwidth is safe",
         detector.detect_content(SAFE_TABULARX, "test.tex").tables[0].has_resizebox),
    ]))

    # Test 3: Step 3 - Count Columns
    unsafe_5_result = detector.detect_content(UNSAFE_5_COLS, "test.tex")
    unsafe_6_result = detector.detect_content(UNSAFE_6_COLS, "test.tex")
    unsafe_4_result = detector.detect_content(UNSAFE_4_COLS, "test.tex")
    safe_3_result = detector.detect_content(SAFE_3_COLS, "test.tex")

    results.append(("Step 3: Count Columns", [
        ("counts 5 columns correctly", unsafe_5_result.tables[0].columns == 5),
        ("counts 6 columns correctly", unsafe_6_result.tables[0].columns == 6),
        ("counts 4 columns correctly", unsafe_4_result.tables[0].columns == 4),
        ("counts 3 columns correctly", safe_3_result.tables[0].columns == 3),
    ]))

    # Test 4: Detection Rules
    results.append(("Detection Rules", [
        ("5+ cols no resizebox -> CRITICAL", unsafe_5_result.tables[0].severity == "CRITICAL"),
        ("6+ cols no resizebox -> CRITICAL", unsafe_6_result.tables[0].severity == "CRITICAL"),
        ("4 cols no resizebox -> WARNING", unsafe_4_result.tables[0].severity == "WARNING"),
        ("3 cols no resizebox -> SAFE", safe_3_result.tables[0].severity == "SAFE"),
        ("any with resizebox -> SAFE",
         detector.detect_content(SAFE_RESIZEBOX, "test.tex").tables[0].severity == "SAFE"),
        ("tabularx textwidth -> SAFE",
         detector.detect_content(SAFE_TABULARX, "test.tex").tables[0].severity == "SAFE"),
    ]))

    # Test 5: Verdict
    results.append(("Verdict", [
        ("FAIL on CRITICAL", unsafe_5_result.verdict == "FAIL"),
        ("WARNING on WARNING only", unsafe_4_result.verdict == "WARNING"),
        ("PASS on SAFE only", safe_3_result.verdict == "PASS"),
    ]))

    # Test 6: Triggers
    results.append(("Triggers", [
        ("triggers on unsafe", "qa-table-overflow-fix" in unsafe_5_result.triggers),
        ("no triggers on safe", len(safe_3_result.triggers) == 0),
    ]))

    # Test 7: Output Format
    output = detector.to_dict(unsafe_5_result)
    results.append(("Output Format Compliance", [
        ("skill field", output.get("skill") == "qa-table-overflow-detect"),
        ("status field", output.get("status") == "DONE"),
        ("verdict field", "verdict" in output),
        ("tables array", "tables" in output and isinstance(output["tables"], list)),
        ("summary object", "summary" in output),
        ("summary.total_tables", "total_tables" in output.get("summary", {})),
        ("summary.unsafe", "unsafe" in output.get("summary", {})),
        ("summary.safe", "safe" in output.get("summary", {})),
        ("triggers array", "triggers" in output),
        ("table.file", "file" in output["tables"][0]),
        ("table.line", "line" in output["tables"][0]),
        ("table.type", "type" in output["tables"][0]),
        ("table.columns", "columns" in output["tables"][0]),
        ("table.has_resizebox", "has_resizebox" in output["tables"][0]),
        ("table.severity", "severity" in output["tables"][0]),
        ("table.fix", "fix" in output["tables"][0]),
    ]))

    # Test 8: Fix suggestion
    results.append(("Fix Suggestion", [
        ("fix contains resizebox", "resizebox" in unsafe_5_result.tables[0].fix.lower()),
    ]))

    return results


def print_results(results):
    """Print comparison results."""
    print("=" * 70)
    print("qa-table-overflow-detect: Skill vs Python Tool Comparison")
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
