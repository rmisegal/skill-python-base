r"""
Cross-Reference Fixer Tool
Fixes cross-chapter reference issues in LaTeX documents.

Version: 1.0.0

Converts hardcoded chapter references to CLS commands:
- "ראה פרק \en{2}" -> \chapterref{2}
- "פרקים \en{2-3}" -> \chapterrefrange{2}{3}
- "פרקים \en{6, 9}" -> \chapterreflist{6,9}
- "יוסבר בפרק \en{5}" -> \chapterrefforward{5}
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Fix:
    """Represents a fix to apply."""
    line: int
    before: str
    after: str
    rule: str


class RefFixer:
    """Fixes cross-chapter reference issues in LaTeX documents."""

    # Fix patterns - match and replace
    FIX_PATTERNS = [
        # Forward reference: יוסבר בפרק \en{5} -> \chapterrefforward{5}
        # Must come before generic "פרק" pattern
        (
            re.compile(r'יוסבר\s+(?:ב)?פרק\s*\\en\{(\d+)\}', re.UNICODE),
            r'\\chapterrefforward{\1}',
            "ref-hardcoded-chapter"
        ),
        # Chapter range: פרקים \en{2-3} -> \chapterrefrange{2}{3}
        (
            re.compile(r'פרקים\s*\\en\{(\d+)\s*[-–—]+\s*(\d+)\}', re.UNICODE),
            r'\\chapterrefrange{\1}{\2}',
            "ref-hardcoded-chapters-range"
        ),
        # Chapter list: פרקים \en{6, 9} -> \chapterreflist{6,9}
        (
            re.compile(r'פרקים\s*\\en\{(\d+(?:\s*,\s*\d+)+)\}', re.UNICODE),
            lambda m: f'\\chapterreflist{{{m.group(1).replace(" ", "")}}}',
            "ref-hardcoded-chapters-list"
        ),
        # Single chapter with prefix: ראה פרק \en{2} -> \chapterref{2}
        # Handles: ראה פרק, עיין בפרק, בפרק, לפרק
        (
            re.compile(
                r'((?:ראה|עיין\s*ב?|ל)?)\s*פרק\s*\\en\{(\d+)\}',
                re.UNICODE
            ),
            lambda m: (
                f'{m.group(1)}\\chapterref{{{m.group(2)}}}'
                if m.group(1) else f'\\chapterref{{{m.group(2)}}}'
            ),
            "ref-hardcoded-chapter"
        ),
    ]

    # Pattern to skip already-fixed references
    SKIP_PATTERN = re.compile(r'\\chapter(?:ref|refrange|reflist|refforward)\{')

    def fix_in_content(self, content: str, file_path: str = "input.tex") -> Tuple[str, List[Fix]]:
        """Fix reference issues in content string."""
        fixes = []
        lines = content.split('\n')
        fixed_lines = []

        for line_num, line in enumerate(lines, 1):
            fixed_line = line

            # Skip comments and already-fixed lines
            if line.strip().startswith('%') or self.SKIP_PATTERN.search(line):
                fixed_lines.append(line)
                continue

            # Apply each fix pattern
            for pattern, replacement, rule in self.FIX_PATTERNS:
                matches = list(pattern.finditer(fixed_line))
                if matches:
                    for match in reversed(matches):  # Reverse to preserve positions
                        before = match.group(0)
                        if callable(replacement):
                            after = replacement(match)
                        else:
                            after = pattern.sub(replacement, before)

                        # Record the fix
                        fixes.append(Fix(
                            line=line_num,
                            before=before,
                            after=after,
                            rule=rule
                        ))

                    # Apply all fixes to line
                    if callable(replacement):
                        fixed_line = pattern.sub(replacement, fixed_line)
                    else:
                        fixed_line = pattern.sub(replacement, fixed_line)

            fixed_lines.append(fixed_line)

        return '\n'.join(fixed_lines), fixes

    def fix_in_file(self, file_path: Path, write: bool = True) -> Dict:
        """Fix reference issues in a LaTeX file."""
        if not file_path.exists():
            return {"status": "ERROR", "message": f"File not found: {file_path}"}

        content = file_path.read_text(encoding='utf-8', errors='ignore')
        fixed_content, fixes = self.fix_in_content(content, str(file_path))

        if write and fixes:
            file_path.write_text(fixed_content, encoding='utf-8')

        return self._format_result(fixes, str(file_path), write)

    def fix_in_project(
        self, project_path: Path, chapters_dir: str = "chapters", write: bool = True
    ) -> Dict:
        """Fix reference issues across all chapters in a project."""
        chapters_path = project_path / chapters_dir

        if not chapters_path.exists():
            tex_files = list(project_path.glob("*.tex"))
        else:
            tex_files = sorted(chapters_path.glob("chapter*.tex"))

        all_fixes = []
        files_modified = []

        for tex_file in tex_files:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            fixed_content, fixes = self.fix_in_content(
                content, str(tex_file.relative_to(project_path))
            )

            if fixes:
                if write:
                    tex_file.write_text(fixed_content, encoding='utf-8')
                    files_modified.append(str(tex_file.relative_to(project_path)))
                all_fixes.extend(fixes)

        return {
            "skill": "qa-ref-fix",
            "status": "DONE",
            "fixes_applied": len(all_fixes),
            "files_modified": len(files_modified),
            "files": files_modified,
            "changes": [
                {
                    "file": f.line,  # Note: line stored here for grouping
                    "line": f.line,
                    "before": f.before,
                    "after": f.after,
                    "rule": f.rule,
                }
                for f in all_fixes
            ],
        }

    def _format_result(self, fixes: List[Fix], file_path: str, written: bool) -> Dict:
        """Format fix result as dictionary."""
        return {
            "skill": "qa-ref-fix",
            "status": "DONE",
            "fixes_applied": len(fixes),
            "files_modified": 1 if fixes and written else 0,
            "file": file_path,
            "written": written,
            "changes": [
                {
                    "line": f.line,
                    "before": f.before,
                    "after": f.after,
                    "rule": f.rule,
                }
                for f in fixes
            ],
        }


# Module-level functions for skill integration
_fixer = RefFixer()


def fix_in_content(content: str, file_path: str = "input.tex") -> Tuple[str, List[Dict]]:
    """Fix reference issues in content string."""
    fixed, fixes = _fixer.fix_in_content(content, file_path)
    return fixed, [
        {"line": f.line, "before": f.before, "after": f.after, "rule": f.rule}
        for f in fixes
    ]


def fix_in_file(file_path: str, write: bool = True) -> Dict:
    """Fix reference issues in a LaTeX file."""
    return _fixer.fix_in_file(Path(file_path), write)


def fix_in_project(
    project_path: str, chapters_dir: str = "chapters", write: bool = True
) -> Dict:
    """Fix reference issues across all chapters in a project."""
    return _fixer.fix_in_project(Path(project_path), chapters_dir, write)


def get_fixed_content(content: str) -> str:
    """Auto-detect and fix issues, return fixed content."""
    fixed, _ = _fixer.fix_in_content(content)
    return fixed


if __name__ == "__main__":
    import sys
    import json

    # Ensure UTF-8 output for Windows
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print("Usage: python tool.py <project_path> [chapters_dir] [--dry-run]")
        print("   or: python tool.py --file <file_path> [--dry-run]")
        sys.exit(1)

    write = "--dry-run" not in sys.argv

    if sys.argv[1] == "--file":
        result = fix_in_file(sys.argv[2], write)
    else:
        chapters = "chapters"
        if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
            chapters = sys.argv[2]
        result = fix_in_project(sys.argv[1], chapters, write)

    print(json.dumps(result, indent=2, ensure_ascii=False))
