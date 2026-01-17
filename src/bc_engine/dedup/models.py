"""
Domain models for chapter deduplication.

Defines data structures for chunks, issues, and comparison results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DedupSeverity(Enum):
    """Severity levels for deduplication issues."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class ChapterChunk:
    """
    Represents a chunk of chapter content for comparison.

    Attributes:
        chapter_num: Chapter number (1-indexed)
        chunk_index: Index within chapter
        content: Text content of the chunk
        start_line: Starting line in original file
        end_line: Ending line in original file
        file_path: Path to source file
    """

    chapter_num: int
    chunk_index: int
    content: str
    start_line: int
    end_line: int
    file_path: str

    @property
    def chapter_label(self) -> str:
        """Return chapter label for references."""
        return f"chapter{self.chapter_num}"

    @property
    def line_count(self) -> int:
        """Number of lines in chunk."""
        return self.end_line - self.start_line


@dataclass
class ComparisonResult:
    """
    Result of comparing two chapter chunks for semantic similarity.

    Attributes:
        source_chunk: The source (earlier) chunk
        target_chunk: The target (later) chunk being checked
        is_duplicate: Whether semantic duplication was found
        similarity_score: Confidence score (0.0 - 1.0)
        duplicate_segments: Specific duplicated text segments
    """

    source_chunk: ChapterChunk
    target_chunk: ChapterChunk
    is_duplicate: bool
    similarity_score: float = 0.0
    duplicate_segments: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_chapter": self.source_chunk.chapter_num,
            "target_chapter": self.target_chunk.chapter_num,
            "is_duplicate": self.is_duplicate,
            "similarity_score": self.similarity_score,
            "duplicate_count": len(self.duplicate_segments),
        }


@dataclass
class DedupIssue:
    """
    Represents a deduplication issue found in content.

    Attributes:
        rule: Detection rule that triggered this issue
        file: Path to the file containing the issue
        line: Line number where issue was found
        content: The duplicated content
        severity: Issue severity level
        fix: Suggested fix with chapterref
        source_chapter: Chapter containing original content
        target_chapter: Chapter with duplicate to be replaced
        context: Additional context data
    """

    rule: str
    file: str
    line: int
    content: str
    severity: DedupSeverity
    source_chapter: int
    target_chapter: int
    fix: Optional[str] = None
    context: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary for JSON serialization."""
        return {
            "rule": self.rule,
            "file": self.file,
            "line": self.line,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "severity": self.severity.value,
            "source_chapter": self.source_chapter,
            "target_chapter": self.target_chapter,
            "fix": self.fix,
            "context": self.context,
        }

    @classmethod
    def from_comparison(
        cls,
        result: ComparisonResult,
        rule: str = "dedup-semantic-duplicate",
    ) -> DedupIssue:
        """Create DedupIssue from ComparisonResult."""
        fix = f"\\chapterref{{chapter{result.source_chunk.chapter_num}}}"
        return cls(
            rule=rule,
            file=result.target_chunk.file_path,
            line=result.target_chunk.start_line,
            content=result.duplicate_segments[0] if result.duplicate_segments else "",
            severity=DedupSeverity.WARNING,
            source_chapter=result.source_chunk.chapter_num,
            target_chapter=result.target_chunk.chapter_num,
            fix=fix,
            context={
                "similarity_score": result.similarity_score,
                "segment_count": len(result.duplicate_segments),
            },
        )
