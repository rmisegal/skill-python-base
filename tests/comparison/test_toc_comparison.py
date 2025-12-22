"""
Comparison test: TOC detection via Python tools.

Tests that local Python tools detect the same (or more) issues
as global Claude CLI skills would.
"""

import pytest
from pathlib import Path

from qa_engine.infrastructure.detection.toc_detector import TOCDetector


# Expected issues from global skill qa-cls-toc-detect
# Based on analysis of CLS-examples/hebrew-academic-template.cls
# Line ranges updated to accommodate CLS file changes
EXPECTED_GLOBAL_ISSUES = {
    "toc-lchapter-no-rtl": {
        "description": "l@chapter missing RTL direction",
        "expected_line_range": (660, 680),
    },
    "toc-lsection-no-rtl": {
        "description": "l@section missing RTL direction",
        "expected_line_range": (680, 700),
    },
    "toc-lsubsection-no-rtl": {
        "description": "l@subsection missing RTL direction",
        "expected_line_range": (695, 715),
    },
}


class TestTOCDetectionComparison:
    """Compare Python detection with expected global skill output."""

    @pytest.fixture
    def cls_path(self):
        path = Path(__file__).parent.parent.parent / "test-data" / "CLS-examples"
        cls = path / "hebrew-academic-template.cls"
        if not cls.exists():
            pytest.skip("CLS-examples not found")
        return cls

    def test_python_detects_all_expected_issues(self, cls_path):
        """Python tools detect all issues that global skills would."""
        detector = TOCDetector()
        issues = detector.detect_in_cls_file(str(cls_path))

        detected_rules = {i.rule for i in issues}

        for expected_rule in EXPECTED_GLOBAL_ISSUES.keys():
            assert expected_rule in detected_rules, (
                f"Python did not detect {expected_rule}"
            )

    def test_line_numbers_match_expected(self, cls_path):
        """Detected line numbers are in expected ranges."""
        detector = TOCDetector()
        issues = detector.detect_in_cls_file(str(cls_path))

        for issue in issues:
            if issue.rule in EXPECTED_GLOBAL_ISSUES:
                expected = EXPECTED_GLOBAL_ISSUES[issue.rule]
                lo, hi = expected["expected_line_range"]
                assert lo <= issue.line <= hi, (
                    f"{issue.rule} at line {issue.line} "
                    f"not in expected range ({lo}, {hi})"
                )

    def test_python_equal_or_better(self, cls_path):
        """Python tools should detect >= issues vs global skills."""
        detector = TOCDetector()
        issues = detector.detect_in_cls_file(str(cls_path))

        # Python should find AT LEAST all expected issues
        detected = len(issues)
        expected = len(EXPECTED_GLOBAL_ISSUES)

        print(f"\n--- TOC Detection Comparison ---")
        print(f"Expected from global skill: {expected} issues")
        print(f"Detected by Python tool:    {detected} issues")
        print(f"Detected rules:")
        for issue in issues:
            print(f"  - {issue.rule} (line {issue.line})")

        assert detected >= expected, (
            f"Python detected {detected} issues, expected >= {expected}"
        )


class TestTOCDetectionPerformance:
    """Test performance of Python detection."""

    @pytest.fixture
    def cls_path(self):
        path = Path(__file__).parent.parent.parent / "test-data" / "CLS-examples"
        cls = path / "hebrew-academic-template.cls"
        if not cls.exists():
            pytest.skip("CLS-examples not found")
        return cls

    def test_detection_speed(self, cls_path):
        """Detection should complete quickly."""
        import time

        detector = TOCDetector()
        content = cls_path.read_text(encoding="utf-8", errors="replace")

        start = time.perf_counter()
        for _ in range(100):
            detector.detect(content, str(cls_path))
        elapsed = time.perf_counter() - start

        per_run = elapsed / 100 * 1000  # ms
        print(f"\n100 detections in {elapsed:.3f}s ({per_run:.2f}ms/run)")

        # Should complete 100 runs in under 1 second
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s for 100 runs"

    def test_deterministic_results(self, cls_path):
        """Detection should be deterministic (same result every time)."""
        detector = TOCDetector()
        content = cls_path.read_text(encoding="utf-8", errors="replace")

        results = []
        for _ in range(5):
            issues = detector.detect(content, str(cls_path))
            results.append([(i.rule, i.line) for i in issues])

        # All results should be identical
        for i, result in enumerate(results[1:], 2):
            assert result == results[0], f"Run {i} differs from run 1"
