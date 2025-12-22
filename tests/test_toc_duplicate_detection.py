"""
Tests for TOC duplicate title detection (v2.2.0).
"""

import pytest
from src.qa_engine.toc.detection.structure_helpers import StructureHelpers
from src.qa_engine.toc.config.config_loader import TOCConfigLoader
from src.qa_engine.toc.detection.toc_entry_parser import TOCEntry


@pytest.fixture
def helpers():
    """Create structure helpers instance."""
    config = TOCConfigLoader()
    return StructureHelpers(config)


def create_entry(entry_type: str, title: str, number: str, line: int) -> TOCEntry:
    """Create a TOC entry for testing."""
    return TOCEntry(
        entry_type=entry_type,
        title=title,
        page="1",
        hyperref=f"{entry_type}.{line}",
        line_number=line,
        raw_content=f"\\contentsline {{{entry_type}}}{{\\numberline {{{number}}}{title}}}{{1}}",
        number=number,
    )


class TestNormalizeTitle:
    """Test title normalization."""

    def test_normalize_removes_latex_wrappers(self, helpers):
        title = r"\textenglish{English References}"
        normalized = helpers.normalize_title(title)
        assert normalized == "english references"

    def test_normalize_removes_numberline(self, helpers):
        title = r"\numberline{11.19}English References"
        normalized = helpers.normalize_title(title)
        assert normalized == "english references"

    def test_normalize_handles_hebrew(self, helpers):
        title = r"\texthebrew{מקורות}"
        normalized = helpers.normalize_title(title)
        assert "מקורות" in normalized


class TestFindDuplicateTitles:
    """Test duplicate title detection."""

    def test_finds_duplicate_titles(self, helpers):
        entries = [
            create_entry("section", "English References", "11.19", 100),
            create_entry("section", "Hebrew Sources", "11.20", 101),
            create_entry("section", "English References", "11.21", 102),
        ]
        duplicates = helpers.find_duplicate_titles(entries)
        assert len(duplicates) == 1
        key = list(duplicates.keys())[0]
        assert len(duplicates[key]) == 2

    def test_no_duplicates_when_titles_differ(self, helpers):
        entries = [
            create_entry("section", "First Title", "1.1", 10),
            create_entry("section", "Second Title", "1.2", 11),
            create_entry("section", "Third Title", "1.3", 12),
        ]
        duplicates = helpers.find_duplicate_titles(entries)
        assert len(duplicates) == 0


class TestFindSequentialDuplicates:
    """Test sequential duplicate detection."""

    def test_finds_adjacent_duplicates(self, helpers):
        entries = [
            create_entry("section", "English References", "11.19", 100),
            create_entry("section", "English References", "11.20", 101),
        ]
        sequential = helpers.find_sequential_duplicates(entries)
        assert len(sequential) == 1
        assert sequential[0][0].line_number == 100
        assert sequential[0][1].line_number == 101

    def test_non_adjacent_not_sequential(self, helpers):
        entries = [
            create_entry("section", "English References", "11.19", 100),
            create_entry("section", "Hebrew Sources", "11.20", 101),
            create_entry("section", "English References", "11.21", 102),
        ]
        sequential = helpers.find_sequential_duplicates(entries)
        assert len(sequential) == 0


class TestTitleSimilarity:
    """Test title similarity calculation."""

    def test_identical_titles_score_one(self, helpers):
        similarity = helpers.calculate_title_similarity(
            "English References", "English References"
        )
        assert similarity == 1.0

    def test_different_titles_score_low(self, helpers):
        similarity = helpers.calculate_title_similarity(
            "English References", "Hebrew Sources"
        )
        assert similarity < 0.5

    def test_similar_titles_score_high(self, helpers):
        similarity = helpers.calculate_title_similarity(
            "English References Guide", "English References Manual"
        )
        assert similarity >= 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
