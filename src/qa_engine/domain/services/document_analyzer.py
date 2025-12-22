"""
Document analyzer service.

Analyzes LaTeX documents to determine size and processing strategy.
Implements FR-101 from PRD.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List


class ProcessingStrategy(Enum):
    """Document processing strategies based on size."""

    SINGLE_PASS = "single_pass"
    FILE_BY_FILE = "file_by_file"
    CHUNKED = "chunked"
    PARALLEL_CHUNKED = "parallel_chunked"


@dataclass
class DocumentMetrics:
    """
    Document analysis metrics.

    Attributes:
        total_lines: Total lines across all files
        total_files: Number of .tex files
        estimated_tokens: Estimated token count
        recommended_strategy: Suggested processing strategy
        largest_file: Path to largest file
        largest_file_lines: Line count of largest file
    """

    total_lines: int
    total_files: int
    estimated_tokens: int
    recommended_strategy: ProcessingStrategy
    largest_file: str
    largest_file_lines: int


class DocumentAnalyzer:
    """
    Service for analyzing LaTeX document projects.

    Determines document size and recommends processing strategy
    as per FR-101 acceptance criteria.
    """

    TOKENS_PER_LINE_ESTIMATE = 10
    SINGLE_PASS_THRESHOLD = 2000
    FILE_BY_FILE_THRESHOLD = 10000
    CHUNKED_THRESHOLD = 30000

    def analyze(self, project_path: str | Path) -> DocumentMetrics:
        """
        Analyze a LaTeX project.

        Args:
            project_path: Path to project directory

        Returns:
            DocumentMetrics with analysis results
        """
        path = Path(project_path)
        tex_files = self._find_tex_files(path)

        total_lines = 0
        largest_file = ""
        largest_lines = 0

        for tex_file in tex_files:
            lines = self._count_lines(tex_file)
            total_lines += lines
            if lines > largest_lines:
                largest_lines = lines
                largest_file = str(tex_file)

        estimated_tokens = total_lines * self.TOKENS_PER_LINE_ESTIMATE
        strategy = self._recommend_strategy(total_lines)

        return DocumentMetrics(
            total_lines=total_lines,
            total_files=len(tex_files),
            estimated_tokens=estimated_tokens,
            recommended_strategy=strategy,
            largest_file=largest_file,
            largest_file_lines=largest_lines,
        )

    def _find_tex_files(self, path: Path) -> List[Path]:
        """Find all .tex files in project."""
        if path.is_file():
            return [path] if path.suffix == ".tex" else []
        return list(path.rglob("*.tex"))

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except OSError:
            return 0

    def _recommend_strategy(self, total_lines: int) -> ProcessingStrategy:
        """Recommend processing strategy based on line count."""
        if total_lines <= self.SINGLE_PASS_THRESHOLD:
            return ProcessingStrategy.SINGLE_PASS
        elif total_lines <= self.FILE_BY_FILE_THRESHOLD:
            return ProcessingStrategy.FILE_BY_FILE
        elif total_lines <= self.CHUNKED_THRESHOLD:
            return ProcessingStrategy.CHUNKED
        else:
            return ProcessingStrategy.PARALLEL_CHUNKED
