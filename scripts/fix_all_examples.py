"""
Fix all issues in CLS-examples.

Applies all QA fixers to resolve detected issues.
"""

import sys
import io
from pathlib import Path

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection import (
    BiDiDetector,
    TableDetector,
    CodeDetector,
    BibDetector,
)
from qa_engine.infrastructure.fixing import (
    BiDiFixer,
    CodeFixer,
    TableFixer,
    TikzFixer,
    BibFixer,
)


def fix_file(file_path: Path) -> dict:
    """Fix all issues in a single file."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    original_content = content

    # Detect issues
    bidi_detector = BiDiDetector()
    code_detector = CodeDetector()
    table_detector = TableDetector()
    bib_detector = BibDetector()

    bidi_issues = bidi_detector.detect(content, str(file_path))
    code_issues = code_detector.detect(content, str(file_path))
    table_issues = table_detector.detect(content, str(file_path))
    bib_issues = bib_detector.detect(content, str(file_path))

    # Apply fixes
    bidi_fixer = BiDiFixer()
    code_fixer = CodeFixer()
    table_fixer = TableFixer()
    tikz_fixer = TikzFixer()
    bib_fixer = BibFixer()

    # Fix BiDi issues
    bidi_fixable = [i for i in bidi_issues if i.rule in [
        "bidi-numbers", "bidi-english", "bidi-acronym", "bidi-tikz-rtl"
    ]]
    content = bidi_fixer.fix(content, bidi_fixable)

    # Fix TikZ issues (subset of bidi)
    tikz_issues = [i for i in bidi_issues if i.rule == "bidi-tikz-rtl"]
    content = tikz_fixer.fix(content, tikz_issues)

    # Fix code issues
    code_fixable = [i for i in code_issues if i.rule == "code-background-overflow"]
    content = code_fixer.fix(content, code_fixable)

    # Fix table issues
    content = table_fixer.fix(content, table_issues)

    # Fix bib issues (creates .bib files)
    bib_fixer.fix_with_context(content, bib_issues, str(file_path))

    # Write fixed content
    if content != original_content:
        file_path.write_text(content, encoding="utf-8")

    return {
        "file": file_path.name,
        "bidi_fixed": len(bidi_fixable),
        "code_fixed": len(code_fixable),
        "table_fixed": len(table_issues),
        "tikz_fixed": len(tikz_issues),
        "bib_fixed": len(bib_issues),
        "changed": content != original_content,
    }


def main():
    """Fix all CLS-examples."""
    test_data = Path(__file__).parent.parent / "test-data" / "CLS-examples"

    if not test_data.exists():
        print(f"Test data not found: {test_data}")
        return

    tex_files = list(test_data.rglob("*.tex"))
    print(f"\n{'=' * 60}")
    print("FIXING ALL CLS-EXAMPLES")
    print(f"{'=' * 60}")
    print(f"Files to process: {len(tex_files)}")

    total_fixed = {
        "bidi": 0,
        "code": 0,
        "table": 0,
        "tikz": 0,
        "bib": 0,
        "files_changed": 0,
    }

    for tex_file in tex_files:
        try:
            result = fix_file(tex_file)
            print(f"\n{result['file']}:")
            print(f"  BiDi: {result['bidi_fixed']}")
            print(f"  Code: {result['code_fixed']}")
            print(f"  Table: {result['table_fixed']}")
            print(f"  TikZ: {result['tikz_fixed']}")
            print(f"  Bib: {result['bib_fixed']}")
            print(f"  Changed: {result['changed']}")

            total_fixed["bidi"] += result["bidi_fixed"]
            total_fixed["code"] += result["code_fixed"]
            total_fixed["table"] += result["table_fixed"]
            total_fixed["tikz"] += result["tikz_fixed"]
            total_fixed["bib"] += result["bib_fixed"]
            if result["changed"]:
                total_fixed["files_changed"] += 1

        except Exception as e:
            print(f"\nError processing {tex_file.name}: {e}")

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total BiDi fixes: {total_fixed['bidi']}")
    print(f"Total Code fixes: {total_fixed['code']}")
    print(f"Total Table fixes: {total_fixed['table']}")
    print(f"Total TikZ fixes: {total_fixed['tikz']}")
    print(f"Total Bib fixes: {total_fixed['bib']}")
    print(f"Files changed: {total_fixed['files_changed']}")


if __name__ == "__main__":
    main()
