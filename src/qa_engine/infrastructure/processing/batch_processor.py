"""
Batch processor for smart chunking of large documents.

Implements FR-102 from PRD - handles chunked processing strategy.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, List

from ...domain.models.issue import Issue
from .chunk import Chunk, ChunkResult


class BatchProcessor:
    """
    Processes documents using smart chunking strategies.

    Splits large files into chunks and processes them in parallel
    based on the recommended strategy from DocumentAnalyzer.
    """

    DEFAULT_CHUNK_SIZE = 500  # lines per chunk
    OVERLAP_LINES = 10  # overlap to avoid missing cross-line issues

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        max_workers: int = 4,
    ) -> None:
        self._chunk_size = chunk_size
        self._max_workers = max_workers

    def create_chunks(self, file_path: Path, content: str) -> List[Chunk]:
        """Split file content into chunks."""
        lines = content.split("\n")
        total_lines = len(lines)

        if total_lines <= self._chunk_size:
            return [Chunk(
                file_path=str(file_path),
                content=content,
                start_line=1,
                end_line=total_lines,
                chunk_index=0,
                total_chunks=1,
            )]

        chunks: List[Chunk] = []
        start = 0
        chunk_idx = 0
        total_chunks = (total_lines + self._chunk_size - 1) // self._chunk_size

        while start < total_lines:
            end = min(start + self._chunk_size + self.OVERLAP_LINES, total_lines)
            chunk_lines = lines[start:end]

            chunks.append(Chunk(
                file_path=str(file_path),
                content="\n".join(chunk_lines),
                start_line=start + 1,
                end_line=end,
                chunk_index=chunk_idx,
                total_chunks=total_chunks,
            ))

            start += self._chunk_size
            chunk_idx += 1

        return chunks

    def process_chunks(
        self,
        chunks: List[Chunk],
        processor: Callable[[str, str, int], List[Issue]],
        parallel: bool = True,
    ) -> List[ChunkResult]:
        """Process chunks using provided processor function."""
        if parallel and len(chunks) > 1:
            return self._process_parallel(chunks, processor)
        return self._process_sequential(chunks, processor)

    def _process_parallel(
        self,
        chunks: List[Chunk],
        processor: Callable[[str, str, int], List[Issue]],
    ) -> List[ChunkResult]:
        """Process chunks in parallel."""
        results: List[ChunkResult] = []

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {
                executor.submit(self._process_single, chunk, processor): chunk
                for chunk in chunks
            }

            for future in as_completed(futures):
                results.append(future.result())

        return sorted(results, key=lambda r: r.chunk.chunk_index)

    def _process_sequential(
        self,
        chunks: List[Chunk],
        processor: Callable[[str, str, int], List[Issue]],
    ) -> List[ChunkResult]:
        """Process chunks sequentially."""
        return [self._process_single(chunk, processor) for chunk in chunks]

    def _process_single(
        self,
        chunk: Chunk,
        processor: Callable[[str, str, int], List[Issue]],
    ) -> ChunkResult:
        """Process a single chunk."""
        try:
            offset = chunk.start_line - 1
            issues = processor(chunk.content, chunk.file_path, offset)
            return ChunkResult(chunk=chunk, issues=issues)
        except Exception as e:
            return ChunkResult(chunk=chunk, error=str(e))

    def merge_results(self, results: List[ChunkResult]) -> List[Issue]:
        """Merge results from multiple chunks, deduplicating overlap."""
        all_issues: List[Issue] = []
        seen: set = set()

        for result in results:
            if result.error:
                continue
            for issue in result.issues:
                key = (issue.file, issue.line, issue.rule, issue.content)
                if key not in seen:
                    seen.add(key)
                    all_issues.append(issue)

        return sorted(all_issues, key=lambda i: (i.file, i.line))
