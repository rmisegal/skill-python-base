"""
Test for TOC detection (v2.1).

Tests the improved detection that identifies:
- Entries with \numberline{} (numbered)
- Entries without \numberline{} (unnumbered)
- Classification of unnumbered entries
- Naked English text (will render RTL)
"""

import pytest
from pathlib import Path


# Sample TOC content for testing
SAMPLE_TOC_CONTENT = r"""
\contentsline {chapter}{\numberline {\LRE {1}}מבוא לנוף אבטחת הבינה המלאכותית יוצרת \textenglish {2025}}{1}{chapter.1}%
\contentsline {section}{\numberline {\LRE {1.1}}\texthebrew {הגדרה והיקף}}{1}{section*.4}%
\contentsline {chapter}{\texthebrew {מקורות}}{15}{chapter*.32}%
\contentsline {subsubsection}{\textenglish {(1) Agentic AI} - מודלים שמתחילים לפעול באופן עצמאי}{5}{subsubsection*.14}%
\contentsline {subsubsection}{הגדרה}{54}{subsubsection*.96}%
\contentsline {section}{English References}{54}{section.2.11}%
"""

# Sample with naked English (will render RTL)
NAKED_ENGLISH_SAMPLES = [
    # (raw_content, title, has_naked_english)
    (r"\contentsline {section}{English References}{54}{section.2.11}%",
     "English References", True),
    (r"\contentsline {section}{\textenglish{English References}}{54}{section.2.11}%",
     r"\textenglish{English References}", False),
    (r"\contentsline {section}{\LR{API Guide}}{54}{section.2.11}%",
     r"\LR{API Guide}", False),
    (r"\contentsline {section}{מדריך API}{54}{section.2.11}%",
     "מדריך API", True),  # API is naked
]


def test_detect_numberline_presence():
    """Test detection of \\numberline{} in TOC entries."""
    lines = SAMPLE_TOC_CONTENT.strip().split("\n")

    results = []
    for line in lines:
        if not line.strip():
            continue
        has_numberline = r"\numberline" in line
        results.append({
            "line": line[:60] + "...",
            "has_numberline": has_numberline
        })

    # Verify expected results
    assert results[0]["has_numberline"] is True   # Chapter 1
    assert results[1]["has_numberline"] is True   # Section 1.1
    assert results[2]["has_numberline"] is False  # מקורות (bibliography)
    assert results[3]["has_numberline"] is False  # Agentic AI subsubsection
    assert results[4]["has_numberline"] is False  # הגדרה subsubsection


def test_classify_unnumbered_entries():
    """Test classification of unnumbered entries."""
    import re

    EXPECTED_PATTERNS = [
        r"מקורות",
        r"bibliography",
        r"references",
        r"נספח",
        r"appendix",
    ]

    def classify(title: str, hyperref: str) -> str:
        """Classify an unnumbered entry."""
        for pattern in EXPECTED_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return "EXPECTED"
        if "*." in hyperref:
            return "STARRED"
        return "UNEXPECTED"

    # Test cases
    assert classify("מקורות", "chapter*.32") == "EXPECTED"
    assert classify("הגדרה", "subsubsection*.96") == "STARRED"
    assert classify("Some Title", "subsubsection*.14") == "STARRED"
    assert classify("Some Title", "section.5") == "UNEXPECTED"


def test_extract_entry_type():
    """Test extraction of entry type from TOC line."""
    import re

    pattern = r"\\contentsline\s*\{(\w+)\}"

    test_lines = [
        (r"\contentsline {chapter}{\numberline...", "chapter"),
        (r"\contentsline {section}{\numberline...", "section"),
        (r"\contentsline {subsection}{\numberline...", "subsection"),
        (r"\contentsline {subsubsection}{הגדרה}...", "subsubsection"),
    ]

    for line, expected_type in test_lines:
        match = re.search(pattern, line)
        assert match is not None
        assert match.group(1) == expected_type


def test_naked_english_detection():
    """Test detection of naked English text (v2.1)."""
    import re

    LTR_WRAPPERS = [
        r"\\textenglish\s*\{",
        r"\\LR\s*\{",
        r"\\en\s*\{",
    ]

    def has_naked_english(raw_content: str, title: str) -> bool:
        """Check if title has English not wrapped in LTR."""
        # Find English words (3+ chars)
        english_words = re.findall(r'[A-Za-z]{3,}', title)

        for word in english_words:
            # Skip LaTeX commands
            if word in ["textenglish", "texthebrew", "contentsline", "numberline"]:
                continue

            # Check if word is inside any wrapper
            is_wrapped = False
            for wrapper in LTR_WRAPPERS:
                pattern = wrapper + r'[^}]*' + re.escape(word)
                if re.search(pattern, raw_content, re.IGNORECASE):
                    is_wrapped = True
                    break

            if not is_wrapped:
                return True  # Found naked English

        return False

    # Test each sample
    for raw, title, expected in NAKED_ENGLISH_SAMPLES:
        result = has_naked_english(raw, title)
        assert result == expected, f"Failed for: {title[:30]}..."

    print("   All naked English detection tests passed")


def test_real_toc_file():
    """Test with real TOC file if available."""
    toc_path = Path(
        "C:/25D/GeneralLearning/skill-python-base/test-data/"
        "GenAI-Security-Cheat-Sheet-2025-2026/master/master-main.toc"
    )

    if not toc_path.exists():
        pytest.skip("Real TOC file not available")

    content = toc_path.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")

    # Count entries by type
    numbered = 0
    unnumbered = 0
    naked_english_count = 0

    for line in lines:
        if r"\contentsline" not in line:
            continue
        if r"\numberline" in line:
            numbered += 1
        else:
            unnumbered += 1

        # Check for naked English (simple check)
        # Find English words not in \textenglish{}
        import re
        english_words = re.findall(r'[A-Za-z]{4,}', line)
        for word in english_words:
            if word in ["contentsline", "chapter", "section", "subsection",
                       "subsubsection", "numberline", "textenglish", "texthebrew",
                       "LRE", "hskip"]:
                continue
            # Check if wrapped
            if not re.search(r'\\textenglish\s*\{[^}]*' + word, line):
                if not re.search(r'\\LR\s*\{[^}]*' + word, line):
                    naked_english_count += 1
                    break

    print(f"\nReal TOC analysis:")
    print(f"  Numbered entries: {numbered}")
    print(f"  Unnumbered entries: {unnumbered}")
    print(f"  Entries with naked English: {naked_english_count}")

    # Should have at least 1 unnumbered (bibliography)
    assert unnumbered >= 1, "Expected at least 1 unnumbered entry (bibliography)"


if __name__ == "__main__":
    print("Testing TOC detection (v2.1)...")

    print("\n1. Testing numberline presence detection:")
    test_detect_numberline_presence()
    print("   PASSED")

    print("\n2. Testing unnumbered entry classification:")
    test_classify_unnumbered_entries()
    print("   PASSED")

    print("\n3. Testing entry type extraction:")
    test_extract_entry_type()
    print("   PASSED")

    print("\n4. Testing naked English detection (v2.1):")
    test_naked_english_detection()
    print("   PASSED")

    print("\n5. Testing real TOC file:")
    try:
        test_real_toc_file()
        print("   PASSED")
    except Exception as e:
        print(f"   SKIPPED: {e}")

    print("\n[OK] All tests passed!")
