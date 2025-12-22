r"""
CLS Footer BiDi Detector Tool
Detects BiDi issues in fancyhdr footer/header definitions in CLS files

Version: 2.1.0
- Added: TOC page number LTR detection (l@chapter, l@section, etc.)
- Fixed: Skip comment lines (starting with %)
- Added: thepage override detection (breaks frontmatter Roman numerals)
- Added: plain pagestyle detection (chapter opening pages)
"""

import re
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Issue:
    """Detected footer BiDi issue."""
    rule: str
    severity: str
    line: int
    content: str
    message: str
    fix: str


def is_comment_line(line: str) -> bool:
    """Check if line is a LaTeX comment (starts with %)."""
    return line.lstrip().startswith('%')


def detect_thepage_override(cls_path: Path) -> List[Issue]:
    r"""Detect \renewcommand{\thepage} that forces Arabic numerals."""
    issues = []

    if not cls_path.exists():
        return issues

    content = cls_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.splitlines()

    # Pattern for \renewcommand{\thepage}{...}
    thepage_pattern = r'\\renewcommand\s*\{\\thepage\}\s*\{(.+)\}'

    for i, line in enumerate(lines, 1):
        # Skip comment lines
        if is_comment_line(line):
            continue

        match = re.search(thepage_pattern, line)
        if not match:
            continue

        definition = match.group(1)

        # Check if it hardcodes \arabic{page}
        if re.search(r'\\arabic\s*\{page\}', definition):
            issues.append(Issue(
                rule="cls-thepage-forces-arabic",
                severity="CRITICAL",
                line=i,
                content=line.strip()[:80],
                message=r"\renewcommand{\thepage} forces \arabic{page} - "
                        r"breaks \frontmatter Roman numerals (i, ii, iii...)",
                fix=r"Remove \renewcommand{\thepage} - use LTR wrapper in footer instead"
            ))

    return issues


def detect_plain_pagestyle_issues(cls_path: Path) -> List[Issue]:
    r"""Detect issues in \fancypagestyle{plain} definitions."""
    issues = []

    if not cls_path.exists():
        return issues

    content = cls_path.read_text(encoding='utf-8', errors='ignore')

    # Find \fancypagestyle{plain}{...} block
    # This is multi-line, so we need to find the block
    plain_match = re.search(
        r'\\fancypagestyle\s*\{plain\}\s*\{(.*?)\}(?=\s*(?:\\|%|\n\n|$))',
        content,
        re.DOTALL
    )

    if not plain_match:
        # Try simpler pattern for single-line or nearby definition
        lines = content.splitlines()
        in_plain_style = False
        brace_count = 0
        plain_start = -1

        for i, line in enumerate(lines, 1):
            # Skip comment lines
            if is_comment_line(line):
                continue

            if r'\fancypagestyle{plain}' in line:
                in_plain_style = True
                plain_start = i
                brace_count = line.count('{') - line.count('}')
                continue

            if in_plain_style:
                brace_count += line.count('{') - line.count('}')

                # Check for fancyfoot in plain style
                footer_match = re.search(
                    r'\\fancyfoot\s*\[([^\]]*)\]\s*\{(.+)\}', line
                )
                if footer_match:
                    position = footer_match.group(1)
                    foot_content = footer_match.group(2)

                    # Check for page number patterns
                    has_page = (r'\thepage' in foot_content or
                               r'\arabic{page}' in foot_content)

                    if has_page:
                        # Check for proper LTR wrapper
                        has_good_ltr = re.search(
                            r'\\textdir\s+TLT', foot_content
                        )
                        has_weak_ltr = re.search(
                            r'\\textenglish', foot_content
                        )

                        if not has_good_ltr:
                            if has_weak_ltr:
                                issues.append(Issue(
                                    rule="cls-plain-page-weak-ltr",
                                    severity="CRITICAL",
                                    line=i,
                                    content=line.strip()[:80],
                                    message=f"plain style \\fancyfoot[{position}] uses "
                                            f"\\textenglish - doesn't force LTR",
                                    fix=r"Use {\textdir TLT\thepage} in plain style"
                                ))
                            else:
                                issues.append(Issue(
                                    rule="cls-plain-page-no-ltr",
                                    severity="CRITICAL",
                                    line=i,
                                    content=line.strip()[:80],
                                    message=f"plain style \\fancyfoot[{position}] has "
                                            f"page number without LTR wrapper",
                                    fix=r"Use {\textdir TLT\thepage} in plain style"
                                ))

                if brace_count <= 0:
                    in_plain_style = False

    return issues


def detect_missing_plain_pagestyle(cls_path: Path) -> List[Issue]:
    r"""Detect if plain pagestyle is not redefined (uses default which may have issues)."""
    issues = []

    if not cls_path.exists():
        return issues

    content = cls_path.read_text(encoding='utf-8', errors='ignore')

    # Check if fancyhdr is used but plain style not redefined
    has_fancyhdr = r'\pagestyle{fancy}' in content or r'\usepackage{fancyhdr}' in content
    has_plain_style = r'\fancypagestyle{plain}' in content

    if has_fancyhdr and not has_plain_style:
        issues.append(Issue(
            rule="cls-plain-style-not-defined",
            severity="WARNING",
            line=0,
            content="fancyhdr used but \\fancypagestyle{plain} not defined",
            message="plain page style not redefined - chapter opening pages "
                    "may have default footer with RTL page numbers",
            fix=r"Add \fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{{\textdir TLT\thepage}}}"
        ))

    return issues


