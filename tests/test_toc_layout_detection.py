"""
Tests for TOC layout and gap detection (v2.3.0).
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


def create_entry(
    entry_type: str, number: str, page: str, line: int, raw: str = ""
) -> TOCEntry:
    """Create a TOC entry for testing."""
    return TOCEntry(
        entry_type=entry_type,
        title=f"Test {entry_type} {number}",
        page=page,
        hyperref=f"{entry_type}.{line}",
        line_number=line,
        raw_content=raw or f"\\contentsline {{{entry_type}}}{{\\numberline {{{number}}}Title}}{{{page}}}",
        number=number,
    )


class TestFindMissingSectionGaps:
    """Test missing section gap detection."""

    def test_detects_section_after_subsection_no_gap(self, helpers):
        """Section following subsection without gap marker."""
        entries = [
            create_entry("subsection", "2.1.4", "27", 100),
            create_entry("section", "2.2", "27", 101),
        ]
        missing = helpers.find_missing_section_gaps(entries)
        assert len(missing) == 1
        assert missing[0][1].number == "2.2"

    def test_no_issue_when_gap_marker_present(self, helpers):
        """Section with addvspace marker should not trigger."""
        entries = [
            create_entry("subsection", "2.1.4", "27", 100),
            create_entry(
                "section", "2.2", "27", 101,
                raw="\\addvspace{1em}\\contentsline {section}{\\numberline{2.2}Title}{27}"
            ),
        ]
        missing = helpers.find_missing_section_gaps(entries)
        assert len(missing) == 0

    def test_section_after_chapter_ok(self, helpers):
        """Section after chapter is normal - no gap issue."""
        entries = [
            create_entry("chapter", "2", "20", 100),
            create_entry("section", "2.1", "20", 101),
        ]
        missing = helpers.find_missing_section_gaps(entries)
        assert len(missing) == 0

    def test_multiple_missing_gaps(self, helpers):
        """Multiple sections without gaps."""
        entries = [
            create_entry("subsection", "2.1.4", "27", 100),
            create_entry("section", "2.2", "27", 101),
            create_entry("subsection", "2.2.1", "28", 102),
            create_entry("subsection", "2.2.2", "29", 103),
            create_entry("section", "2.3", "30", 104),
        ]
        missing = helpers.find_missing_section_gaps(entries)
        assert len(missing) == 2
        assert missing[0][1].number == "2.2"
        assert missing[1][1].number == "2.3"


class TestFindPageNumberJumps:
    """Test page number jump detection."""

    def test_detects_large_jump_within_section(self, helpers):
        """Large page jump within same section group."""
        entries = [
            create_entry("subsection", "2.1.3", "23", 100),
            create_entry("subsection", "2.1.4", "42", 101),  # Jump of 19
        ]
        jumps = helpers.find_page_number_jumps(entries, threshold=10)
        assert len(jumps) == 1
        assert jumps[0][2] == 19  # Jump size

    def test_no_issue_for_small_jump(self, helpers):
        """Small page jumps are normal."""
        entries = [
            create_entry("subsection", "2.1.1", "23", 100),
            create_entry("subsection", "2.1.2", "25", 101),  # Jump of 2
        ]
        jumps = helpers.find_page_number_jumps(entries, threshold=10)
        assert len(jumps) == 0

    def test_jump_across_sections_ignored(self, helpers):
        """Jumps between different sections are expected."""
        entries = [
            create_entry("subsection", "2.1.4", "27", 100),
            create_entry("subsection", "2.2.1", "50", 101),  # Different section
        ]
        jumps = helpers.find_page_number_jumps(entries, threshold=10)
        assert len(jumps) == 0

    def test_backward_jump_detected(self, helpers):
        """Backward page jumps are also suspicious."""
        entries = [
            create_entry("subsection", "2.1.3", "42", 100),
            create_entry("subsection", "2.1.4", "23", 101),  # Backward jump
        ]
        jumps = helpers.find_page_number_jumps(entries, threshold=10)
        assert len(jumps) == 1
        assert jumps[0][2] == 19


class TestSameParentSection:
    """Test parent section comparison."""

    def test_same_section_returns_true(self, helpers):
        entry1 = create_entry("subsection", "2.1.3", "23", 100)
        entry2 = create_entry("subsection", "2.1.4", "24", 101)
        assert helpers._same_parent_section(entry1, entry2) is True

    def test_different_section_returns_false(self, helpers):
        entry1 = create_entry("subsection", "2.1.4", "27", 100)
        entry2 = create_entry("subsection", "2.2.1", "28", 101)
        assert helpers._same_parent_section(entry1, entry2) is False

    def test_different_chapter_returns_false(self, helpers):
        entry1 = create_entry("subsection", "2.1.4", "27", 100)
        entry2 = create_entry("subsection", "3.1.1", "50", 101)
        assert helpers._same_parent_section(entry1, entry2) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
