"""
Automated QA Pipeline.

Runs all QA detectors and fixers automatically using skill tools.
This is the main entry point for the QA system.
"""

import sys
import io
from pathlib import Path
from typing import Dict, List, Any

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import all detectors
from qa_engine.infrastructure.detection import (
    BiDiDetector,
    TableDetector,
    CodeDetector,
    BibDetector,
)

# Import all fixers
from qa_engine.infrastructure.fixing import (
    BiDiFixer,
    TableFixer,
    CodeFixer,
    BibFixer,
    TikzFixer,
)


class QAPipeline:
    """Automated QA detection and fixing pipeline."""

    def __init__(self):
        """Initialize detectors and fixers."""
        self.detectors = {
            "bidi": BiDiDetector(),
            "table": TableDetector(),
            "code": CodeDetector(),
            "bib": BibDetector(),
        }
        self.fixers = {
            "bidi": BiDiFixer(),
            "table": TableFixer(),
            "code": CodeFixer(),
            "bib": BibFixer(),
            "tikz": TikzFixer(),
        }

    def run_detection(self, content: str, file_path: str) -> Dict[str, List]:
        """Run all detectors on content."""
        results = {}
        for name, detector in self.detectors.items():
            issues = detector.detect(content, file_path)
            results[name] = [self._issue_to_dict(i) for i in issues]
        return results

    def run_fixes(
        self, content: str, issues: Dict[str, List], file_path: str
    ) -> str:
        """Apply all fixes to content."""
        fixed = content

        # Fix BiDi issues (numbers, english, acronyms)
        bidi_issues = issues.get("bidi", [])
        bidi_fixable = [
            i for i in bidi_issues
            if i["rule"] in ["bidi-numbers", "bidi-english", "bidi-acronym"]
        ]
        if bidi_fixable:
            fixed = self._apply_bidi_fix(fixed, bidi_fixable)

        # Fix TikZ issues
        tikz_issues = [i for i in bidi_issues if i["rule"] == "bidi-tikz-rtl"]
        if tikz_issues:
            fixed = self._apply_tikz_fix(fixed, tikz_issues)

        # Fix code issues
        code_issues = issues.get("code", [])
        code_fixable = [
            i for i in code_issues
            if i["rule"] == "code-background-overflow"
        ]
        if code_fixable:
            fixed = self._apply_code_fix(fixed, code_fixable)

        # Fix table issues
        table_issues = issues.get("table", [])
        if table_issues:
            fixed = self._apply_table_fix(fixed, table_issues)

        # Fix bib issues
        bib_issues = issues.get("bib", [])
        if bib_issues:
            # First fix malformed citation keys (modifies content)
            malformed = [i for i in bib_issues if i["rule"] == "bib-malformed-cite-key"]
            if malformed:
                fixed = self._apply_malformed_bib_fix(fixed, malformed)
            # Then create .bib files for remaining issues
            self._apply_bib_fix(fixed, bib_issues, file_path)

        return fixed

    def _apply_bidi_fix(self, content: str, issues: List[Dict]) -> str:
        """Apply BiDi fixes using BiDiFixer."""
        from qa_engine.domain.models.issue import Issue, Severity
        issue_objs = [self._dict_to_issue(i) for i in issues]
        return self.fixers["bidi"].fix(content, issue_objs)

    def _apply_tikz_fix(self, content: str, issues: List[Dict]) -> str:
        """Apply TikZ fixes using TikzFixer."""
        issue_objs = [self._dict_to_issue(i) for i in issues]
        return self.fixers["tikz"].fix(content, issue_objs)

    def _apply_code_fix(self, content: str, issues: List[Dict]) -> str:
        """Apply code fixes using CodeFixer."""
        issue_objs = [self._dict_to_issue(i) for i in issues]
        return self.fixers["code"].fix(content, issue_objs)

    def _apply_table_fix(self, content: str, issues: List[Dict]) -> str:
        """Apply table fixes using TableFixer."""
        issue_objs = [self._dict_to_issue(i) for i in issues]
        return self.fixers["table"].fix(content, issue_objs)

    def _apply_malformed_bib_fix(self, content: str, issues: List[Dict]) -> str:
        """Apply malformed citation key fixes using BibFixer."""
        issue_objs = [self._dict_to_issue(i) for i in issues]
        return self.fixers["bib"].fix(content, issue_objs)

    def _apply_bib_fix(
        self, content: str, issues: List[Dict], file_path: str
    ) -> None:
        """Apply bib fixes using BibFixer."""
        issue_objs = [self._dict_to_issue(i) for i in issues]
        self.fixers["bib"].fix_with_context(content, issue_objs, file_path)

    def _issue_to_dict(self, issue) -> Dict[str, Any]:
        """Convert Issue object to dictionary."""
        return {
            "rule": issue.rule,
            "file": issue.file,
            "line": issue.line,
            "content": issue.content,
            "severity": issue.severity.value,
            "fix": issue.fix,
            "context": issue.context,
        }

    def _dict_to_issue(self, d: Dict) -> Any:
        """Convert dictionary to Issue object."""
        from qa_engine.domain.models.issue import Issue, Severity
        return Issue(
            rule=d["rule"],
            file=d.get("file", ""),
            line=d.get("line", 0),
            content=d.get("content", ""),
            severity=Severity(d.get("severity", "warning")),
            fix=d.get("fix"),
            context=d.get("context", {}),
        )

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file: detect issues, apply fixes."""
        content = file_path.read_text(encoding="utf-8", errors="replace")
        original = content

        # Phase 1: Detection
        issues = self.run_detection(content, str(file_path))

        # Phase 2: Fixing
        fixed = self.run_fixes(content, issues, str(file_path))

        # Phase 3: Save if changed
        changed = fixed != original
        if changed:
            file_path.write_text(fixed, encoding="utf-8")

        # Phase 4: Re-detect to count remaining
        remaining = self.run_detection(fixed, str(file_path))
        remaining_count = sum(len(v) for v in remaining.values())

        return {
            "file": file_path.name,
            "issues_found": sum(len(v) for v in issues.values()),
            "issues_remaining": remaining_count,
            "changed": changed,
            "details": {
                "bidi": len(issues.get("bidi", [])),
                "table": len(issues.get("table", [])),
                "code": len(issues.get("code", [])),
                "bib": len(issues.get("bib", [])),
            },
        }

    def process_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Process all .tex files in directory."""
        tex_files = list(dir_path.rglob("*.tex"))
        results = []
        total_found = 0
        total_remaining = 0

        for tex_file in tex_files:
            try:
                result = self.process_file(tex_file)
                results.append(result)
                total_found += result["issues_found"]
                total_remaining += result["issues_remaining"]
            except Exception as e:
                print(f"Error processing {tex_file.name}: {e}")

        return {
            "files_processed": len(tex_files),
            "total_issues_found": total_found,
            "total_issues_remaining": total_remaining,
            "files": results,
        }


