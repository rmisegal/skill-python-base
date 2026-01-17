r"""
BC Dedup - Chapter Deduplication & Balancing Engine.

Provides automated content deduplication using backward scan algorithm
with \chapterref{} references for zero redundancy.
"""

from .models import DedupIssue, ChapterChunk, ComparisonResult
from .orchestrator import DedupOrchestrator

__all__ = [
    "DedupIssue",
    "ChapterChunk",
    "ComparisonResult",
    "DedupOrchestrator",
]
