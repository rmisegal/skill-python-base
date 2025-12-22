"""
Integration tests for CLS-examples.

Runs all QA detectors on the CLS-examples folder and reports issues.
"""

import pytest
from pathlib import Path
from typing import List, Dict

from qa_engine.infrastructure.detection import (
    BiDiDetector,
    TableDetector,
    SubfilesDetector,
    BibDetector,
    CodeDetector,
    TypesetDetector,
)
from qa_engine.infrastructure.detection.toc_detector import TOCDetector
from qa_engine.domain.models.issue import Issue


# Path to test data
TEST_DATA_PATH = Path(__file__).parent.parent.parent / "test-data" / "CLS-examples"


def get_all_tex_files() -> List[Path]:
    """Get all .tex files in test data."""
    if not TEST_DATA_PATH.exists():
        return []
    return list(TEST_DATA_PATH.rglob("*.tex"))


class TestBiDiDetectionOnExamples:
    """Test BiDi detection on CLS-examples."""

    def setup_method(self):
        """Setup detector."""
        self.detector = BiDiDetector()

    @pytest.mark.parametrize("tex_file", get_all_tex_files())
    def test_bidi_detection(self, tex_file: Path):
        """Run BiDi detection on each file."""
        content = tex_file.read_text(encoding="utf-8", errors="replace")
        issues = self.detector.detect(content, str(tex_file))
        # Test passes - we're collecting issues for review
        print(f"\n{tex_file.name}: {len(issues)} BiDi issues")
        for issue in issues[:5]:  # Show first 5
            print(f"  - Line {issue.line}: {issue.rule}")


class TestTableDetectionOnExamples:
    """Test Table detection on CLS-examples."""

    def setup_method(self):
        """Setup detector."""
        self.detector = TableDetector()

    @pytest.mark.parametrize("tex_file", get_all_tex_files())
    def test_table_detection(self, tex_file: Path):
        """Run Table detection on each file."""
        content = tex_file.read_text(encoding="utf-8", errors="replace")
        issues = self.detector.detect(content, str(tex_file))
        print(f"\n{tex_file.name}: {len(issues)} Table issues")
        for issue in issues[:5]:
            print(f"  - Line {issue.line}: {issue.rule}")


class TestCodeDetectionOnExamples:
    """Test Code detection on CLS-examples."""

    def setup_method(self):
        """Setup detector."""
        self.detector = CodeDetector()

    @pytest.mark.parametrize("tex_file", get_all_tex_files())
    def test_code_detection(self, tex_file: Path):
        """Run Code detection on each file."""
        content = tex_file.read_text(encoding="utf-8", errors="replace")
        issues = self.detector.detect(content, str(tex_file))
        print(f"\n{tex_file.name}: {len(issues)} Code issues")
        for issue in issues[:5]:
            print(f"  - Line {issue.line}: {issue.rule}")


class TestBibDetectionOnExamples:
    """Test Bibliography detection on CLS-examples."""

    def setup_method(self):
        """Setup detector."""
        self.detector = BibDetector()

    @pytest.mark.parametrize("tex_file", get_all_tex_files())
    def test_bib_detection(self, tex_file: Path):
        """Run Bibliography detection on each file."""
        content = tex_file.read_text(encoding="utf-8", errors="replace")
        issues = self.detector.detect(content, str(tex_file))
        print(f"\n{tex_file.name}: {len(issues)} Bibliography issues")
        for issue in issues[:5]:
            print(f"  - Line {issue.line}: {issue.rule}")


class TestTOCDetectionOnExamples:
    """Test TOC detection on CLS files in CLS-examples."""

    def setup_method(self):
        """Setup detector."""
        self.detector = TOCDetector()

    def test_toc_detection_on_cls(self):
        """Run TOC detection on CLS file."""
        cls_file = TEST_DATA_PATH / "hebrew-academic-template.cls"
        if not cls_file.exists():
            pytest.skip("CLS file not found")
        issues = self.detector.detect_in_cls_file(str(cls_file))
        print(f"\n{cls_file.name}: {len(issues)} TOC issues")
        for issue in issues:
            print(f"  - Line {issue.line}: {issue.rule} ({issue.severity.name})")
        # Should detect l@ command issues
        rules = [i.rule for i in issues]
        assert "toc-lchapter-no-rtl" in rules


class TestAllDetectorsReport:
    """Run all detectors and generate summary report."""

    def test_full_qa_report(self):
        """Generate full QA report for all files."""
        tex_files = get_all_tex_files()
        if not tex_files:
            pytest.skip("No test files found")

        detectors = {
            "BiDi": BiDiDetector(),
            "Table": TableDetector(),
            "Code": CodeDetector(),
            "Bib": BibDetector(),
            "TOC": TOCDetector(),
        }

        all_issues: Dict[str, List[Issue]] = {}
        summary = {"total_files": len(tex_files), "total_issues": 0}

        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                print(f"Error reading {tex_file}: {e}")
                continue

            file_issues = []
            for name, detector in detectors.items():
                issues = detector.detect(content, str(tex_file))
                file_issues.extend(issues)

            if file_issues:
                all_issues[str(tex_file)] = file_issues
                summary["total_issues"] += len(file_issues)

        # Print summary report
        print("\n" + "=" * 60)
        print("QA DETECTION REPORT - CLS-EXAMPLES")
        print("=" * 60)
        print(f"Total files scanned: {summary['total_files']}")
        print(f"Total issues found: {summary['total_issues']}")
        print("-" * 60)

        # Group by rule
        rule_counts: Dict[str, int] = {}
        for issues in all_issues.values():
            for issue in issues:
                rule_counts[issue.rule] = rule_counts.get(issue.rule, 0) + 1

        print("\nIssues by Rule:")
        for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
            print(f"  {rule}: {count}")

        print("-" * 60)
        print("\nIssues by File:")
        for file_path, issues in sorted(all_issues.items()):
            print(f"\n{Path(file_path).name}: {len(issues)} issues")
            # Group by rule
            file_rules: Dict[str, int] = {}
            for issue in issues:
                file_rules[issue.rule] = file_rules.get(issue.rule, 0) + 1
            for rule, count in file_rules.items():
                print(f"    {rule}: {count}")

        print("\n" + "=" * 60)

        # Test passes regardless - this is a diagnostic test
        assert True
