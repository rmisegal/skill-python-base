"""Unit tests for Typeset Detection aligned with qa-typeset-detect skill.md v1.5."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.typeset.detection import (
    LogWarningDetector, TikzDetector, ItemsepDetector, FullTypesetDetector,
    TypesetDetectResult
)


class TestLogWarningDetector:
    """Tests for log file parsing (Step 2)."""

    def setup_method(self):
        self.detector = LogWarningDetector()

    # Overfull hbox tests
    def test_overfull_hbox_critical(self):
        """Test CRITICAL for overfull hbox > 10pt."""
        log = "Overfull \\hbox (15.5pt too wide) in paragraph at lines 100--101"
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.overfull_hbox) == 1
        assert result.overfull_hbox[0].amount_pt == 15.5
        assert result.overfull_hbox[0].severity == "CRITICAL"

    def test_overfull_hbox_warning(self):
        """Test WARNING for overfull hbox 1-10pt."""
        log = "Overfull \\hbox (5.0pt too wide) in paragraph at lines 50--51"
        result = self.detector.detect_log_content(log, "test.log")
        assert result.overfull_hbox[0].severity == "WARNING"

    def test_overfull_hbox_info(self):
        """Test INFO for overfull hbox < 1pt."""
        log = "Overfull \\hbox (0.5pt too wide) in paragraph at lines 20--21"
        result = self.detector.detect_log_content(log, "test.log")
        assert result.overfull_hbox[0].severity == "INFO"

    def test_overfull_hbox_extracts_lines(self):
        """Test line number extraction."""
        log = "Overfull \\hbox (4.9pt too wide) in paragraph at lines 162--163"
        result = self.detector.detect_log_content(log, "test.log")
        assert result.overfull_hbox[0].lines == [162, 163]

    # Underfull hbox tests
    def test_underfull_hbox_warning(self):
        """Test WARNING for underfull hbox badness >= 10000."""
        log = "Underfull \\hbox (badness 10000) in paragraph at lines 45--46"
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.underfull_hbox) == 1
        assert result.underfull_hbox[0].badness == 10000
        assert result.underfull_hbox[0].severity == "WARNING"

    def test_underfull_hbox_info(self):
        """Test INFO for underfull hbox badness < 5000."""
        log = "Underfull \\hbox (badness 1000) in paragraph at lines 45--46"
        result = self.detector.detect_log_content(log, "test.log")
        assert result.underfull_hbox[0].severity == "INFO"

    # Vbox tests
    def test_overfull_vbox_always_critical(self):
        """Test CRITICAL for any overfull vbox."""
        log = "Overfull \\vbox (10.0pt too high) has occurred"
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.overfull_vbox) == 1
        assert result.overfull_vbox[0].severity == "CRITICAL"

    def test_underfull_vbox_warning(self):
        """Test WARNING for underfull vbox badness 10000."""
        log = "Underfull \\vbox (badness 10000) has occurred while \\output is active"
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.underfull_vbox) == 1
        assert result.underfull_vbox[0].severity == "WARNING"
        assert "page break" in result.underfull_vbox[0].context

    # Undefined reference tests
    def test_undefined_reference(self):
        """Test undefined reference detection."""
        log = "LaTeX Warning: Reference `tab:python-libraries' on page 27 undefined on input line 185."
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.undefined_references) == 1
        assert result.undefined_references[0].reference == "tab:python-libraries"
        assert result.undefined_references[0].page == 27
        assert result.undefined_references[0].input_line == 185
        assert result.undefined_references[0].severity == "CRITICAL"

    # Undefined citation tests
    def test_undefined_citation(self):
        """Test undefined citation detection."""
        log = "LaTeX Warning: Citation `smith2020' on page 5 undefined on input line 42."
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.undefined_citations) == 1
        assert result.undefined_citations[0].citation == "smith2020"
        assert result.undefined_citations[0].severity == "CRITICAL"

    # Float too large tests
    def test_float_too_large_critical(self):
        """Test CRITICAL for float > 50pt too large."""
        log = "LaTeX Warning: Float too large for page by 165.89pt on input line 141."
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.float_too_large) == 1
        assert result.float_too_large[0].overflow_pt == 165.89
        assert result.float_too_large[0].severity == "CRITICAL"

    def test_float_too_large_warning(self):
        """Test WARNING for float <= 50pt too large."""
        log = "LaTeX Warning: Float too large for page by 30.0pt on input line 50."
        result = self.detector.detect_log_content(log, "test.log")
        assert result.float_too_large[0].severity == "WARNING"

    # Known issues tests
    def test_known_issue_pythonbox(self):
        """Test known issue whitelist for pythonbox."""
        log = "! LaTeX Error: \\begin{pythonbox} on input line 318 ended by \\end{python}."
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.known_issues) == 1
        assert result.known_issues[0].type == "pythonbox_internal"
        assert result.known_issues[0].severity == "INFO"
        assert len(result.latex_errors) == 0  # Not counted as error

    def test_unknown_latex_error_critical(self):
        """Test unknown LaTeX error is CRITICAL."""
        log = "! LaTeX Error: Some unknown error."
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.latex_errors) == 1
        assert result.latex_errors[0].severity == "CRITICAL"

    def test_package_error(self):
        """Test package error detection."""
        log = "! Package tcolorbox Error: Some error message."
        result = self.detector.detect_log_content(log, "test.log")
        assert len(result.package_errors) == 1
        assert result.package_errors[0].package == "tcolorbox"
        assert result.package_errors[0].severity == "WARNING"


class TestTikzDetector:
    """Tests for TikZ source analysis (Step 3)."""

    def setup_method(self):
        self.detector = TikzDetector()

    def test_detects_unconstrained_tikz(self):
        """Test detection of tikzpicture without constraint."""
        content = r"\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 1
        assert result[0].issue == "no_width_constraint"
        assert result[0].severity == "WARNING"

    def test_safe_with_resizebox(self):
        """Test tikzpicture with resizebox is safe."""
        content = r"\resizebox{\textwidth}{!}{\begin{tikzpicture}\draw (0,0);\end{tikzpicture}}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 0

    def test_safe_with_scale(self):
        """Test tikzpicture with scale option is safe."""
        content = r"\begin{tikzpicture}[scale=0.8]\draw (0,0);\end{tikzpicture}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 0

    def test_large_coordinates_critical(self):
        """Test large coordinates (>10) are CRITICAL."""
        content = r"\begin{tikzpicture}\draw (15,0) -- (20,10);\end{tikzpicture}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 1
        assert result[0].issue == "large_coordinates"
        assert result[0].severity == "CRITICAL"


class TestItemsepDetector:
    """Tests for itemsep detection (v1.5)."""

    def setup_method(self):
        self.detector = ItemsepDetector()

    def test_detects_itemize_without_noitemsep(self):
        """Test detection of itemize without noitemsep."""
        content = r"\begin{itemize}\item A\end{itemize}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 1
        assert result[0].env_type == "itemize"

    def test_detects_enumerate_without_noitemsep(self):
        """Test detection of enumerate without noitemsep."""
        content = r"\begin{enumerate}\item A\end{enumerate}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 1
        assert result[0].env_type == "enumerate"

    def test_safe_with_noitemsep(self):
        """Test itemize with noitemsep is safe."""
        content = r"\begin{itemize}[noitemsep]\item A\end{itemize}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 0

    def test_safe_with_nosep(self):
        """Test itemize with nosep is safe."""
        content = r"\begin{itemize}[nosep]\item A\end{itemize}"
        result = self.detector.detect_in_content(content, "test.tex")
        assert len(result) == 0

    def test_check_raggedbottom(self):
        """Test raggedbottom detection."""
        content = r"\documentclass{book}\raggedbottom"
        assert self.detector.check_raggedbottom(content) is True

    def test_check_book_class(self):
        """Test book class detection."""
        content = r"\documentclass{book}"
        assert self.detector.check_book_class(content) is True


class TestFullTypesetDetector:
    """Tests for combined detector."""

    def setup_method(self):
        self.detector = FullTypesetDetector()

    def test_verdict_fail_on_critical(self):
        """Test verdict is FAIL when CRITICAL issues exist."""
        log = "Overfull \\hbox (15.0pt too wide) in paragraph at lines 10--11"
        result = self.detector.log_detector.detect_log_content(log, "test.log")
        assert result.verdict == "FAIL"

    def test_verdict_warning(self):
        """Test verdict is WARNING when only WARNING issues."""
        log = "Overfull \\hbox (5.0pt too wide) in paragraph at lines 10--11"
        result = self.detector.log_detector.detect_log_content(log, "test.log")
        assert result.verdict == "WARNING"

    def test_verdict_pass(self):
        """Test verdict is PASS when no significant issues."""
        log = "Overfull \\hbox (0.5pt too wide) in paragraph at lines 10--11"
        result = self.detector.log_detector.detect_log_content(log, "test.log")
        assert result.verdict == "PASS"

    def test_triggers_hbox(self):
        """Test triggers include hbox fix skill."""
        log = "Overfull \\hbox (5.0pt too wide) in paragraph at lines 10--11"
        result = self.detector.log_detector.detect_log_content(log, "test.log")
        assert "qa-typeset-fix-hbox" in result.triggers

    def test_triggers_refs(self):
        """Test triggers include refs fix skill."""
        log = "LaTeX Warning: Reference `test' on page 1 undefined on input line 10."
        result = self.detector.log_detector.detect_log_content(log, "test.log")
        assert "qa-typeset-fix-refs" in result.triggers

    def test_output_format(self):
        """Test output format matches skill.md."""
        log = "Overfull \\hbox (5.0pt too wide) in paragraph at lines 10--11"
        result = self.detector.log_detector.detect_log_content(log, "test.log")
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-typeset-detect"
        assert output["status"] == "DONE"
        assert "verdict" in output
        assert "warnings" in output
        assert "summary" in output
        assert "triggers" in output

    def test_summary_counts(self):
        """Test summary counts are correct."""
        log = """Overfull \\hbox (5.0pt too wide) in paragraph at lines 10--11
Overfull \\hbox (6.0pt too wide) in paragraph at lines 20--21
Underfull \\vbox (badness 10000) has occurred"""
        result = self.detector.log_detector.detect_log_content(log, "test.log")
        output = self.detector.to_dict(result)

        assert output["summary"]["overfull_hbox"] == 2
        assert output["summary"]["underfull_vbox"] == 1
        assert output["summary"]["total"] == 3

    def test_get_rules(self):
        """Test get_rules returns all detection rules."""
        rules = self.detector.get_rules()
        assert "overfull_hbox_critical" in rules
        assert "overfull_hbox_warning" in rules
        assert "undefined_ref_critical" in rules
        assert "tikz_no_constraint_warning" in rules