def main():
    """Main entry point."""
    pipeline = QAPipeline()

    # Process CLS-examples
    test_data = Path(__file__).parent.parent / "test-data" / "CLS-examples"

    if not test_data.exists():
        print(f"Test data not found: {test_data}")
        return

    print("\n" + "=" * 60)
    print("QA PIPELINE - AUTOMATED DETECTION AND FIXING")
    print("=" * 60)

    # Run multiple passes until no more fixes
    max_passes = 3
    for pass_num in range(1, max_passes + 1):
        print(f"\n--- Pass {pass_num} ---")
        result = pipeline.process_directory(test_data)

        print(f"Files processed: {result['files_processed']}")
        print(f"Issues found: {result['total_issues_found']}")
        print(f"Issues remaining: {result['total_issues_remaining']}")

        # Show per-file summary
        for file_result in result["files"]:
            if file_result["issues_found"] > 0:
                print(f"  {file_result['file']}: "
                      f"{file_result['issues_found']} -> "
                      f"{file_result['issues_remaining']}")

        # Stop if no issues remaining or no progress
        if result["total_issues_remaining"] == 0:
            print("\nAll issues fixed!")
            break
        if result["total_issues_found"] == result["total_issues_remaining"]:
            print("\nNo more fixes possible with current rules.")
            break

    print("\n" + "=" * 60)
    print("QA PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
