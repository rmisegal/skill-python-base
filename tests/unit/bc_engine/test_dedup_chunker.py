"""
Unit tests for ChapterChunker.

Tests text chunking and environment exclusion.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from bc_engine.dedup.chunker import ChapterChunker
from bc_engine.dedup.config import DedupConfig


class TestChapterChunker:
    """Tests for ChapterChunker class."""

    def setup_method(self):
        """Reset config singleton before each test."""
        DedupConfig.reset()

    def _create_mock_config(self):
        """Create mock config with test values."""
        config = MagicMock(spec=DedupConfig)
        config.chunk_size = 10
        config.min_chunk_words = 5
        config.excluded_environments = ["pythonbox", "equation"]
        return config

    def test_chunk_simple_content(self):
        """Should chunk content into segments."""
        config = self._create_mock_config()
        chunker = ChapterChunker(config)

        content = "Line 1\n" * 25  # 25 lines
        chunks = chunker.chunk_content(content, chapter_num=1, file_path="ch1.tex")

        # With chunk_size=10 and 25 lines, expect ~3 chunks
        assert len(chunks) >= 2
        assert all(c.chapter_num == 1 for c in chunks)

    def test_exclude_pythonbox(self):
        """Should exclude pythonbox environments."""
        config = self._create_mock_config()
        chunker = ChapterChunker(config)

        content = """
        This is regular text that should be included.
        \\begin{pythonbox}
        def example():
            return 42
        \\end{pythonbox}
        More regular text here.
        """

        chunks = chunker.chunk_content(content, chapter_num=1, file_path="ch1.tex")

        # Check that pythonbox content is not in chunks
        for chunk in chunks:
            assert "def example" not in chunk.content
            assert "return 42" not in chunk.content

    def test_exclude_equation(self):
        """Should exclude equation environments."""
        config = self._create_mock_config()
        chunker = ChapterChunker(config)

        content = """
        Regular explanatory text here.
        \\begin{equation}
        E = mc^2
        \\end{equation}
        More explanation.
        """

        chunks = chunker.chunk_content(content, chapter_num=1, file_path="ch1.tex")

        for chunk in chunks:
            assert "E = mc^2" not in chunk.content

    def test_extract_chapter_number(self):
        """Should extract chapter number from filename."""
        config = self._create_mock_config()
        chunker = ChapterChunker(config)

        test_cases = [
            ("chapter1.tex", 1),
            ("chapter12.tex", 12),
            ("Chapter5.tex", 5),
            ("ch_chapter3_intro.tex", 3),
        ]

        for filename, expected in test_cases:
            path = Path(filename)
            num = chunker._extract_chapter_num(path)
            assert num == expected, f"Failed for {filename}"

    def test_skip_small_chunks(self):
        """Should skip chunks with too few words."""
        config = self._create_mock_config()
        config.min_chunk_words = 10
        chunker = ChapterChunker(config)

        content = "One two three.\n" * 5  # Only 15 words total

        chunks = chunker.chunk_content(content, chapter_num=1, file_path="ch1.tex")

        # Chunks with < 10 words should be skipped
        for chunk in chunks:
            word_count = len(chunk.content.split())
            assert word_count >= 10 or len(chunks) == 0

    def test_clean_latex_commands(self):
        """Should clean LaTeX commands from content."""
        config = self._create_mock_config()
        chunker = ChapterChunker(config)

        content = """
        \\section{Introduction}
        \\label{sec:intro}
        This is \\textbf{important} content.
        See \\ref{fig:example} for details.
        """

        chunks = chunker.chunk_content(content, chapter_num=1, file_path="ch1.tex")

        if chunks:
            # Labels and refs should be removed
            assert "\\label" not in chunks[0].content
            assert "\\ref" not in chunks[0].content
            # But text content should remain
            assert "Introduction" in chunks[0].content or "important" in chunks[0].content

    def test_chunk_file_nonexistent(self):
        """Should return empty list for nonexistent file."""
        config = self._create_mock_config()
        chunker = ChapterChunker(config)

        chunks = chunker.chunk_file(Path("/nonexistent/chapter1.tex"))
        assert chunks == []

    def test_chunk_properties(self):
        """Should set correct chunk properties."""
        config = self._create_mock_config()
        config.chunk_size = 5
        chunker = ChapterChunker(config)

        content = "Word one two three four five.\n" * 20

        chunks = chunker.chunk_content(content, chapter_num=3, file_path="ch3.tex")

        if chunks:
            chunk = chunks[0]
            assert chunk.chapter_num == 3
            assert chunk.chunk_index == 0
            assert chunk.file_path == "ch3.tex"
            assert chunk.start_line >= 1
            assert chunk.chapter_label == "chapter3"