def detect_footer_page_number_issues(cls_path: Path) -> List[Issue]:
    """Detect page numbers in footers without proper LTR wrapper."""
    issues = []

    if not cls_path.exists():
        return issues

    content = cls_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.splitlines()

    # Pattern for fancyfoot/fancyhead with page number
    footer_pattern = r'\\fancy(foot|head)\s*\[([^\]]+)\]\s*\{(.+)\}'

    # Patterns that indicate page numbers
    page_patterns = [
        r'\\thepage',
        r'\\arabic\{page\}',
    ]

    # Good LTR wrappers for fancyhdr context
    good_wrappers = [
        r'\\textdir\s+TLT',
        r'\\LR\s*\{',
        r'\\lr\s*\{',
    ]

    # Insufficient wrappers (don't work in fancyhdr)
    weak_wrappers = [
        r'\\textenglish\s*\{',
        r'\\en\s*\{',
    ]

    # Track if we're inside a fancypagestyle block (to avoid double-reporting)
    in_pagestyle = False

    for i, line in enumerate(lines, 1):
        # Skip comment lines
        if is_comment_line(line):
            continue

        if r'\fancypagestyle' in line:
            in_pagestyle = True
        if in_pagestyle and line.strip() == '}':
            in_pagestyle = False
            continue

        # Skip if inside a pagestyle block (handled by other detector)
        if in_pagestyle:
            continue

        match = re.search(footer_pattern, line)
        if not match:
            continue

        element_type = match.group(1)  # foot or head
        position = match.group(2)       # LE, RO, etc.
        content_str = match.group(3)    # The content

        # Check if contains page number patterns
        has_page_number = any(
            re.search(p, content_str) for p in page_patterns
        )

        if not has_page_number:
            continue

        # Check if has good LTR wrapper
        has_good_wrapper = any(
            re.search(p, content_str, re.IGNORECASE) for p in good_wrappers
        )

        # Check if using weak wrapper
        has_weak_wrapper = any(
            re.search(p, content_str, re.IGNORECASE) for p in weak_wrappers
        )

        if has_good_wrapper:
            continue  # OK

        if has_weak_wrapper:
            issues.append(Issue(
                rule="cls-footer-page-weak-ltr",
                severity="CRITICAL",
                line=i,
                content=line.strip()[:80],
                message=f"\\fancy{element_type}[{position}] uses \\textenglish for "
                        f"page number - doesn't force LTR in fancyhdr context",
                fix=r"Use {\textdir TLT\thepage} instead of \textenglish{\thepage}"
            ))
        else:
            issues.append(Issue(
                rule="cls-footer-page-no-ltr",
                severity="CRITICAL",
                line=i,
                content=line.strip()[:80],
                message=f"\\fancy{element_type}[{position}] has page number without "
                        f"LTR wrapper - will render RTL (reversed)",
                fix=r"Wrap page number with {\textdir TLT\thepage}"
            ))

    return issues


def detect_toc_page_number_issues(cls_path: Path) -> List[Issue]:
    """Detect TOC page numbers using weak LTR wrapper (textenglish instead of textdir TLT)."""
    issues = []

    if not cls_path.exists():
        return issues

    content = cls_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.splitlines()

    # Pattern for l@chapter, l@section, l@subsection page number handling
    # Looking for: \hss \textenglish{#2} or similar weak patterns
    toc_handler_pattern = r'\\l@(chapter|section|subsection|subsubsection)'
    pnum_weak_pattern = r'\\textenglish\s*\{\s*#2\s*\}'
    pnum_good_pattern = r'\\textdir\s+TLT\s*#2'

    in_toc_handler = False
    handler_name = ""
    handler_start = 0

    for i, line in enumerate(lines, 1):
        if is_comment_line(line):
            continue

        # Check if entering a TOC handler definition
        handler_match = re.search(toc_handler_pattern, line)
        if handler_match and ('renewcommand' in line or 'newcommand' in line):
            in_toc_handler = True
            handler_name = handler_match.group(1)
            handler_start = i
            continue

        if in_toc_handler:
            # Check for weak page number wrapper
            if re.search(pnum_weak_pattern, line):
                issues.append(Issue(
                    rule="cls-toc-page-weak-ltr",
                    severity="CRITICAL",
                    line=i,
                    content=line.strip()[:80],
                    message=f"l@{handler_name} uses \\textenglish{{#2}} for page - "
                            f"doesn't force LTR, page numbers render RTL (reversed)",
                    fix=r"Use {\textdir TLT #2} instead of \textenglish{#2}"
                ))

            # Check if handler ends (closing brace at start of line or empty def)
            if line.strip() == '}' or re.search(r'^\s*\}%?\s*$', line):
                in_toc_handler = False

    return issues


def detect(cls_path: str) -> Dict:
    """
    Main detection function.

    Args:
        cls_path: Path to CLS file

    Returns:
        Detection report with issues
    """
    path = Path(cls_path)
    issues = []

    # Run all detectors
    issues.extend(detect_thepage_override(path))
    issues.extend(detect_plain_pagestyle_issues(path))
    issues.extend(detect_missing_plain_pagestyle(path))
    issues.extend(detect_footer_page_number_issues(path))
    issues.extend(detect_toc_page_number_issues(path))

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
                "fix": i.fix
            }
            for i in issues
        ]
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python tool.py <cls_file>")
        sys.exit(1)

    result = detect(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=True))
