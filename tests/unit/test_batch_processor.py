"""
Tests for Batch Processor.

Tests for smart chunking and parallel processing.
"""

import pytest
from pathlib import Path

from qa_engine.infrastructure.processing import BatchProcessor, Chunk, ChunkResult
from qa_engine.domain.models.issue import Issue, Severity


class TestBatchProcessor:
    """Tests for BatchProcessor."""

    def setup_method(self):
        """Create processor instance."""
        self.processor = BatchProcessor(chunk_size=100, max_workers=2)

    def test_create_chunks_small_file(self):
        """Test small file creates single chunk."""
        content = "line1\nline2\nline3"
        chunks = self.processor.create_chunks(Path("test.tex"), content)
        assert len(chunks) == 1
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 3
        assert chunks[0].chunk_index == 0
        assert chunks[0].total_chunks == 1

    def test_create_chunks_large_file(self):
        """Test large file creates multiple chunks."""
        # Create 250 lines
        content = "\n".join(f"line{i}" for i in range(250))
        chunks = self.processor.create_chunks(Path("test.tex"), content)
        assert len(chunks) == 3  # 100 + 100 + 50
        assert chunks[0].start_line == 1
        assert chunks[1].start_line == 101
        assert chunks[2].start_line == 201

    def test_chunk_overlap(self):
        """Test chunks have overlap for cross-line issues."""
        content = "\n".join(f"line{i}" for i in range(200))
        processor = BatchProcessor(chunk_size=100, max_workers=2)
        chunks = processor.create_chunks(Path("test.tex"), content)
        # First chunk should include overlap
        assert chunks[0].end_line > 100

    def test_process_sequential(self):
        """Test sequential chunk processing."""
        content = "\n".join(f"line{i}" for i in range(50))
        chunks = self.processor.create_chunks(Path("test.tex"), content)

        def mock_processor(content, file_path, offset):
            return [Issue(
                rule="test",
                file=file_path,
                line=1 + offset,
                content="test",
                severity=Severity.INFO,
                fix="",
            )]

        results = self.processor.process_chunks(chunks, mock_processor, parallel=False)
        assert len(results) == 1
        assert len(results[0].issues) == 1

    def test_process_parallel(self):
        """Test parallel chunk processing."""
        content = "\n".join(f"line{i}" for i in range(250))
        chunks = self.processor.create_chunks(Path("test.tex"), content)

        def mock_processor(content, file_path, offset):
            return [Issue(
                rule="test",
                file=file_path,
                line=1 + offset,
                content="test",
                severity=Severity.INFO,
                fix="",
            )]

        results = self.processor.process_chunks(chunks, mock_processor, parallel=True)
        assert len(results) == 3
        # Results should be sorted by chunk index
        assert results[0].chunk.chunk_index == 0
        assert results[1].chunk.chunk_index == 1
        assert results[2].chunk.chunk_index == 2

    def test_merge_results_deduplicates(self):
        """Test result merging removes duplicates from overlap."""
        chunk1 = Chunk("test.tex", "content", 1, 110, 0, 2)
        chunk2 = Chunk("test.tex", "content", 101, 200, 1, 2)

        # Same issue appears in both chunks (overlap region)
        issue = Issue(
            rule="test",
            file="test.tex",
            line=105,
            content="duplicate",
            severity=Severity.WARNING,
            fix="",
        )

        results = [
            ChunkResult(chunk=chunk1, issues=[issue]),
            ChunkResult(chunk=chunk2, issues=[issue]),
        ]

        merged = self.processor.merge_results(results)
        assert len(merged) == 1  # Deduplicated

    def test_merge_results_sorted(self):
        """Test merged results are sorted by file and line."""
        chunk1 = Chunk("test.tex", "content", 1, 100, 0, 2)
        chunk2 = Chunk("test.tex", "content", 101, 200, 1, 2)

        issue1 = Issue("r", "test.tex", 150, "c", Severity.INFO, "")
        issue2 = Issue("r", "test.tex", 50, "c", Severity.INFO, "")

        results = [
            ChunkResult(chunk=chunk1, issues=[issue2]),
            ChunkResult(chunk=chunk2, issues=[issue1]),
        ]

        merged = self.processor.merge_results(results)
        assert merged[0].line == 50
        assert merged[1].line == 150

    def test_process_with_error(self):
        """Test error handling in chunk processing."""
        content = "test content"
        chunks = self.processor.create_chunks(Path("test.tex"), content)

        def failing_processor(content, file_path, offset):
            raise ValueError("Test error")

        results = self.processor.process_chunks(chunks, failing_processor)
        assert len(results) == 1
        assert results[0].error == "Test error"

    def test_merge_skips_errors(self):
        """Test merge skips chunks with errors."""
        chunk1 = Chunk("test.tex", "content", 1, 100, 0, 2)
        issue = Issue("r", "test.tex", 50, "c", Severity.INFO, "")

        results = [
            ChunkResult(chunk=chunk1, issues=[issue]),
            ChunkResult(chunk=chunk1, error="Failed"),
        ]

        merged = self.processor.merge_results(results)
        assert len(merged) == 1

    def test_chunk_line_count(self):
        """Test chunk line count property."""
        chunk = Chunk("test.tex", "content", 10, 50, 0, 1)
        assert chunk.line_count == 40
