"""
Structure helper functions for TOC detection.

Provides reusable methods for structure validation.
All patterns loaded from JSON configuration.

Version: 2.0.0 - Added duplicate title detection
"""

from __future__ import annotations

import re
from typing import List, Set, Optional, Dict, Tuple
from collections import defaultdict

from ..config.config_loader import TOCConfigLoader
from .toc_entry_parser import TOCEntry


class StructureHelpers:
    """Helper methods for structure detection."""

    def __init__(self, config: TOCConfigLoader) -> None:
        """Initialize with config."""
        self._config = config

    def get_chapter_numbers(self, entries: List[TOCEntry]) -> Set[int]:
        """Extract all chapter numbers as integers."""
        found: Set[int] = set()

        for entry in entries:
            if entry.entry_type == "chapter" and entry.number:
                try:
                    found.add(int(entry.number))
                except ValueError:
                    continue

        return found

    def has_bibliography(self, entries: List[TOCEntry]) -> bool:
        """Check if any entry is a bibliography."""
        bib_heb = self._config.get_raw_pattern("bibliography_patterns", "hebrew")
        bib_eng = self._config.get_raw_pattern("bibliography_patterns", "english")

        for entry in entries:
            if bib_heb and re.search(bib_heb, entry.title):
                return True
            if bib_eng and re.search(bib_eng, entry.title.lower()):
                return True

        return False

    def make_entry_key(self, entry: TOCEntry) -> str:
        """Create a unique key for an entry."""
        return f"{entry.entry_type}:{entry.number}:{entry.title[:30]}"

    def parse_page_number(self, page: str) -> Optional[int]:
        """Parse page number, handling roman numerals."""
        if not page:
            return None

        try:
            return int(page)
        except ValueError:
            return self._roman_to_int(page.lower())

    def _roman_to_int(self, roman: str) -> Optional[int]:
        """Convert roman numeral to integer."""
        values = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}

        if not all(c in values for c in roman):
            return None

        total = 0
        prev = 0

        for char in reversed(roman):
            val = values[char]
            if val < prev:
                total -= val
            else:
                total += val
            prev = val

        return total

    def is_empty_title(self, title: str) -> bool:
        """Check if title is effectively empty."""
        cleaned = re.sub(r"\\[a-zA-Z]+\{[^}]*\}", "", title)
        cleaned = re.sub(r"\\[a-zA-Z]+", "", cleaned)
        return not cleaned.strip()

    def get_section_depth(self, entry_type: str) -> int:
        """Get nesting depth for entry type."""
        depths = {"chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3}
        return depths.get(entry_type, 0)

    def is_appendix(self, entry: TOCEntry) -> bool:
        """Check if entry is an appendix."""
        return "נספח" in entry.title or "appendix" in entry.title.lower()

    def normalize_title(self, title: str) -> str:
        """
        Normalize title for duplicate comparison (v2.0).

        Removes:
        - LaTeX commands and wrappers
        - Numbers and section markers
        - Extra whitespace
        - Case differences
        """
        normalized = title

        # Remove LaTeX wrappers: \textenglish{...}, \texthebrew{...}, etc.
        normalized = re.sub(r'\\tex[a-z]+\{([^}]*)\}', r'\1', normalized)
        normalized = re.sub(r'\\[A-Za-z]+\{([^}]*)\}', r'\1', normalized)

        # Remove standalone LaTeX commands
        normalized = re.sub(r'\\[a-zA-Z]+', '', normalized)

        # Remove numberline content
        normalized = re.sub(r'\\numberline\s*\{[^}]*\}', '', normalized)

        # Remove leading/trailing numbers and dots
        normalized = re.sub(r'^[\d\.\s]+', '', normalized)
        normalized = re.sub(r'[\d\.\s]+$', '', normalized)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Lowercase for comparison
        normalized = normalized.lower()

        return normalized

    def make_title_key(self, entry: TOCEntry) -> str:
        """
        Create a key based on normalized title only (v2.0).

        Ignores section numbers - catches duplicate titles.
        """
        normalized = self.normalize_title(entry.title)
        return f"{entry.entry_type}:{normalized}"

    def find_duplicate_titles(
        self, entries: List[TOCEntry]
    ) -> Dict[str, List[TOCEntry]]:
        """
        Find entries with duplicate titles (v2.0).

        Groups entries by normalized title, returns only groups
        with more than one entry.
        """
        title_groups: Dict[str, List[TOCEntry]] = defaultdict(list)

        for entry in entries:
            # Skip very short titles (likely auto-generated)
            if len(entry.title.strip()) < 5:
                continue

            key = self.make_title_key(entry)
            title_groups[key].append(entry)

        # Return only duplicates
        return {
            key: group
            for key, group in title_groups.items()
            if len(group) > 1
        }

    def find_sequential_duplicates(
        self, entries: List[TOCEntry]
    ) -> List[Tuple[TOCEntry, TOCEntry]]:
        """
        Find adjacent entries with same or very similar titles (v2.0).

        These are more likely to be errors than non-adjacent duplicates.
        """
        duplicates = []

        for i in range(len(entries) - 1):
            current = entries[i]
            next_entry = entries[i + 1]

            # Same type and similar title
            if current.entry_type == next_entry.entry_type:
                current_norm = self.normalize_title(current.title)
                next_norm = self.normalize_title(next_entry.title)

                if current_norm == next_norm:
                    duplicates.append((current, next_entry))

        return duplicates

    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two titles (v2.0).

        Uses Jaccard similarity on word sets.
        Returns 0.0 to 1.0 (1.0 = identical).
        """
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)

        if norm1 == norm2:
            return 1.0

        words1 = set(norm1.split())
        words2 = set(norm2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def find_similar_titles(
        self, entries: List[TOCEntry], threshold: float = 0.8
    ) -> List[Tuple[TOCEntry, TOCEntry, float]]:
        """
        Find entries with very similar (but not identical) titles (v2.0).

        Returns tuples of (entry1, entry2, similarity_score).
        """
        similar = []
        n = len(entries)

        for i in range(n):
            for j in range(i + 1, n):
                # Only compare same type
                if entries[i].entry_type != entries[j].entry_type:
                    continue

                similarity = self.calculate_title_similarity(
                    entries[i].title, entries[j].title
                )

                # Similar but not identical
                if threshold <= similarity < 1.0:
                    similar.append((entries[i], entries[j], similarity))

        return similar

    def find_missing_section_gaps(
        self, entries: List[TOCEntry]
    ) -> List[Tuple[TOCEntry, TOCEntry]]:
        """
        Find sections that follow subsections without proper gap (v2.3).

        Returns tuples of (previous_entry, section_entry) where gap is missing.
        """
        missing_gaps = []
        depth_map = {"chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3}

        for i in range(1, len(entries)):
            prev = entries[i - 1]
            curr = entries[i]

            prev_depth = depth_map.get(prev.entry_type, 0)
            curr_depth = depth_map.get(curr.entry_type, 0)

            # Section following deeper entry (subsection/subsubsection)
            if curr.entry_type == "section" and prev_depth > curr_depth:
                # Check if raw_content has addvspace marker
                if not self._has_gap_marker(curr.raw_content):
                    missing_gaps.append((prev, curr))

        return missing_gaps

    def _has_gap_marker(self, raw_content: str) -> bool:
        """Check if TOC entry has vertical space marker."""
        import re
        gap_patterns = [
            r"\\addvspace",
            r"\\vspace",
            r"\\bigskip",
            r"\\medskip",
        ]
        for pattern in gap_patterns:
            if re.search(pattern, raw_content):
                return True
        return False

    def find_page_number_jumps(
        self, entries: List[TOCEntry], threshold: int = 10
    ) -> List[Tuple[TOCEntry, TOCEntry, int]]:
        """
        Find anomalous page jumps within subsection groups (v2.3).

        Returns tuples of (entry1, entry2, jump_size) for large jumps.
        """
        jumps = []

        for i in range(1, len(entries)):
            prev = entries[i - 1]
            curr = entries[i]

            # Only check within same parent section
            if not self._same_parent_section(prev, curr):
                continue

            prev_page = self.parse_page_number(prev.page)
            curr_page = self.parse_page_number(curr.page)

            if prev_page is None or curr_page is None:
                continue

            jump = abs(curr_page - prev_page)
            if jump >= threshold:
                jumps.append((prev, curr, jump))

        return jumps

    def _same_parent_section(self, entry1: TOCEntry, entry2: TOCEntry) -> bool:
        """Check if two entries belong to same parent section."""
        if not entry1.number or not entry2.number:
            return False

        # Extract parent (e.g., "2.1" from "2.1.3")
        parts1 = entry1.number.split(".")
        parts2 = entry2.number.split(".")

        if len(parts1) < 2 or len(parts2) < 2:
            return False

        # Compare chapter.section prefix
        return parts1[0] == parts2[0] and parts1[1] == parts2[1]
