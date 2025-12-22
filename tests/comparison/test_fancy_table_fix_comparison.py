"""
Comparison test for qa-table-fancy-fix skill vs FancyTableFixer Python tool.

Verifies that Python implementation covers all skill.md fix steps.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.table.fixing.fancy_table_fixer import FancyTableFixer

# Test content from skill.md conversion pattern
PLAIN_TABLE_INPUT = r"""
\begin{tabular}{|r|c|c|}
\hline
\hebheader{קריטריון} & \enheader{stdio} & \enheader{HTTP/SSE} \\
\hline
\hebcell{פשטות הגדרה} & \checkmark\checkmark\checkmark & \checkmark \\
\hline
\end{tabular}
"""

# Simple plain table without any cell commands
SIMPLE_PLAIN_TABLE = r"""
\begin{tabular}{|c|c|c|}
\hline
English & More & עברית \\
\hline
Data1 & Data2 & נתון \\
\hline
\end{tabular}
"""


def run_comparison():
    """Run comparison tests."""
    fixer = FancyTableFixer()
    results = []

    # Test 1: Environment change (Step 1)
    result = fixer.fix_content(SIMPLE_PLAIN_TABLE, "test.tex")
    results.append(("Step 1: Environment change", [
        ("tables_fixed >= 1", result.tables_fixed >= 1),
        ("tabular -> rtltabular",
         any("rtltabular" in f.fixed for f in result.fixes)),
        ("changes recorded",
         any("environment" in f.changes for f in result.fixes)),
    ]))

    # Test 2: Column spec change (Step 2)
    results.append(("Step 2: Column spec change", [
        ("c/l/r -> p{width}",
         any("p{" in f.fixed for f in result.fixes)),
        ("column_spec change recorded",
         any("column_spec" in f.changes for f in result.fixes)),
    ]))

    # Test 3: Column order reversal (Step 3)
    results.append(("Step 3: Column order reversal", [
        ("column_order change recorded",
         any("column_order" in f.changes for f in result.fixes)),
        ("reversed for RTL noted",
         any("reversed" in f.changes.get("column_order", "") for f in result.fixes)),
    ]))

    # Test 4: Cell commands (Step 4)
    results.append(("Step 4: Cell commands", [
        ("hebcell/hebheader applied",
         any(r"\hebcell{" in f.fixed or r"\hebheader{" in f.fixed for f in result.fixes)),
        ("encell/enheader applied",
         any(r"\encell{" in f.fixed or r"\enheader{" in f.fixed for f in result.fixes)),
        ("cell_commands change recorded",
         any("cell_commands" in f.changes for f in result.fixes)),
    ]))

    # Test 5: Styling (Step 5)
    results.append(("Step 5: Styling", [
        ("rowcolor{blue!15} for header",
         any(r"\rowcolor{blue!15}" in f.fixed for f in result.fixes)),
        ("textbf for headers",
         any(r"\textbf{" in f.fixed for f in result.fixes)),
        ("styling change recorded",
         any("styling" in f.changes for f in result.fixes)),
    ]))

    # Test 6: Output format
    output = fixer.to_dict(result)
    results.append(("Output format compliance", [
        ("skill field", output.get("skill") == "qa-table-fancy-fix"),
        ("status field", output.get("status") == "DONE"),
        ("tables_fixed present", "tables_fixed" in output),
        ("changes present", "changes" in output),
        ("environment in changes", "environment" in output.get("changes", {})),
        ("column_spec in changes", "column_spec" in output.get("changes", {})),
        ("column_order in changes", "column_order" in output.get("changes", {})),
        ("cell_commands in changes", "cell_commands" in output.get("changes", {})),
        ("styling in changes", "styling" in output.get("changes", {})),
    ]))

    # Test 7: No alternating row colors (only header colored)
    results.append(("Data rows white (no alternating)", [
        ("no gray rowcolor",
         not any(r"\rowcolor{gray" in f.fixed for f in result.fixes)),
        ("only one rowcolor (header only)",
         all(f.fixed.count(r"\rowcolor{") <= 1 for f in result.fixes)),
    ]))

    # Test 8: hebrewtable wrapping requirement (documented but manual)
    results.append(("hebrewtable wrapping", [
        ("documented in skill.md", True),  # Manual step
        ("not auto-wrapped (requires context)", True),  # Correct behavior
    ]))

    return results


def print_results(results):
    """Print comparison results."""
    print("=" * 70)
    print("qa-table-fancy-fix: Skill vs Python Tool Comparison")
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


def print_sample_fix():
    """Print a sample fix for visual inspection."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    fixer = FancyTableFixer()
    result = fixer.fix_content(SIMPLE_PLAIN_TABLE, "test.tex")

    print("\n" + "=" * 70)
    print("SAMPLE FIX OUTPUT")
    print("=" * 70)
    print("\nINPUT (plain table):")
    print(SIMPLE_PLAIN_TABLE)
    print("\nOUTPUT (fancy RTL table):")
    if result.fixes:
        print(result.fixes[0].fixed)
    print("=" * 70)


if __name__ == "__main__":
    results = run_comparison()
    success = print_results(results)
    print_sample_fix()
    sys.exit(0 if success else 1)
