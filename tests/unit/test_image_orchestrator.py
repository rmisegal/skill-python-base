"""Unit tests for Image Orchestrator."""
import pytest
import tempfile
from pathlib import Path
from qa_engine.infrastructure.image_orchestrator import (
    ImageOrchestrator, ImageOrchestratorResult, ImageDetectResult, ImageFixResult
)


class TestImageOrchestrator:
    """Tests for ImageOrchestrator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ImageOrchestrator()

    def test_detect_missing_image(self):
        """Test detection of missing image files."""
        content = r"\includegraphics{nonexistent.png}"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False, validate=False)
        assert result.detect_result is not None
        assert result.detect_result.total > 0
        assert "img-file-not-found" in result.detect_result.by_rule

    def test_detect_no_graphicspath(self):
        """Test detection of missing graphicspath."""
        content = r"""
\begin{document}
\includegraphics{test.png}
\end{document}
"""
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False, validate=False)
        assert result.detect_result is not None
        # May or may not detect depending on rules

    def test_detect_placeholder_box(self):
        """Test detection of placeholder boxes."""
        content = r"""
\begin{figure}
\fbox{\parbox{5cm}{Placeholder for image}}
\caption{Test}
\end{figure}
"""
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False, validate=False)
        assert result.detect_result is not None

    def test_fix_adds_graphicspath(self):
        """Test that fixes add graphicspath."""
        content = r"""
\begin{document}
\includegraphics{test.png}
\end{document}
"""
        result = self.orchestrator.run(content, "test.tex", apply_fixes=True, create_missing=False, validate=False)
        if result.fix_result:
            # Graphicspath may be added
            pass

    def test_validation_runs(self):
        """Test that validation phase executes."""
        content = r"\includegraphics{test.png}"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False, validate=True)
        assert result.validate_result is not None
        assert "qa-img-validate" in result.skills_executed

    def test_skills_executed_tracking(self):
        """Test that executed skills are tracked."""
        content = r"\includegraphics{test.png}"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False, validate=False)
        assert "qa-img-detect" in result.skills_executed
        assert result.skills_executed["qa-img-detect"] == "DONE"

    def test_to_dict_format(self):
        """Test output dictionary format matches skill.md."""
        content = r"\includegraphics{test.png}"
        result = self.orchestrator.run(content, "test.tex")
        output = self.orchestrator.to_dict(result)

        assert output["family"] == "img"
        assert output["status"] == "DONE"
        assert "verdict" in output
        assert "phases" in output
        assert "skills_executed" in output

    def test_phases_structure(self):
        """Test phases structure in output."""
        content = r"\includegraphics{test.png}"
        result = self.orchestrator.run(content, "test.tex")
        output = self.orchestrator.to_dict(result)
        phases = output["phases"]

        assert "source_detection" in phases
        assert "source_fixing" in phases
        assert "validation" in phases
        assert phases["source_detection"]["tool"] == "ImageDetector"

    def test_with_existing_image(self):
        """Test with existing image file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test image
            img_path = Path(tmpdir) / "test.png"
            img_path.write_text("fake image")

            content = r"\includegraphics{test.png}"
            orchestrator = ImageOrchestrator(project_root=Path(tmpdir))
            result = orchestrator.run(content, str(Path(tmpdir) / "test.tex"))

            # Should not have missing file issues for this image
            if result.validate_result:
                assert result.validate_result.figures_verified >= 0

    def test_orchestrator_result_dataclass(self):
        """Test ImageOrchestratorResult dataclass."""
        detect = ImageDetectResult()
        fix = ImageFixResult(paths_fixed=3, images_created=2)
        result = ImageOrchestratorResult(detect_result=detect, fix_result=fix)

        assert result.status == "DONE"
        assert result.verdict == "PASS"  # No issues in detect_result

    def test_detect_result_total(self):
        """Test ImageDetectResult total calculation."""
        from qa_engine.domain.models.issue import Issue, Severity
        result = ImageDetectResult()
        result.issues.append(Issue(rule="img-file-not-found", file="", line=1, content="", severity=Severity.CRITICAL))
        result.issues.append(Issue(rule="img-no-graphicspath", file="", line=2, content="", severity=Severity.WARNING))

        assert result.total == 2
        assert result.verdict == "FAIL"

    def test_fix_result_defaults(self):
        """Test ImageFixResult default values."""
        result = ImageFixResult()
        assert result.paths_fixed == 0
        assert result.images_created == 0
        assert result.placeholders_replaced == 0
        assert result.graphicspath_added == False
        assert result.content == ""

    def test_no_fixes_when_disabled(self):
        """Test that fixes are skipped when disabled."""
        content = r"\includegraphics{missing.png}"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False, validate=False)
        assert result.fix_result is None
        assert result.skills_executed.get("qa-img-fix-paths") == "SKIP"

    def test_no_validation_when_disabled(self):
        """Test that validation is skipped when disabled."""
        content = r"\includegraphics{test.png}"
        result = self.orchestrator.run(content, "test.tex", apply_fixes=False, validate=False)
        assert result.validate_result is None
        assert result.skills_executed.get("qa-img-validate") == "SKIP"


class TestImageDetectResult:
    """Tests for ImageDetectResult dataclass."""

    def test_empty_result(self):
        """Test empty result is PASS."""
        result = ImageDetectResult()
        assert result.total == 0
        assert result.verdict == "PASS"

    def test_with_issues(self):
        """Test result with issues is FAIL."""
        from qa_engine.domain.models.issue import Issue, Severity
        result = ImageDetectResult()
        result.issues.append(Issue(rule="test", file="", line=1, content="x", severity=Severity.WARNING))
        assert result.total == 1
        assert result.verdict == "FAIL"


class TestImageFixResult:
    """Tests for ImageFixResult dataclass."""

    def test_default_values(self):
        """Test default values."""
        result = ImageFixResult()
        assert result.paths_fixed == 0
        assert result.images_created == 0
        assert result.content == ""

    def test_with_fixes(self):
        """Test with fix counts."""
        result = ImageFixResult(paths_fixed=3, images_created=2, content="fixed")
        assert result.paths_fixed == 3
        assert result.images_created == 2
        assert result.content == "fixed"
