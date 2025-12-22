"""Unit tests for Image Validator."""
import pytest
from pathlib import Path
import tempfile
import os
from qa_engine.infrastructure.validation import ImageValidator, ValidationResult, FigureComparison


class TestImageValidator:
    """Tests for ImageValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ImageValidator()

    def test_find_figures_in_content(self):
        """Test finding figures in LaTeX content."""
        content = r"""
\begin{figure}[htbp]
\includegraphics{test.png}
\caption{Test figure}
\end{figure}
"""
        figures = self.validator._find_figures(content)
        assert len(figures) == 1
        assert figures[0][0] == "test.png"

    def test_find_multiple_figures(self):
        """Test finding multiple figures."""
        content = r"""
\begin{figure}
\includegraphics{fig1.png}
\caption{First}
\end{figure}
\begin{figure}
\includegraphics{fig2.jpg}
\caption{Second}
\end{figure}
"""
        figures = self.validator._find_figures(content)
        assert len(figures) == 2

    def test_find_standalone_includegraphics(self):
        """Test finding includegraphics outside figure env."""
        content = r"\includegraphics[width=0.5\textwidth]{diagram.pdf}"
        figures = self.validator._find_figures(content)
        assert len(figures) == 1
        assert figures[0][0] == "diagram.pdf"

    def test_record_before_state(self):
        """Test recording issues before fixes."""
        issues = [
            {"rule": "img-missing-file", "content": "test.png"},
            {"rule": "img-missing-file", "content": "other.jpg"},
        ]
        self.validator.record_before_state(issues)
        assert len(self.validator._before_state) == 2

    def test_validate_with_existing_images(self):
        """Test validation when images exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test image
            img_path = Path(tmpdir) / "test.png"
            img_path.write_text("fake image")

            content = r"\includegraphics{test.png}"
            self.validator = ImageValidator(project_root=Path(tmpdir))
            result = self.validator.validate_after_fixes(content, Path(tmpdir))

            assert result.figures_verified == 1
            assert result.all_rendered == True
            assert result.verdict == "PASS"

    def test_validate_with_missing_images(self):
        """Test validation when images are missing."""
        content = r"\includegraphics{nonexistent.png}"
        result = self.validator.validate_after_fixes(content)

        assert result.figures_verified == 1
        assert result.all_rendered == False
        assert result.verdict == "FAIL"
        assert 1 in result.still_missing

    def test_comparison_records(self):
        """Test before/after comparison records."""
        # Use unique filename that definitely doesn't exist
        issues = [{"rule": "img-missing-file", "content": "nonexistent_unique_test_image_xyz123.png"}]
        self.validator.record_before_state(issues)

        content = r"\includegraphics{nonexistent_unique_test_image_xyz123.png}"
        result = self.validator.validate_after_fixes(content)

        assert len(result.comparison) == 1
        assert result.comparison[0].before == "MISSING"
        assert result.comparison[0].after == "MISSING"  # File doesn't exist

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"\includegraphics{test.png}"
        result = self.validator.validate_after_fixes(content)
        output = self.validator.to_dict(result)

        assert output["skill"] == "qa-img-validate"
        assert output["status"] == "DONE"
        assert "verdict" in output
        assert "figures_verified" in output
        assert "all_rendered" in output
        assert "comparison" in output

    def test_verdict_pass(self):
        """Test PASS verdict when all images render."""
        result = ValidationResult(figures_verified=2, all_rendered=True)
        assert result.verdict == "PASS"

    def test_verdict_fail(self):
        """Test FAIL verdict when images missing."""
        result = ValidationResult(figures_verified=2, all_rendered=False)
        assert result.verdict == "FAIL"

    def test_image_search_paths(self):
        """Test image search in multiple directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create image in images/ subdirectory
            images_dir = Path(tmpdir) / "images"
            images_dir.mkdir()
            (images_dir / "test.png").write_text("fake")

            self.validator = ImageValidator(project_root=Path(tmpdir))
            assert self.validator._image_exists("test.png", Path(tmpdir)) == True

    def test_image_extension_inference(self):
        """Test image extension is inferred if not specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "diagram.png").write_text("fake")

            self.validator = ImageValidator(project_root=Path(tmpdir))
            # Path without extension should find .png
            assert self.validator._image_exists("diagram", Path(tmpdir)) == True

    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        before_issues = [{"rule": "img-missing-file", "content": "fig.png"}]
        content = r"\includegraphics{fig.png}"

        result = self.validator.validate_content(content, before_issues)

        assert result.figures_verified == 1
        assert len(result.comparison) == 1
