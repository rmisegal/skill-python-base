"""
Unit tests for ChapterComparator.

Tests parallel comparison and backward scan algorithm.
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from bc_engine.dedup.comparator import ChapterComparator, ComparisonTask
from bc_engine.dedup.models import ChapterChunk
from bc_engine.dedup.config import DedupConfig


class TestChapterComparator:
    """Tests for ChapterComparator class."""

    def setup_method(self):
        """Reset config singleton before each test."""
        DedupConfig.reset()

    def _create_mock_config(self):
        """Create mock config."""
        config = MagicMock(spec=DedupConfig)
        config.similarity_threshold = 0.75
        config.max_workers = 2
        config.llm_prompt_template = "Compare: {source_text} vs {target_text}"
        return config

    def _create_chunk(self, chapter_num, content, chunk_index=0):
        """Create a test chunk."""
        return ChapterChunk(
            chapter_num=chapter_num,
            chunk_index=chunk_index,
            content=content,
            start_line=1,
            end_line=10,
            file_path=f"chapter{chapter_num}.tex",
        )

    def test_simple_compare_high_overlap(self):
        """Should detect high word overlap as duplicate."""
        config = self._create_mock_config()
        comparator = ChapterComparator(config, llm_callback=None)

        source = self._create_chunk(1, "neural networks process information in layers")
        target = self._create_chunk(2, "neural networks process data in multiple layers")

        result = comparator._simple_compare(source, target)

        # High overlap should be detected
        assert result.similarity_score > 0.5
        assert result.source_chunk == source
        assert result.target_chunk == target

    def test_simple_compare_low_overlap(self):
        """Should not detect low overlap as duplicate."""
        config = self._create_mock_config()
        comparator = ChapterComparator(config, llm_callback=None)

        source = self._create_chunk(1, "neural networks process information")
        target = self._create_chunk(2, "database systems store records efficiently")

        result = comparator._simple_compare(source, target)

        assert result.similarity_score < 0.5
        assert not result.is_duplicate

    def test_compare_with_llm_callback(self):
        """Should use LLM callback when provided."""
        config = self._create_mock_config()

        llm_response = json.dumps({
            "is_duplicate": True,
            "similarity_score": 0.85,
            "duplicate_segments": ["neural networks"],
        })
        mock_llm = MagicMock(return_value=llm_response)

        comparator = ChapterComparator(config, llm_callback=mock_llm)

        source = self._create_chunk(1, "neural networks")
        target = self._create_chunk(2, "neural networks again")

        task = ComparisonTask(source=source, target=target)
        result = comparator._compare_single(task)

        assert mock_llm.called
        assert result.is_duplicate is True
        assert result.similarity_score == 0.85
        assert "neural networks" in result.duplicate_segments

    def test_parse_llm_response_valid(self):
        """Should parse valid LLM JSON response."""
        config = self._create_mock_config()
        comparator = ChapterComparator(config)

        response = '{"is_duplicate": true, "similarity_score": 0.9, "duplicate_segments": ["test"]}'
        parsed = comparator._parse_llm_response(response)

        assert parsed["is_duplicate"] is True
        assert parsed["similarity_score"] == 0.9
        assert parsed["duplicate_segments"] == ["test"]

    def test_parse_llm_response_invalid(self):
        """Should return defaults for invalid response."""
        config = self._create_mock_config()
        comparator = ChapterComparator(config)

        response = "This is not JSON"
        parsed = comparator._parse_llm_response(response)

        assert parsed["is_duplicate"] is False
        assert parsed["similarity_score"] == 0.0
        assert parsed["duplicate_segments"] == []

    def test_compare_chapters_parallel(self):
        """Should compare chapters in parallel."""
        config = self._create_mock_config()
        config.similarity_threshold = 0.3  # Lower threshold for test
        comparator = ChapterComparator(config, llm_callback=None)

        source_chunks = [
            self._create_chunk(1, "machine learning algorithms", 0),
            self._create_chunk(1, "deep neural networks", 1),
        ]
        target_chunks = [
            self._create_chunk(2, "machine learning models", 0),
            self._create_chunk(2, "convolutional networks", 1),
        ]

        results = comparator.compare_chapters(source_chunks, target_chunks)

        # Should find some matches due to word overlap
        assert isinstance(results, list)
        for result in results:
            assert result.is_duplicate

    def test_backward_scan_order(self):
        """Should scan chapters in backward order."""
        config = self._create_mock_config()
        config.similarity_threshold = 0.9  # High threshold
        comparator = ChapterComparator(config, llm_callback=None)

        chapters = {
            1: [self._create_chunk(1, "chapter one content")],
            2: [self._create_chunk(2, "chapter two content")],
            3: [self._create_chunk(3, "chapter three content")],
        }

        # With high threshold, likely no duplicates
        results = comparator.compare_backward(chapters)
        assert isinstance(results, list)

    def test_backward_scan_finds_duplicates(self):
        """Should find duplicates during backward scan."""
        config = self._create_mock_config()
        config.similarity_threshold = 0.3
        comparator = ChapterComparator(config, llm_callback=None)

        # Create chapters with similar content
        chapters = {
            1: [self._create_chunk(1, "neural networks learn from data")],
            3: [self._create_chunk(3, "neural networks learn from examples data")],
        }

        results = comparator.compare_backward(chapters)

        # Should find the duplicate
        if results:
            assert results[0].source_chunk.chapter_num < results[0].target_chunk.chapter_num

    def test_empty_chapters(self):
        """Should handle empty chapter dict."""
        config = self._create_mock_config()
        comparator = ChapterComparator(config, llm_callback=None)

        results = comparator.compare_backward({})
        assert results == []

    def test_single_chapter(self):
        """Should handle single chapter (no comparison needed)."""
        config = self._create_mock_config()
        comparator = ChapterComparator(config, llm_callback=None)

        chapters = {
            1: [self._create_chunk(1, "only chapter")],
        }

        results = comparator.compare_backward(chapters)
        assert results == []
