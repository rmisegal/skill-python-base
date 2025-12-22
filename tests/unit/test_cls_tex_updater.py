"""Unit tests for CLSTexUpdater."""

import tempfile
from pathlib import Path

import pytest
from qa_engine.infrastructure.fixing.cls_tex_updater import (
    CLSTexUpdater, CLSTexUpdateReport, TexUpdateResult,
    CLS_UPGRADE_PATTERNS, REDUNDANT_PACKAGES,
)


class TestCLSTexUpdater:
    """Test cases for CLSTexUpdater."""

    def test_update_documentclass(self):
        """Test documentclass update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text(r"\documentclass{article}", encoding="utf-8")

            updater = CLSTexUpdater()
            result = updater.update_file(tex_file)

            content = tex_file.read_text(encoding="utf-8")
            assert "hebrew-academic-template" in content
            assert result.documentclass_updated is True

    def test_skip_already_updated_documentclass(self):
        """Test documentclass not changed if already using CLS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text(r"\documentclass{hebrew-academic-template}", encoding="utf-8")

            updater = CLSTexUpdater()
            result = updater.update_file(tex_file)

            assert result.documentclass_updated is False

    def test_hebmath_pattern_replacement(self):
        """Test Hebrew in math replacement with \\hebmath."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text(r"$x_{\text{שלום}}$", encoding="utf-8")

            updater = CLSTexUpdater()
            result = updater.update_file(tex_file)

            content = tex_file.read_text(encoding="utf-8")
            assert r"\hebmath{שלום}" in content
            assert "hebmath" in result.patterns_applied

    def test_remove_redundant_packages(self):
        """Test removal of packages now provided by CLS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text(
                r"\usepackage{biblatex}" + "\n" + r"\usepackage{geometry}",
                encoding="utf-8",
            )

            updater = CLSTexUpdater()
            result = updater.update_file(tex_file)

            content = tex_file.read_text(encoding="utf-8")
            assert "biblatex" not in content
            assert "geometry" not in content
            assert "biblatex" in result.packages_removed
            assert "geometry" in result.packages_removed

    def test_update_project(self):
        """Test updating multiple files in project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple tex files
            (Path(tmpdir) / "main.tex").write_text(r"\documentclass{article}", encoding="utf-8")
            (Path(tmpdir) / "chapter.tex").write_text(r"$\text{עברית}$", encoding="utf-8")

            updater = CLSTexUpdater()
            report = updater.update_project(Path(tmpdir))

            assert report.files_updated == 2
            assert report.total_changes >= 2

    def test_no_changes_needed(self):
        """Test file with no changes needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text(r"Just regular text", encoding="utf-8")

            updater = CLSTexUpdater()
            result = updater.update_file(tex_file)

            assert not result.patterns_applied
            assert not result.packages_removed
            assert not result.documentclass_updated

    def test_get_patterns(self):
        """Test get_patterns returns available patterns."""
        updater = CLSTexUpdater()
        patterns = updater.get_patterns()

        assert "hebmath" in patterns
        assert len(patterns) > 0

    def test_preserve_documentclass_options(self):
        """Test that documentclass options are preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text(r"\documentclass[12pt,a4paper]{article}", encoding="utf-8")

            updater = CLSTexUpdater()
            updater.update_file(tex_file)

            content = tex_file.read_text(encoding="utf-8")
            assert "[12pt,a4paper]" in content
            assert "hebrew-academic-template" in content
