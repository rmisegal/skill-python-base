r"""
Cross-Reference Detector Tool
Detects cross-chapter reference issues in LaTeX documents.

Version: 1.0.0

Detection Rules:
- ref-hardcoded-chapter: Hardcoded "ראה פרק \en{X}"
- ref-hardcoded-chapters-range: Hardcoded "פרקים \en{X-Y}"
- ref-hardcoded-chapters-list: Hardcoded "פרקים \en{X, Y}"
- ref-undefined-label: \ref{} to undefined label
- ref-orphan-label: \label{} never referenced
- ref-standalone-unsafe: Reference breaks in standalone mode
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Issue:
    """Represents a detected reference issue."""
    rule: str
    severity: Severity
    file: str
    line: int
    content: str
    fix: str
    chapter_refs: List[str] = field(default_factory=list)


class RefDetector:
    """Detects cross-chapter reference issues in LaTeX documents."""

    # Patterns for hardcoded chapter references (Hebrew)
    PATTERNS = {
        # Single chapter: ראה פרק \en{2} or ראה פרק \en{2})
        "ref-hardcoded-chapter": re.compile(
            r'(?:ראה|עיין|ב)?\s*פרק\s*\\en\{(\d+)\}',
            re.UNICODE
        ),
        # Chapter range: פרקים \en{2-3} or \en{2--3}
        "ref-hardcoded-chapters-range": re.compile(
            r'פרקים\s*\\en\{(\d+)\s*[-–—]+\s*(\d+)\}',
            re.UNICODE
        ),
        # Chapter list: פרקים \en{6, 9} or \en{6,9}
        "ref-hardcoded-chapters-list": re.compile(
            r'פרקים\s*\\en\{(\d+(?:\s*,\s*\d+)+)\}',
            re.UNICODE
        ),
        # Forward reference: יוסבר בפרק \en{5}
        "ref-forward-chapter": re.compile(
            r'יוסבר\s*(?:ב)?פרק\s*\\en\{(\d+)\}',
            re.UNICODE
        ),
    }

    # Pattern for \ref{} and \label{}
    REF_PATTERN = re.compile(r'\\ref\{([^}]+)\}')
    LABEL_PATTERN = re.compile(r'\\label\{([^}]+)\}')

    # Pattern for already-correct \chapterref{}
    CHAPTERREF_PATTERN = re.compile(r'\\chapterref\{[^}]+\}')

    def __init__(self):
        self.rules = [
            "ref-hardcoded-chapter",
            "ref-hardcoded-chapters-range",
            "ref-hardcoded-chapters-list",
            "ref-undefined-label",
            "ref-orphan-label",
            "ref-standalone-unsafe",
        ]

    def get_rules(self) -> List[str]:
        """Return list of detection rules."""
        return self.rules

    def detect_in_content(
        self, content: str, file_path: str = "input.tex"
    ) -> List[Issue]:
        """Detect reference issues in content string."""
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('%'):
                continue

            # Detect hardcoded chapter references
            issues.extend(
                self._detect_hardcoded_refs(line, line_num, file_path)
            )

        return issues

    def _detect_hardcoded_refs(
        self, line: str, line_num: int, file_path: str
    ) -> List[Issue]:
        """Detect hardcoded chapter references in a line."""
        issues = []

        # Skip if line already uses \chapterref
        if self.CHAPTERREF_PATTERN.search(line):
            return issues

        # Single chapter reference
        for match in self.PATTERNS["ref-hardcoded-chapter"].finditer(line):
            chapter = match.group(1)
            issues.append(Issue(
                rule="ref-hardcoded-chapter",
                severity=Severity.HIGH,
                file=file_path,
                line=line_num,
                content=match.group(0),
                fix=f"Use \\chapterref{{{chapter}}} instead",
                chapter_refs=[chapter]
            ))

        # Chapter range
        for match in self.PATTERNS["ref-hardcoded-chapters-range"].finditer(line):
            start, end = match.group(1), match.group(2)
            issues.append(Issue(
                rule="ref-hardcoded-chapters-range",
                severity=Severity.HIGH,
                file=file_path,
                line=line_num,
                content=match.group(0),
                fix=f"Use \\chapterrefrange{{{start}}}{{{end}}} instead",
                chapter_refs=[start, end]
            ))

        # Chapter list
        for match in self.PATTERNS["ref-hardcoded-chapters-list"].finditer(line):
            chapters = [c.strip() for c in match.group(1).split(',')]
            issues.append(Issue(
                rule="ref-hardcoded-chapters-list",
                severity=Severity.HIGH,
                file=file_path,
                line=line_num,
                content=match.group(0),
                fix=f"Use \\chapterreflist{{{','.join(chapters)}}} instead",
                chapter_refs=chapters
            ))

        # Forward reference
        for match in self.PATTERNS["ref-forward-chapter"].finditer(line):
            chapter = match.group(1)
            issues.append(Issue(
                rule="ref-hardcoded-chapter",
                severity=Severity.HIGH,
                file=file_path,
                line=line_num,
                content=match.group(0),
                fix=f"Use \\chapterrefforward{{{chapter}}} instead",
                chapter_refs=[chapter]
            ))

        return issues

    def detect_in_file(self, file_path: Path) -> Dict:
        """Detect reference issues in a LaTeX file."""
        if not file_path.exists():
            return {"status": "ERROR", "message": f"File not found: {file_path}"}

        content = file_path.read_text(encoding='utf-8', errors='ignore')
        issues = self.detect_in_content(content, str(file_path))

        return self._format_result(issues, [str(file_path)])

    def detect_in_project(
        self, project_path: Path, chapters_dir: str = "chapters"
    ) -> Dict:
        """Detect reference issues across all chapters in a project."""
        chapters_path = project_path / chapters_dir

        if not chapters_path.exists():
            # Try direct tex files
            tex_files = list(project_path.glob("*.tex"))
        else:
            tex_files = sorted(chapters_path.glob("chapter*.tex"))

        all_issues = []
        all_labels: Dict[str, Tuple[str, int]] = {}  # label -> (file, line)
        all_refs: List[Tuple[str, str, int]] = []  # (label, file, line)

        for tex_file in tex_files:
            content = tex_file.read_text(encoding='utf-8', errors='ignore')
            file_str = str(tex_file.relative_to(project_path))

            # Detect hardcoded references
            issues = self.detect_in_content(content, file_str)
            all_issues.extend(issues)

            # Collect labels and refs for cross-file analysis
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Extract labels
                for match in self.LABEL_PATTERN.finditer(line):
                    label = match.group(1)
                    all_labels[label] = (file_str, line_num)

                # Extract refs
                for match in self.REF_PATTERN.finditer(line):
                    label = match.group(1)
                    all_refs.append((label, file_str, line_num))

        # Check for undefined refs
        for label, file_path, line_num in all_refs:
            if label not in all_labels:
                all_issues.append(Issue(
                    rule="ref-undefined-label",
                    severity=Severity.CRITICAL,
                    file=file_path,
                    line=line_num,
                    content=f"\\ref{{{label}}}",
                    fix=f"Define \\label{{{label}}} or remove reference"
                ))

        # Check for orphan labels
        referenced_labels = {ref[0] for ref in all_refs}
        for label, (file_path, line_num) in all_labels.items():
            if label not in referenced_labels:
                # Skip common patterns that don't need refs
                if any(label.startswith(p) for p in ['chap:', 'sec:', 'subsec:']):
                    continue
                all_issues.append(Issue(
                    rule="ref-orphan-label",
                    severity=Severity.LOW,
                    file=file_path,
                    line=line_num,
                    content=f"\\label{{{label}}}",
                    fix="Remove unused label or add \\ref{}"
                ))

        return self._format_result(
            all_issues, [str(f.relative_to(project_path)) for f in tex_files]
        )

    def _format_result(
        self, issues: List[Issue], files_checked: List[str]
    ) -> Dict:
        """Format detection result as dictionary."""
        # Count by category
        hardcoded = sum(1 for i in issues if i.rule.startswith("ref-hardcoded"))
        undefined = sum(1 for i in issues if i.rule == "ref-undefined-label")
        orphan = sum(1 for i in issues if i.rule == "ref-orphan-label")

        # Determine verdict
        if any(i.severity == Severity.CRITICAL for i in issues):
            verdict = "CRITICAL"
        elif any(i.severity == Severity.HIGH for i in issues):
            verdict = "WARNING"
        elif issues:
            verdict = "INFO"
        else:
            verdict = "OK"

        return {
            "skill": "qa-ref-detect",
            "status": "DONE",
            "verdict": verdict,
            "issues": [
                {
                    "rule": i.rule,
                    "file": i.file,
                    "line": i.line,
                    "content": i.content,
                    "severity": i.severity.value,
                    "fix": i.fix,
                    "chapter_refs": i.chapter_refs,
                }
                for i in issues
            ],
            "summary": {
                "files_checked": len(files_checked),
                "total_issues": len(issues),
                "hardcoded_refs": hardcoded,
                "undefined_refs": undefined,
                "orphan_labels": orphan,
            },
            "triggers": ["qa-ref-fix"] if issues else [],
        }


# Module-level functions for skill integration
_detector = RefDetector()


def detect_in_file(file_path: str) -> Dict:
    """Detect reference issues in a LaTeX file."""
    return _detector.detect_in_file(Path(file_path))


def detect_in_content(content: str, file_path: str = "input.tex") -> List[Dict]:
    """Detect reference issues in content string."""
    issues = _detector.detect_in_content(content, file_path)
    return [
        {
            "rule": i.rule,
            "file": i.file,
            "line": i.line,
            "content": i.content,
            "severity": i.severity.value,
            "fix": i.fix,
        }
        for i in issues
    ]


def detect_in_project(project_path: str, chapters_dir: str = "chapters") -> Dict:
    """Detect reference issues across all chapters in a project."""
    return _detector.detect_in_project(Path(project_path), chapters_dir)


def get_rules() -> List[str]:
    """Return list of detection rules."""
    return _detector.get_rules()


if __name__ == "__main__":
    import sys
    import json

    # Ensure UTF-8 output for Windows
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print("Usage: python tool.py <project_path> [chapters_dir]")
        print("   or: python tool.py --file <file_path>")
        sys.exit(1)

    if sys.argv[1] == "--file":
        result = detect_in_file(sys.argv[2])
    else:
        chapters = sys.argv[2] if len(sys.argv) > 2 else "chapters"
        result = detect_in_project(sys.argv[1], chapters)

    print(json.dumps(result, indent=2, ensure_ascii=False))
