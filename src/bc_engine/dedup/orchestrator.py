"""
Dedup Orchestrator - Main coordinator for chapter deduplication.

Orchestrates the backward scan algorithm with parallel processing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .chunker import ChapterChunker
from .comparator import ChapterComparator
from .config import DedupConfig
from .models import ChapterChunk, ComparisonResult, DedupIssue
from .rewriter import ChapterRefRewriter


@dataclass
class DedupResult:
    """Result from deduplication run."""

    issues: List[DedupIssue] = field(default_factory=list)
    chapters_scanned: int = 0
    duplicates_found: int = 0
    fixes_applied: int = 0
    balance_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "chapters_scanned": self.chapters_scanned,
            "duplicates_found": self.duplicates_found,
            "fixes_applied": self.fixes_applied,
            "issues": [i.to_dict() for i in self.issues],
            "balance_warnings": self.balance_warnings,
        }


class DedupOrchestrator:
    """
    Main orchestrator for chapter deduplication.

    Coordinates chunking, comparison, and rewriting using
    the backward scan algorithm.
    """

    def __init__(
        self,
        project_path: str | Path,
        config_path: Optional[str | Path] = None,
        llm_callback: Optional[Callable[[str], str]] = None,
    ) -> None:
        """
        Initialize orchestrator.

        Args:
            project_path: Root path of the book project
            config_path: Path to bc_dedup.json config
            llm_callback: Function for LLM calls
        """
        self._project_path = Path(project_path)
        self._config = DedupConfig()

        if config_path:
            self._config.load(config_path)

        self._chunker = ChapterChunker(self._config)
        self._comparator = ChapterComparator(self._config, llm_callback)
        self._rewriter = ChapterRefRewriter(self._config, llm_callback)

    def _discover_chapters(self) -> Dict[int, Path]:
        """Discover chapter files in project."""
        pattern = self._config.chapter_pattern
        chapters: Dict[int, Path] = {}

        for path in self._project_path.glob(pattern):
            # Extract chapter number from filename
            import re
            match = re.search(r"chapter(\d+)", path.stem, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                chapters[num] = path

        return dict(sorted(chapters.items()))

    def _load_all_chunks(
        self,
        chapter_paths: Dict[int, Path],
    ) -> Dict[int, List[ChapterChunk]]:
        """Load and chunk all chapters."""
        chunks: Dict[int, List[ChapterChunk]] = {}

        for num, path in chapter_paths.items():
            chapter_chunks = self._chunker.chunk_file(path)
            if chapter_chunks:
                chunks[num] = chapter_chunks

        return chunks

    def _check_balance(
        self,
        chunks: Dict[int, List[ChapterChunk]],
    ) -> List[str]:
        """Check chapter balance and return warnings."""
        warnings: List[str] = []
        threshold = self._config.balance_threshold

        if not chunks:
            return warnings

        sizes = {num: len(ch) for num, ch in chunks.items()}
        avg_size = sum(sizes.values()) / len(sizes)

        for num, size in sizes.items():
            if avg_size > 0 and size > avg_size * threshold:
                ratio = size / avg_size
                warnings.append(
                    f"Chapter {num} is {ratio:.1f}x larger than average"
                )

        return warnings

    def detect(self) -> DedupResult:
        """
        Detect duplicates using backward scan algorithm.

        Returns:
            DedupResult with all issues found
        """
        result = DedupResult()

        # Discover and load chapters
        chapter_paths = self._discover_chapters()
        if len(chapter_paths) < 2:
            return result

        chunks = self._load_all_chunks(chapter_paths)
        result.chapters_scanned = len(chunks)

        # Check balance
        result.balance_warnings = self._check_balance(chunks)

        # Perform backward comparison
        comparisons = self._comparator.compare_backward(chunks)
        result.duplicates_found = len(comparisons)

        # Convert to issues
        for comp in comparisons:
            issue = DedupIssue.from_comparison(comp)
            issue.fix = self._rewriter.generate_fix(comp)
            result.issues.append(issue)

        return result

    def fix(self, issues: List[DedupIssue]) -> int:
        """
        Apply fixes to chapter files.

        Args:
            issues: List of DedupIssues to fix

        Returns:
            Number of fixes applied
        """
        # Group issues by file
        by_file: Dict[str, List[DedupIssue]] = {}
        for issue in issues:
            if issue.file not in by_file:
                by_file[issue.file] = []
            by_file[issue.file].append(issue)

        fixes_applied = 0

        for file_path, file_issues in by_file.items():
            path = Path(file_path)
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8")
            fixed = self._rewriter.apply_fixes(content, file_issues)

            if fixed != content:
                path.write_text(fixed, encoding="utf-8")
                fixes_applied += len(file_issues)

        return fixes_applied

    def run(self, apply_fixes: bool = False) -> DedupResult:
        """
        Run full deduplication pipeline.

        Args:
            apply_fixes: Whether to apply fixes to files

        Returns:
            DedupResult with all findings
        """
        result = self.detect()

        if apply_fixes and result.issues:
            result.fixes_applied = self.fix(result.issues)

        return result
