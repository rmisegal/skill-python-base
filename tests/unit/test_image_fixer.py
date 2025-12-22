"""Unit tests for Image Fixer."""
import pytest
import tempfile
from pathlib import Path
from qa_engine.infrastructure.fixing.image_fixer import ImageFixer


class TestImageFixer:
    """Tests for ImageFixer."""

    def setup_method(self):
        self.fixer = ImageFixer()

    def test_add_graphicspath_inserts_before_document(self):
        """Test graphicspath is added before begin document."""
        content = "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}"
        result = self.fixer.add_graphicspath(content, ["images/", "figures/"])
        assert "\\graphicspath{{images/}{figures/}}" in result
        assert result.index("\\graphicspath") < result.index("\\begin{document}")

    def test_add_graphicspath_skips_if_exists(self):
        """Test no duplicate graphicspath added."""
        content = "\\graphicspath{{old/}}\n\\begin{document}\n\\end{document}"
        result = self.fixer.add_graphicspath(content, ["new/"])
        assert result == content
        assert "new/" not in result

    def test_add_graphicspath_default_paths(self):
        """Test default paths are used when none specified."""
        content = "\\begin{document}\\end{document}"
        result = self.fixer.add_graphicspath(content)
        assert "images/" in result
        assert "../images/" in result

    def test_fix_preamble_graphicspath_creates_paths(self):
        """Test fix_preamble_graphicspath auto-detects image directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create structure: shared/preamble.tex, images/figures/test.png
            shared = root / "shared"
            shared.mkdir()
            preamble = shared / "preamble.tex"
            preamble.write_text("\\begin{document}\\end{document}")

            img_dir = root / "images" / "figures"
            img_dir.mkdir(parents=True)
            (img_dir / "test.png").write_text("fake")

            result = self.fixer.fix_preamble_graphicspath(preamble, root)
            assert result is True

            content = preamble.read_text()
            assert "\\graphicspath" in content

    def test_fix_preamble_graphicspath_skips_if_exists(self):
        """Test no change if graphicspath already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            preamble = Path(tmpdir) / "preamble.tex"
            preamble.write_text("\\graphicspath{{old/}}\n\\begin{document}\\end{document}")

            result = self.fixer.fix_preamble_graphicspath(preamble)
            assert result is False

    def test_fix_preamble_graphicspath_returns_false_if_no_file(self):
        """Test returns False if file doesn't exist."""
        result = self.fixer.fix_preamble_graphicspath(Path("/nonexistent/file.tex"))
        assert result is False

    def test_detect_image_paths_finds_png(self):
        """Test _detect_image_paths finds PNG files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            preamble = root / "shared" / "preamble.tex"
            preamble.parent.mkdir()
            preamble.write_text("")

            (root / "images").mkdir()
            (root / "images" / "test.png").write_text("fake")

            paths = self.fixer._detect_image_paths(preamble, root)
            assert any("images" in p for p in paths)

    def test_fix_image_path_replaces_path(self):
        """Test fix_image_path replaces specific path."""
        content = r"\includegraphics{old/image.png}"
        result = self.fixer.fix_image_path(content, "old/image.png", "new/image.png")
        assert "new/image.png" in result
        assert "old/image.png" not in result

    def test_fix_image_path_preserves_options(self):
        """Test fix_image_path preserves width options."""
        content = r"\includegraphics[width=0.5\textwidth]{old.png}"
        result = self.fixer.fix_image_path(content, "old.png", "new.png")
        assert r"[width=0.5\textwidth]" in result
        assert "new.png" in result

    def test_lowercase_filenames(self):
        """Test lowercase conversion of filenames."""
        content = r"\includegraphics{Images/TEST.PNG}"
        pattern = r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}"
        result = self.fixer._lowercase_filenames(content, pattern)
        assert "images/test.png" in result

    def test_get_patterns_returns_dict(self):
        """Test get_patterns returns pattern definitions."""
        patterns = self.fixer.get_patterns()
        assert isinstance(patterns, dict)
        assert len(patterns) > 0
        for name, pat in patterns.items():
            assert "find" in pat
            assert "description" in pat

    def test_add_graphicspath_preamble_without_begin_document(self):
        """Test graphicspath added after usetikzlibrary in preamble files."""
        content = "\\usepackage{graphicx}\n\\usetikzlibrary{arrows}\n% end"
        result = self.fixer.add_graphicspath(content, ["images/"])
        assert "\\graphicspath{{images/}}" in result
        assert result.index("\\usetikzlibrary") < result.index("\\graphicspath")
