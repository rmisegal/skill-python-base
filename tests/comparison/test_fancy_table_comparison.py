"""
Comparison test for qa-table-fancy-detect skill vs FancyTableDetector Python tool.

Verifies that Python implementation covers all skill.md detection criteria.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.table.detection.fancy_table_detector import (
    FancyTableDetector, FancyDetectResult
)

# Test content samples from skill.md patterns
# PLAIN table: uses tabular, Hebrew in last column (LTR order), no cell commands
PLAIN_TABLE = r"""
\begin{tabular}{|c|c|c|}
\hline
English & More English & עברית \\
\hline
Data & More & טקסט \\
\hline
\end{tabular}
"""

PARTIAL_TABLE = r"""
\begin{rtltabular}{|c|c|c|}
\hline
\hebcell{עברית} & \encell{English} & \encell{More} \\
\rowcolor{gray!8}
Data & More & Last \\
\hline
\end{rtltabular}
"""

FANCY_TABLE = r"""
\begin{rtltabular}{|p{2.5cm}|p{2.5cm}|p{3.5cm}|}
\hline
\rowcolor{blue!15}
\textbf{\enheader{HTTP}} & \textbf{\enheader{stdio}} & \textbf{\hebheader{קריטריון}} \\
\hline
\encell{REST} & \encell{JSON-RPC} & \hebcell{פרוטוקול} \\
\hline
\end{rtltabular}
"""

HEBREWTABLE_WITH_TABULAR = r"""
\begin{hebrewtable}
\caption{Test table}
\begin{tabular}{|c|c|}
\hline
A & B \\
\end{tabular}
\end{hebrewtable}
"""


def run_comparison():
    """Run comparison tests."""
    detector = FancyTableDetector()
    results = []

    # Test 1: PLAIN table detection
    plain_result = detector.detect_content(PLAIN_TABLE, "plain.tex")
    results.append(("PLAIN table detection", [
        ("tables_scanned >= 1", plain_result.tables_scanned >= 1),
        ("plain_tables_found >= 1", plain_result.plain_tables_found >= 1),
        ("uses_tabular_not_rtltabular detected",
         any("uses_tabular_not_rtltabular" in a.problems for a in plain_result.issues)),
        ("missing_hebcell_commands detected",
         any("missing_hebcell_commands" in a.problems for a in plain_result.issues)),
        ("ltr_column_order detected",
         any("ltr_column_order" in a.problems for a in plain_result.issues)),
        ("classification is PLAIN",
         any(a.classification == "PLAIN" for a in plain_result.issues)),
    ]))

    # Test 2: PARTIAL table detection
    partial_result = detector.detect_content(PARTIAL_TABLE, "partial.tex")
    results.append(("PARTIAL table detection", [
        ("tables_scanned >= 1", partial_result.tables_scanned >= 1),
        ("uses_c_columns_not_p detected",
         any("uses_c_columns_not_p" in a.problems for a in partial_result.issues)),
        ("gray_rowcolor_on_data detected",
         any("gray_rowcolor_on_data" in a.problems for a in partial_result.issues)),
    ]))

    # Test 3: FANCY table (no issues)
    fancy_result = detector.detect_content(FANCY_TABLE, "fancy.tex")
    results.append(("FANCY table detection", [
        ("tables_scanned >= 1", fancy_result.tables_scanned >= 1),
        ("fancy_tables_found >= 1", fancy_result.fancy_tables_found >= 1),
        ("no CRITICAL issues",
         not any(a.severity == "CRITICAL" for a in fancy_result.issues)),
    ]))

    # Test 4: hebrewtable with tabular inside
    heb_result = detector.detect_content(HEBREWTABLE_WITH_TABULAR, "heb.tex")
    results.append(("hebrewtable+tabular detection", [
        ("tabular_in_hebrewtable detected",
         any("tabular_in_hebrewtable" in a.problems for a in heb_result.issues)),
    ]))

    # Test 5: Output format
    output = detector.to_dict(plain_result)
    results.append(("Output format compliance", [
        ("skill field present", output.get("skill") == "qa-table-fancy-detect"),
        ("status field present", output.get("status") == "DONE"),
        ("tables_scanned present", "tables_scanned" in output),
        ("plain_tables_found present", "plain_tables_found" in output),
        ("partial_tables_found present", "partial_tables_found" in output),
        ("fancy_tables_found present", "fancy_tables_found" in output),
        ("issues list present", "issues" in output),
        ("triggers present", "triggers" in output),
        ("triggers qa-table-fancy-fix", "qa-table-fancy-fix" in output.get("triggers", [])),
    ]))

    # Test 6: Rules/problem codes
    rules = detector.get_rules()
    results.append(("Problem codes coverage", [
        ("uses_tabular_not_rtltabular", "uses_tabular_not_rtltabular" in rules),
        ("uses_c_columns_not_p", "uses_c_columns_not_p" in rules),
        ("missing_hebcell_commands", "missing_hebcell_commands" in rules),
        ("ltr_column_order", "ltr_column_order" in rules),
        ("gray_rowcolor_on_data", "gray_rowcolor_on_data" in rules),
        ("tabular_in_hebrewtable", "tabular_in_hebrewtable" in rules),
    ]))

    return results


def print_results(results):
    """Print comparison results."""
    print("=" * 70)
    print("qa-table-fancy-detect: Skill vs Python Tool Comparison")
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
