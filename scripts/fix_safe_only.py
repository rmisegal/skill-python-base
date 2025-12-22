"""
Ultra-safe fixes only - minimal changes that won't break compilation.
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime


def fix_hebmath_definitions(book_path: Path):
    """Remove duplicate hebmath definitions - CLS provides this."""
    print("\n=== Removing Duplicate HebMath Definitions ===")
    tex_files = list(book_path.rglob("*.tex"))
    fixed = 0

    for tex_file in tex_files:
        try:
            content = tex_file.read_text(encoding='utf-8')
            # Only remove the exact duplicate definition
            new_content = re.sub(
                r'\\newcommand\{\\hebmath\}\[1\]\{\\texthebrew\{#1\}\}\s*\n?',
                '',
                content
            )
            if new_content != content:
                tex_file.write_text(new_content, encoding='utf-8')
                print(f"  Removed from: {tex_file.name}")
                fixed += 1
        except Exception as e:
            print(f"  Error in {tex_file.name}: {e}")

    print(f"  Total: {fixed} files fixed")
    return fixed


def fix_standalone_bib_paths(book_path: Path):
    """Fix bibliography paths in standalone files."""
    print("\n=== Fixing Standalone Bibliography Paths ===")
    fixed = 0

    # Fix chapter-standalone-preamble.tex
    preamble = book_path / "chapter-standalone-preamble.tex"
    if preamble.exists():
        try:
            content = preamble.read_text(encoding='utf-8')
            # Fix relative path to bibliography
            new_content = content.replace(
                r'\addbibresource{../bibliography/references.bib}',
                r'\addbibresource{bibliography/references.bib}'
            )
            if new_content != content:
                preamble.write_text(new_content, encoding='utf-8')
                print(f"  Fixed: {preamble.name}")
                fixed += 1
        except Exception as e:
            print(f"  Error: {e}")

    print(f"  Total: {fixed} files fixed")
    return fixed


def verify_compilation(book_path: Path):
    """Compile and verify."""
    import subprocess
    print("\n=== Compiling Book ===")

    result = subprocess.run(
        ["lualatex", "-interaction=nonstopmode", "main.tex"],
        cwd=book_path,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check for success
    if "Output written on main.pdf" in result.stdout:
        # Extract page count
        match = re.search(r"Output written on main\.pdf \((\d+) pages", result.stdout)
        if match:
            pages = match.group(1)
            print(f"  SUCCESS: {pages} pages generated")
            return True, int(pages)

    print("  FAILED: Check main.log for errors")
    return False, 0


def run_biber(book_path: Path):
    """Run biber for bibliography."""
    import subprocess
    print("\n=== Running Biber ===")

    result = subprocess.run(
        ["biber", "main"],
        cwd=book_path,
        capture_output=True,
        text=True,
        timeout=120
    )

    if "Output to main.bbl" in result.stdout:
        print("  SUCCESS: Bibliography generated")
        return True

    print("  FAILED or no bibliography needed")
    return False


def main():
    book_path = Path(__file__).parent.parent / "book"

    print(f"\n{'='*60}")
    print("SAFE FIXES ONLY")
    print(f"{'='*60}")
    print(f"Book path: {book_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Apply only safe fixes
    total_fixes = 0
    total_fixes += fix_hebmath_definitions(book_path)
    total_fixes += fix_standalone_bib_paths(book_path)

    print(f"\n=== Total Safe Fixes: {total_fixes} ===")

    # Compile
    print("\n" + "="*60)
    print("COMPILATION")
    print("="*60)

    success, pages = verify_compilation(book_path)
    if success and pages >= 400:
        run_biber(book_path)
        verify_compilation(book_path)  # Second pass with bibliography
        verify_compilation(book_path)  # Third pass for references

    print(f"\n{'='*60}")
    print("DONE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
