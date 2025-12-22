r"""
English Bibliography Missing Fixer Tool
Adds \printenglishbibliography to chapters with English citations

Version: 1.0.0
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class FixResult:
    """Result of fixing a single file."""
    file: str
    line: int
    action: str
    english_citations: int
    success: bool


def get_english_bib_keys(bib_file: Path) -> Set[str]:
    """Extract citation keys that have keyword=english from .bib file."""
    english_keys = set()

    if not bib_file.exists():
        return english_keys

    content = bib_file.read_text(encoding='utf-8', errors='ignore')
    entry_pattern = r'@\w+\{([^,]+),'
    entries = re.split(r'(?=@\w+\{)', content)

    for entry in entries:
        if not entry.strip():
            continue
        key_match = re.search(entry_pattern, entry)
        if not key_match:
            continue
        key = key_match.group(1).strip()
        if re.search(r'keywords?\s*=\s*\{[^}]*english[^}]*\}', entry, re.I):
            english_keys.add(key)

    return english_keys


def extract_citations(tex_file: Path) -> List[str]:
    """Extract all citation keys from a .tex file."""
    if not tex_file.exists():
        return []

    content = tex_file.read_text(encoding='utf-8', errors='ignore')
    cite_pattern = r'\\cite\{([^}]+)\}'
    citations = []

    for match in re.finditer(cite_pattern, content):
        keys = match.group(1).split(',')
        for key in keys:
            citations.append(key.strip())

    return citations


def fix_chapter(chapter_file: Path, english_count: int) -> FixResult:
    r"""Add \printenglishbibliography after \printbibliography."""
    if not chapter_file.exists():
        return FixResult(str(chapter_file), -1, "File not found", 0, False)

    content = chapter_file.read_text(encoding='utf-8', errors='ignore')

    # Check if already has \printenglishbibliography
    if r'\printenglishbibliography' in content:
        return FixResult(
            str(chapter_file), -1,
            "Already has \\printenglishbibliography",
            english_count, True
        )

    # Find \printbibliography line number
    lines = content.splitlines()
    bib_line = -1
    for i, line in enumerate(lines, 1):
        if r'\printbibliography' in line:
            bib_line = i
            break

    if bib_line == -1:
        return FixResult(
            str(chapter_file), -1,
            "No \\printbibliography found",
            english_count, False
        )

    # Fix \printbibliography: change heading=bibintoc to heading=none
    # This removes Hebrew מקורות from TOC (only English References in TOC)
    new_content = re.sub(
        r'heading\s*=\s*bibintoc',
        'heading=none',
        content
    )

    # Add \printenglishbibliography after \printbibliography
    pattern = r'(\\printbibliography\b[^\n]*)'
    replacement = r'\1\n\\printenglishbibliography'
    new_content = re.sub(pattern, replacement, new_content)

    # Write back
    chapter_file.write_text(new_content, encoding='utf-8')

    return FixResult(
        str(chapter_file), bib_line,
        "Added \\printenglishbibliography after \\printbibliography",
        english_count, True
    )


def fix(chapters_dir: str, bib_file: str) -> Dict:
    """
    Main fix function.

    Args:
        chapters_dir: Path to chapters directory
        bib_file: Path to bibliography file

    Returns:
        Fix report with results
    """
    chapters_path = Path(chapters_dir)
    bib_path = Path(bib_file)

    results = []
    chapters_fixed = 0
    already_correct = 0

    # Get English citation keys
    english_keys = get_english_bib_keys(bib_path)

    # Process all chapter files
    chapter_files = sorted(chapters_path.glob("chapter*.tex"))

    for chapter_file in chapter_files:
        citations = extract_citations(chapter_file)
        english_citations = [c for c in citations if c in english_keys]

        if not english_citations:
            continue

        result = fix_chapter(chapter_file, len(english_citations))
        results.append(result)

        if result.success:
            if "Already has" in result.action:
                already_correct += 1
            else:
                chapters_fixed += 1

    return {
        "summary": {
            "total_chapters": len(chapter_files),
            "chapters_fixed": chapters_fixed,
            "already_correct": already_correct,
            "total_english_keys_in_bib": len(english_keys)
        },
        "fixes": [
            {
                "file": r.file,
                "line": r.line,
                "action": r.action,
                "english_citations": r.english_citations,
                "success": r.success
            }
            for r in results
        ]
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: python tool.py <chapters_dir> <bib_file>")
        sys.exit(1)

    result = fix(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))
