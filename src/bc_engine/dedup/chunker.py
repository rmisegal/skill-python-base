"""
Text chunker for chapter content.

Splits LaTeX chapter files into chunks for comparison,
excluding code blocks and other non-prose environments.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Optional

from .config import DedupConfig
from .models import ChapterChunk


class ChapterChunker:
    """
    Splits chapter content into comparable chunks.

    Excludes specified LaTeX environments and respects
    paragraph boundaries for meaningful comparison.
    """

    def __init__(self, config: Optional[DedupConfig] = None) -> None:
        """Initialize chunker with configuration."""
        self._config = config or DedupConfig()
        self._excluded_pattern = self._build_exclusion_pattern()

    def _build_exclusion_pattern(self) -> re.Pattern:
        """Build regex pattern for excluded environments."""
        envs = self._config.excluded_environments
        if not envs:
            return re.compile(r"(?!)")  # Never matches

        env_names = "|".join(re.escape(env) for env in envs)
        pattern = rf"\\begin\{{({env_names})\}}.*?\\end\{{\1\}}"
        return re.compile(pattern, re.DOTALL)

    def _extract_chapter_num(self, file_path: Path) -> int:
        """Extract chapter number from filename."""
        match = re.search(r"chapter(\d+)", file_path.stem, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _strip_excluded_environments(self, content: str) -> str:
        """Remove excluded environments from content."""
        return self._excluded_pattern.sub("", content)

    def _clean_content(self, content: str) -> str:
        """Clean content for comparison - remove LaTeX commands."""
        # Remove comments
        content = re.sub(r"%.*$", "", content, flags=re.MULTILINE)
        # Remove common LaTeX commands but keep text
        content = re.sub(r"\\(section|subsection|chapter)\*?\{([^}]*)\}", r"\2", content)
        content = re.sub(r"\\(textbf|textit|emph)\{([^}]*)\}", r"\2", content)
        content = re.sub(r"\\label\{[^}]*\}", "", content)
        content = re.sub(r"\\ref\{[^}]*\}", "", content)
        # Normalize whitespace
        content = re.sub(r"\s+", " ", content)
        return content.strip()

    def chunk_file(self, file_path: Path) -> List[ChapterChunk]:
        """
        Split a chapter file into chunks.

        Args:
            file_path: Path to the chapter .tex file

        Returns:
            List of ChapterChunk objects
        """
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding="utf-8")
        chapter_num = self._extract_chapter_num(file_path)

        return self.chunk_content(
            content=content,
            chapter_num=chapter_num,
            file_path=str(file_path),
        )

    def chunk_content(
        self,
        content: str,
        chapter_num: int,
        file_path: str,
    ) -> List[ChapterChunk]:
        """
        Split content string into chunks.

        Args:
            content: Raw LaTeX content
            chapter_num: Chapter number for labeling
            file_path: Source file path

        Returns:
            List of ChapterChunk objects
        """
        # Strip excluded environments
        stripped = self._strip_excluded_environments(content)
        lines = stripped.split("\n")

        chunks: List[ChapterChunk] = []
        chunk_size = self._config.chunk_size
        min_words = self._config.min_chunk_words

        chunk_index = 0
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i : i + chunk_size]
            chunk_content = "\n".join(chunk_lines)
            cleaned = self._clean_content(chunk_content)

            # Skip chunks with too few words
            word_count = len(cleaned.split())
            if word_count < min_words:
                continue

            chunks.append(
                ChapterChunk(
                    chapter_num=chapter_num,
                    chunk_index=chunk_index,
                    content=cleaned,
                    start_line=i + 1,
                    end_line=i + len(chunk_lines),
                    file_path=file_path,
                )
            )
            chunk_index += 1

        return chunks

    def iter_chunks(self, file_path: Path) -> Iterator[ChapterChunk]:
        """Iterate over chunks from a file."""
        yield from self.chunk_file(file_path)
