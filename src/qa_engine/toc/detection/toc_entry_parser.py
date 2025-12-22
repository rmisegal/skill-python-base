"""
TOC file entry parser.

Parses LaTeX .toc files into structured entry objects.
All patterns loaded from JSON configuration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..config.config_loader import TOCConfigLoader


@dataclass
class TOCEntry:
    """Represents a single TOC entry."""

    entry_type: str  # chapter, section, subsection, subsubsection
    title: str
    page: str
    hyperref: str
    line_number: int
    raw_content: str
    number: Optional[str] = None
    parent_number: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def depth(self) -> int:
        """Get nesting depth (0=chapter, 1=section, etc.)."""
        depth_map = {"chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3}
        return depth_map.get(self.entry_type, 0)


class TOCEntryParser:
    """Parses .toc file content into structured entries."""

    def __init__(self) -> None:
        """Initialize parser with config."""
        self._config = TOCConfigLoader()
        self._build_patterns()

    def _build_patterns(self) -> None:
        """Build regex patterns from config."""
        raw = self._config.get_raw_pattern("toc_entry_patterns", "contentsline")
        self._entry_pattern = re.compile(raw) if raw else None

        num_pattern = self._config.get_raw_pattern("numbering_patterns", "any_number")
        self._number_pattern = re.compile(num_pattern) if num_pattern else None

        lre = self._config.get_raw_pattern("ltr_wrapper_patterns", "lre")
        self._lre_pattern = re.compile(lre + r"([^}]+)\}") if lre else None

    def parse_file(self, toc_path: str) -> List[TOCEntry]:
        """Parse a .toc file and return entries."""
        path = Path(toc_path)
        if not path.exists():
            return []

        content = path.read_text(encoding="utf-8", errors="replace")
        return self.parse_content(content, toc_path)

    def parse_content(self, content: str, file_path: str = "") -> List[TOCEntry]:
        """Parse TOC content string into entries."""
        entries: List[TOCEntry] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            if not line.strip() or line.strip().startswith("%"):
                continue

            entry = self._parse_line(line, line_num, file_path)
            if entry:
                entries.append(entry)

        self._assign_parent_numbers(entries)
        return entries

    def _parse_line(self, line: str, line_num: int, file_path: str) -> Optional[TOCEntry]:
        """Parse a single line into a TOCEntry."""
        if not self._entry_pattern:
            return None

        match = self._entry_pattern.search(line)
        if not match:
            return None

        entry_type = match.group(1)
        title_content = match.group(2)
        page = match.group(3)
        hyperref = match.group(4) if match.lastindex >= 4 else ""

        number = self._extract_number(title_content)

        return TOCEntry(
            entry_type=entry_type,
            title=title_content,
            page=page,
            hyperref=hyperref,
            line_number=line_num,
            raw_content=line,
            number=number,
            context={"file": file_path},
        )

    def _extract_number(self, title: str) -> Optional[str]:
        """Extract section number from title content."""
        if self._lre_pattern:
            match = self._lre_pattern.search(title)
            if match:
                return match.group(1)

        if self._number_pattern:
            match = self._number_pattern.search(title)
            if match:
                return match.group(1)

        return None

    def _assign_parent_numbers(self, entries: List[TOCEntry]) -> None:
        """Assign parent numbers to entries based on hierarchy."""
        current_parents = {}

        for entry in entries:
            depth = entry.depth
            if entry.number:
                current_parents[depth] = entry.number

            if depth > 0:
                parent_depth = depth - 1
                entry.parent_number = current_parents.get(parent_depth)

    def get_chapters(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter entries to chapters only."""
        return [e for e in entries if e.entry_type == "chapter"]

    def get_sections(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """Filter entries to sections only."""
        return [e for e in entries if e.entry_type == "section"]

    def get_by_type(self, entries: List[TOCEntry], entry_type: str) -> List[TOCEntry]:
        """Filter entries by type."""
        return [e for e in entries if e.entry_type == entry_type]
