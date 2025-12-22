r"""
English Bibliography Missing Detector Tool
Detects chapters with English citations but no \printenglishbibliography

Version: 1.0.0
"""

import re
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass, field


@dataclass
class Issue:
    """Represents a detected issue."""
    rule: str
    severity: str
    file: str
    line: int
    message: str
    english_citations: List[str] = field(default_factory=list)


def get_english_bib_keys(bib_file: Path) -> Set[str]:
    """Extract citation keys that have keyword=english from .bib file."""
    english_keys = set()

    if not bib_file.exists():
        return english_keys

    content = bib_file.read_text(encoding='utf-8', errors='ignore')

    # Find all entries with keyword=english or keywords={english}
    # Pattern: @type{key, ... keywords = {english} or keyword = {english}
    entry_pattern = r'@\w+\{([^,]+),'

    # Split by entries
    entries = re.split(r'(?=@\w+\{)', content)

    for entry in entries:
        if not entry.strip():
            continue

        # Get the key
        key_match = re.search(entry_pattern, entry)
        if not key_match:
            continue

        key = key_match.group(1).strip()

        # Check if entry has keyword=english
        if re.search(r'keywords?\s*=\s*\{[^}]*english[^}]*\}', entry, re.I):
            english_keys.add(key)

    return english_keys


def extract_citations(tex_file: Path) -> List[str]:
    """Extract all citation keys from a .tex file."""
    citations = []

    if not tex_file.exists():
        return citations

    content = tex_file.read_text(encoding='utf-8', errors='ignore')

    # Find all \cite{...} commands
    cite_pattern = r'\\cite\{([^}]+)\}'

    for match in re.finditer(cite_pattern, content):
        # Handle multiple citations in one command: \cite{key1,key2,key3}
        keys = match.group(1).split(',')
        for key in keys:
            citations.append(key.strip())

    return citations


def has_printenglishbibliography(tex_file: Path) -> bool:
    r"""Check if a .tex file contains \printenglishbibliography."""
    if not tex_file.exists():
        return False

    content = tex_file.read_text(encoding='utf-8', errors='ignore')
    return r'\printenglishbibliography' in content


def find_printbibliography_line(tex_file: Path) -> int:
    r"""Find the line number of \printbibliography command."""
    if not tex_file.exists():
        return -1

    lines = tex_file.read_text(encoding='utf-8', errors='ignore').splitlines()

    for i, line in enumerate(lines, 1):
        if r'\printbibliography' in line:
            return i

    return -1


def detect(chapters_dir: str, bib_file: str) -> Dict:
    """
    Main detection function.

    Args:
        chapters_dir: Path to chapters directory
        bib_file: Path to bibliography file

    Returns:
        Detection report with issues
    """
    chapters_path = Path(chapters_dir)
    bib_path = Path(bib_file)

    issues = []
    chapters_checked = 0

    # Get English citation keys from .bib file
    english_keys = get_english_bib_keys(bib_path)

    # Scan all chapter files
    chapter_files = sorted(chapters_path.glob("chapter*.tex"))

    for chapter_file in chapter_files:
        chapters_checked += 1

        # Extract citations from chapter
        citations = extract_citations(chapter_file)

        # Find English citations
        english_citations = [c for c in citations if c in english_keys]

        # Check if chapter has English bibliography
        has_english_bib = has_printenglishbibliography(chapter_file)

        if english_citations and not has_english_bib:
            bib_line = find_printbibliography_line(chapter_file)

            issues.append(Issue(
                rule="bib-english-references-missing",
                severity="CRITICAL",
                file=str(chapter_file),
                line=bib_line,
                message=f"Chapter has {len(english_citations)} English citation(s) but no \\printenglishbibliography",
                english_citations=english_citations
            ))

    return {
        "summary": {
            "total_chapters": chapters_checked,
            "chapters_with_issues": len(issues),
            "total_english_keys_in_bib": len(english_keys),
            "total_issues": len(issues)
        },
        "issues": [
            {
                "rule": i.rule,
                "severity": i.severity,
                "file": i.file,
                "line": i.line,
                "message": i.message,
                "english_citations": i.english_citations,
                "fix": "Add \\printenglishbibliography after \\printbibliography"
            }
            for i in issues
        ]
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: python tool.py <chapters_dir> <bib_file>")
        sys.exit(1)

    result = detect(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))
