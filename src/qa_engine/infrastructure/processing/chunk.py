"""
Chunk model for batch processing.

Represents a chunk of content for parallel processing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ...domain.models.issue import Issue


@dataclass
class Chunk:
    """Represents a chunk of content for processing."""

    file_path: str
    content: str
    start_line: int
    end_line: int
    chunk_index: int
    total_chunks: int

    @property
    def line_count(self) -> int:
        """Number of lines in chunk."""
        return self.end_line - self.start_line


@dataclass
class ChunkResult:
    """Result from processing a single chunk."""

    chunk: Chunk
    issues: List[Issue] = field(default_factory=list)
    error: Optional[str] = None
