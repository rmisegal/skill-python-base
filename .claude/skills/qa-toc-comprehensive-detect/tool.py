r"""
TOC Comprehensive Detector Tool
Detects BiDi and structure issues in Hebrew-English TOC files

Version: 1.0.0
"""

import re
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Issue:
    """Detected TOC issue."""
    rule: str
    severity: str
    line: int
    content: str
    message: str


def detect_english_subsection_rtl(toc_path: Path) -> List[Issue]:
    r"""
    Detect PURELY English entries with wrong TOC handler.

    Two problems to detect:
    1. Using 'subsection' handler (text renders backwards)
    2. Using 'englishsubsection' with wrong alignment (left-aligned in RTL doc)
    """
    issues = []

    if not toc_path.exists():
        return issues

    content = toc_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.splitlines()

    # Pattern 1: English entry using subsection (text renders RTL)
    pattern1 = r'\\contentsline\s*\{subsection\}\{\\LRE\s*\{\\textenglish\s*\{([^}]+)\}\}\}'

    # Pattern 2: English entry using englishsubsection (check if exists)
    pattern2 = r'\\contentsline\s*\{englishsubsection\}\{\\textenglish\s*\{([^}]+)\}\}'

    for i, line in enumerate(lines, 1):
        # Check for wrong handler (subsection)
        match1 = re.search(pattern1, line)
        if match1:
            title = match1.group(1)
            issues.append(Issue(
                rule="toc-english-entry-not-ltr",
                severity="CRITICAL",
                line=i,
                content=line.strip()[:80],
                message=f"English entry '{title}' uses 'subsection' handler - "
                        f"text renders backwards. Need 'englishsubsection'."
            ))
            continue

        # Check for englishsubsection (need to verify alignment is correct)
        match2 = re.search(pattern2, line)
        if match2:
            # This is using englishsubsection - check CLS for proper alignment
            # The handler should use \pardir TRT (RTL paragraph) + \textdir TLT
            # We can't check alignment from .toc file, need CLS check
            pass  # Handler exists, alignment check is in CLS fixer

    return issues


def detect(toc_path: str) -> Dict:
    """
    Main detection function.

    Args:
        toc_path: Path to .toc file

    Returns:
        Detection report with issues
    """
    path = Path(toc_path)
    issues = []

    # Run all detectors
    issues.extend(detect_english_subsection_rtl(path))

    # Count by severity
    critical = sum(1 for i in issues if i.severity == "CRITICAL")
    warning = sum(1 for i in issues if i.severity == "WARNING")
    info = sum(1 for i in issues if i.severity == "INFO")

    return {
        "summary": {
            "total_issues": len(issues),
            "critical": critical,
            "warning": warning,
            "info": info
        },
        "issues": [
            {
                "rule": i.rule,
                "severity": i.severity,
                "line": i.line,
                "content": i.content,
                "message": i.message,
                "fix": "CLS needs l@englishsubsection handler with \\pardir TLT"
            }
            for i in issues
        ]
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python tool.py <toc_file>")
        sys.exit(1)

    result = detect(sys.argv[1])
    # Use ASCII encoding to avoid console encoding issues
    print(json.dumps(result, indent=2, ensure_ascii=True))
