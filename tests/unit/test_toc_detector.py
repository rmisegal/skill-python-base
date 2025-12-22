"""
Unit tests for TOC detector.

Tests both counter-related rules and l@ block-aware detection.
"""

import pytest
from pathlib import Path

from qa_engine.infrastructure.detection.toc_detector import TOCDetector


class TestTOCDetectorCounterRules:
    """Tests for counter-related TOC rules."""

    def setup_method(self):
        self.detector = TOCDetector()

    def test_detect_thechapter_no_wrapper(self):
        """Detect \\thechapter without \\textenglish wrapper."""
        content = r"\renewcommand{\thechapter}{\arabic{chapter}}"
        issues = self.detector.detect(content, "test.cls")
        rules = [i.rule for i in issues]
        assert "toc-thechapter-no-wrapper" in rules

    def test_no_issue_when_thechapter_wrapped(self):
        """No issue when \\thechapter is properly wrapped."""
        content = r"\renewcommand{\thechapter}{\textenglish{\arabic{chapter}}}"
        issues = self.detector.detect(content, "test.cls")
        rules = [i.rule for i in issues]
        assert "toc-thechapter-no-wrapper" not in rules


class TestTOCDetectorLAtBlockRules:
    """Tests for l@ command block-aware detection."""

    def setup_method(self):
        self.detector = TOCDetector()

    def test_detect_lchapter_no_rtl(self):
        """Detect \\l@chapter without RTL direction."""
        content = r"""
  \renewcommand*\l@chapter[2]{%
    \ifnum \c@tocdepth >\m@ne
      \begingroup
        \parindent \z@
        #1\nobreak\hfill\hb@xt@\@pnumwidth{\hss \textenglish{#2}}\par
      \endgroup
    \fi
  }
"""
        issues = self.detector.detect(content, "test.cls")
        rules = [i.rule for i in issues]
        assert "toc-lchapter-no-rtl" in rules

    def test_no_issue_when_lchapter_has_rtl(self):
        """No issue when \\l@chapter has RTL direction."""
        content = r"""
  \renewcommand*\l@chapter[2]{%
    \ifnum \c@tocdepth >\m@ne
      \begingroup
        \pardir TRT\textdir TRT
        #1\nobreak\hfill\hb@xt@\@pnumwidth{\hss \textenglish{#2}}\par
      \endgroup
    \fi
  }
"""
        issues = self.detector.detect(content, "test.cls")
        rules = [i.rule for i in issues]
        assert "toc-lchapter-no-rtl" not in rules

    def test_rtl_elsewhere_not_counted(self):
        """RTL direction elsewhere in file should not satisfy l@ check."""
        content = r"""
% Other command with RTL
\pardir TRT\textdir TRT

% l@chapter WITHOUT RTL
\renewcommand*\l@chapter[2]{%
  \begingroup
    #1\nobreak\hfill\hb@xt@\@pnumwidth{\hss \textenglish{#2}}\par
  \endgroup
}
"""
        issues = self.detector.detect(content, "test.cls")
        rules = [i.rule for i in issues]
        assert "toc-lchapter-no-rtl" in rules

    def test_detect_all_three_l_at_commands(self):
        """Detect all three l@ commands without RTL."""
        content = r"""
\renewcommand*\l@chapter[2]{\begingroup #1 \endgroup}
\renewcommand*\l@section[2]{\begingroup #1 \endgroup}
\renewcommand*\l@subsection[2]{\begingroup #1 \endgroup}
"""
        issues = self.detector.detect(content, "test.cls")
        rules = [i.rule for i in issues]
        assert "toc-lchapter-no-rtl" in rules
        assert "toc-lsection-no-rtl" in rules
        assert "toc-lsubsection-no-rtl" in rules


class TestTOCDetectorOnRealCLS:
    """Integration tests on real CLS file."""

    @pytest.fixture
    def cls_path(self):
        path = Path(__file__).parent.parent.parent / "test-data" / "CLS-examples"
        cls = path / "hebrew-academic-template.cls"
        if not cls.exists():
            pytest.skip("CLS-examples not found")
        return cls

    def test_detect_l_at_issues_in_real_cls(self, cls_path):
        """Detect l@ command issues in real CLS file."""
        detector = TOCDetector()
        issues = detector.detect_in_cls_file(str(cls_path))

        # The real CLS has l@ commands without RTL direction
        rules = [i.rule for i in issues]
        assert "toc-lchapter-no-rtl" in rules
        assert "toc-lsection-no-rtl" in rules
        assert "toc-lsubsection-no-rtl" in rules

    def test_report_format(self, cls_path):
        """Verify report format."""
        detector = TOCDetector()
        issues = detector.detect_in_cls_file(str(cls_path))

        for issue in issues:
            assert issue.rule is not None
            assert issue.file is not None
            assert issue.line > 0
            assert issue.severity is not None
