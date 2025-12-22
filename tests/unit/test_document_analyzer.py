"""
Tests for document analyzer service.
"""

import tempfile
from pathlib import Path

import pytest
from qa_engine.domain.services.document_analyzer import (
    DocumentAnalyzer,
    DocumentMetrics,
    ProcessingStrategy,
)


class TestDocumentAnalyzer:
    """Tests for DocumentAnalyzer."""

    def test_analyze_single_file(self):
        """Test analyzing a single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("line 1\nline 2\nline 3\n")

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.total_files == 1
            assert metrics.total_lines == 3  # 3 lines (trailing newline not counted as line)
            assert metrics.largest_file == str(tex_file)

    def test_analyze_multiple_files(self):
        """Test analyzing multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "a.tex").write_text("line 1\nline 2\n")
            (Path(tmpdir) / "b.tex").write_text("line 1\n")

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.total_files == 2
            assert metrics.total_lines == 3  # 2 + 1 lines

    def test_analyze_empty_directory(self):
        """Test analyzing empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.total_files == 0
            assert metrics.total_lines == 0

    def test_strategy_single_pass(self):
        """Test single_pass strategy for small documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("\n".join(["line"] * 100))

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.recommended_strategy == ProcessingStrategy.SINGLE_PASS

    def test_strategy_file_by_file(self):
        """Test file_by_file strategy for medium documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("\n".join(["line"] * 5000))

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.recommended_strategy == ProcessingStrategy.FILE_BY_FILE

    def test_strategy_chunked(self):
        """Test chunked strategy for large documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("\n".join(["line"] * 20000))

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.recommended_strategy == ProcessingStrategy.CHUNKED

    def test_strategy_parallel_chunked(self):
        """Test parallel_chunked strategy for very large documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("\n".join(["line"] * 40000))

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.recommended_strategy == ProcessingStrategy.PARALLEL_CHUNKED

    def test_nested_files(self):
        """Test finding files in nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "chapters"
            subdir.mkdir()
            (subdir / "ch1.tex").write_text("chapter 1\n")
            (subdir / "ch2.tex").write_text("chapter 2\n")
            (Path(tmpdir) / "main.tex").write_text("main\n")

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            assert metrics.total_files == 3

    def test_token_estimate(self):
        """Test token estimation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("\n".join(["line"] * 100))

            analyzer = DocumentAnalyzer()
            metrics = analyzer.analyze(tmpdir)

            # 100 lines * 10 tokens/line estimate
            assert metrics.estimated_tokens == metrics.total_lines * 10
