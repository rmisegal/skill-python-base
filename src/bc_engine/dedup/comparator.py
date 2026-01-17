"""
Chapter comparator with parallel processing.

Compares chunks between chapters for semantic duplication
using configurable LLM integration.
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from .config import DedupConfig
from .models import ChapterChunk, ComparisonResult


@dataclass
class ComparisonTask:
    """A single comparison task between two chunks."""

    source: ChapterChunk
    target: ChapterChunk


class ChapterComparator:
    """
    Compares chapter chunks for semantic duplication.

    Uses parallel processing for efficient comparison and
    delegates semantic analysis to LLM via callback.
    """

    def __init__(
        self,
        config: Optional[DedupConfig] = None,
        llm_callback: Optional[Callable[[str], str]] = None,
    ) -> None:
        """
        Initialize comparator.

        Args:
            config: Dedup configuration
            llm_callback: Function to call LLM with prompt, returns response
        """
        self._config = config or DedupConfig()
        self._llm_callback = llm_callback
        self._threshold = self._config.similarity_threshold

    def _build_prompt(self, source: ChapterChunk, target: ChapterChunk) -> str:
        """Build LLM prompt for semantic comparison."""
        template = self._config.llm_prompt_template
        return template.format(
            source_chapter=source.chapter_num,
            source_text=source.content[:500],
            target_chapter=target.chapter_num,
            target_text=target.content[:500],
        )

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM JSON response."""
        try:
            # Extract JSON from response
            match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"is_duplicate": False, "similarity_score": 0.0, "duplicate_segments": []}

    def _compare_single(self, task: ComparisonTask) -> ComparisonResult:
        """Compare a single source-target pair."""
        if self._llm_callback is None:
            # Fallback: simple word overlap comparison
            return self._simple_compare(task.source, task.target)

        prompt = self._build_prompt(task.source, task.target)
        response = self._llm_callback(prompt)
        parsed = self._parse_llm_response(response)

        return ComparisonResult(
            source_chunk=task.source,
            target_chunk=task.target,
            is_duplicate=parsed.get("is_duplicate", False),
            similarity_score=parsed.get("similarity_score", 0.0),
            duplicate_segments=parsed.get("duplicate_segments", []),
        )

    def _simple_compare(
        self,
        source: ChapterChunk,
        target: ChapterChunk,
    ) -> ComparisonResult:
        """Simple word-overlap comparison (no LLM)."""
        source_words = set(source.content.lower().split())
        target_words = set(target.content.lower().split())

        if not source_words or not target_words:
            return ComparisonResult(source, target, False, 0.0, [])

        intersection = source_words & target_words
        union = source_words | target_words
        jaccard = len(intersection) / len(union) if union else 0.0

        is_dup = jaccard >= self._threshold
        segments = list(intersection)[:5] if is_dup else []

        return ComparisonResult(source, target, is_dup, jaccard, segments)

    def compare_chapters(
        self,
        source_chunks: List[ChapterChunk],
        target_chunks: List[ChapterChunk],
    ) -> List[ComparisonResult]:
        """
        Compare all target chunks against source chunks.

        Uses parallel processing for efficiency.

        Args:
            source_chunks: Chunks from earlier chapters
            target_chunks: Chunks from later chapter to check

        Returns:
            List of ComparisonResults with duplicates found
        """
        tasks = [
            ComparisonTask(source=src, target=tgt)
            for src in source_chunks
            for tgt in target_chunks
        ]

        results: List[ComparisonResult] = []
        max_workers = self._config.max_workers

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._compare_single, task): task
                for task in tasks
            }

            for future in as_completed(futures):
                result = future.result()
                if result.is_duplicate:
                    results.append(result)

        return results

    def compare_backward(
        self,
        chapters: Dict[int, List[ChapterChunk]],
    ) -> List[ComparisonResult]:
        """
        Perform backward scan comparison.

        Starts from last chapter and compares against all previous.

        Args:
            chapters: Dict mapping chapter_num to list of chunks

        Returns:
            All duplicates found via backward scan
        """
        sorted_nums = sorted(chapters.keys(), reverse=True)
        all_results: List[ComparisonResult] = []

        for i, target_num in enumerate(sorted_nums[:-1]):
            target_chunks = chapters[target_num]

            # Compare against all earlier chapters
            for source_num in sorted_nums[i + 1:]:
                source_chunks = chapters[source_num]
                results = self.compare_chapters(source_chunks, target_chunks)
                all_results.extend(results)

        return all_results
