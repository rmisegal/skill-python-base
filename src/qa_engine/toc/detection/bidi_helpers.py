"""
BiDi helper functions for TOC detection.

Provides reusable pattern matching for bidirectional text.
All patterns loaded from JSON configuration.

Version: 2.0.0 - Added naked English detection
"""

from __future__ import annotations

import re
from typing import List, Tuple, Iterator, Optional

from ..config.config_loader import TOCConfigLoader


class BiDiHelpers:
    """Helper methods for BiDi detection."""

    LTR_WRAPPERS = [
        "LRE", "LR", "textLR",
        "textenglish", "en",
        "num", "english"
    ]

    # Extended list for checking raw content
    LTR_WRAPPER_PATTERNS = [
        r"\\LRE\s*\{",
        r"\\LR\s*\{",
        r"\\textLR\s*\{",
        r"\\textenglish\s*\{",
        r"\\en\s*\{",
        r"\\num\s*\{",
        r"\\begin\s*\{english\}",
    ]
    PAREN_MAP = {
        "parentheses": ("(", ")"),
        "brackets": ("[", "]"),
        "curly-braces": ("{", "}"),
        "angle-brackets": ("<", ">"),
    }

    def __init__(self, config: TOCConfigLoader) -> None:
        """Initialize with config."""
        self._config = config
        self._hebrew_range = config.get_unicode_range("hebrew")

    def has_ltr_wrapper(self, text: str) -> bool:
        """Check if text has any LTR wrapper."""
        return any(f"\\{w}" in text for w in self.LTR_WRAPPERS)

    def is_wrapped_at(self, text: str, pos: int) -> bool:
        """Check if position is inside a wrapper."""
        before = text[max(0, pos - 15):pos]
        return any(f"\\{w}{{" in before for w in self.LTR_WRAPPERS)

    def has_hebrew(self, text: str) -> bool:
        """Check if text contains Hebrew characters."""
        if not self._hebrew_range:
            return False
        return bool(re.search(self._hebrew_range, text))

    def has_unwrapped_percentage(self, text: str) -> bool:
        """Check for unwrapped percentage."""
        pattern = self._config.get_raw_pattern("special_patterns", "percentage")
        if not pattern:
            return False
        if re.search(pattern, text):
            return "\\num{" not in text and "\\textenglish{" not in text
        return False

    def find_unwrapped_english(self, text: str) -> Iterator[Tuple[str, int]]:
        """Find unwrapped English words (3+ chars)."""
        skip_words = {"chapter", "section", "quad", "hskip", "relax"}
        pattern = r"(?<!\\textenglish\{)(?<!\\en\{)[A-Za-z]{3,}"

        for match in re.finditer(pattern, text):
            word = match.group(0)
            if word.lower() not in skip_words:
                yield word, match.start()

    def find_unwrapped_acronyms(self, text: str) -> Iterator[str]:
        """Find unwrapped acronyms (2-6 uppercase letters)."""
        pattern = self._config.get_raw_pattern("special_patterns", "acronym")
        if not pattern:
            return

        for match in re.finditer(pattern, text):
            if not self.is_wrapped_at(text, match.start()):
                yield match.group(0)

    def check_parentheticals(self, text: str) -> Iterator[Tuple[str, bool]]:
        """Check all parenthetical pairs in text."""
        for paren_type, (open_p, close_p) in self.PAREN_MAP.items():
            if open_p in text or close_p in text:
                is_balanced = text.count(open_p) == text.count(close_p)
                yield paren_type, is_balanced

    def has_nested_parens(self, text: str) -> bool:
        """Check for nested parentheses with mixed text."""
        pattern = self._config.get_raw_pattern(
            "parenthetical_patterns", "nested_parens"
        )
        return bool(pattern and re.search(pattern, text))

    def has_heb_eng_heb_pattern(self, text: str) -> bool:
        """Check for Hebrew→English→Hebrew pattern."""
        pattern = self._config.get_raw_pattern(
            "mixed_text_patterns", "hebrew_english_hebrew"
        )
        return bool(pattern and re.search(pattern, text))

    def has_eng_heb_eng_pattern(self, text: str) -> bool:
        """Check for English→Hebrew→English pattern."""
        pattern = self._config.get_raw_pattern(
            "mixed_text_patterns", "english_hebrew_english"
        )
        return bool(pattern and re.search(pattern, text))

    def has_complex_alternating(self, text: str) -> bool:
        """Check for 3+ language switches."""
        pattern = self._config.get_raw_pattern(
            "mixed_text_patterns", "alternating_3plus"
        )
        return bool(pattern and re.search(pattern, text))

    def find_naked_english(
        self, raw_content: str, title: str
    ) -> List[Tuple[str, str]]:
        """
        Find English text that will render RTL (naked English).

        This checks for English words/phrases that are NOT wrapped
        in any LTR command and will therefore render backwards in
        an RTL document.

        Returns list of (english_text, context) tuples.
        """
        naked_english = []

        # Skip LaTeX commands and check for naked English words
        # Pattern: 3+ consecutive English letters not inside a wrapper
        english_word_pattern = r'[A-Za-z]{3,}'

        # Find all English words in title
        for match in re.finditer(english_word_pattern, title):
            word = match.group(0)
            pos = match.start()

            # Skip LaTeX command names
            if self._is_latex_command(title, pos):
                continue

            # Check if this word is wrapped in LTR
            if not self._is_in_ltr_wrapper(raw_content, word):
                naked_english.append((word, title[max(0, pos-10):pos+len(word)+10]))

        return naked_english

    def _is_latex_command(self, text: str, pos: int) -> bool:
        """Check if position is part of a LaTeX command name."""
        # Look backwards for backslash
        check_start = max(0, pos - 20)
        before = text[check_start:pos]

        # Common LaTeX command patterns to skip
        latex_commands = [
            "numberline", "texthebrew", "textenglish", "textbf",
            "textit", "chapter", "section", "subsection",
            "contentsline", "hskip", "hfill", "quad",
            "nobreak", "penalty", "leaders", "hbox",
            "pardir", "textdir", "bfseries", "relax"
        ]

        # Check if the word at pos is a known command
        for cmd in latex_commands:
            if text[pos:pos+len(cmd)] == cmd:
                # Check if preceded by backslash
                if pos > 0 and text[pos-1] == '\\':
                    return True

        return False

    def _is_in_ltr_wrapper(self, raw_content: str, word: str) -> bool:
        """
        Check if word is inside an LTR wrapper in the raw content.

        Searches for patterns like:
        - \\textenglish{...word...}
        - \\LR{...word...}
        - \\en{...word...}
        """
        for pattern in self.LTR_WRAPPER_PATTERNS:
            # Find all LTR wrapper occurrences
            wrapper_regex = pattern + r'[^}]*' + re.escape(word) + r'[^}]*\}'
            if re.search(wrapper_regex, raw_content, re.IGNORECASE):
                return True

        return False

    def has_naked_english_content(self, raw_content: str, title: str) -> bool:
        """Quick check if entry has any naked English."""
        return len(self.find_naked_english(raw_content, title)) > 0

    def get_naked_english_severity(
        self, naked_items: List[Tuple[str, str]]
    ) -> str:
        """
        Determine severity based on naked English content.

        - CRITICAL: Multiple words or long phrases
        - WARNING: Single short word
        """
        if not naked_items:
            return "INFO"

        total_chars = sum(len(word) for word, _ in naked_items)

        if len(naked_items) > 2 or total_chars > 15:
            return "CRITICAL"
        elif len(naked_items) > 1 or total_chars > 8:
            return "WARNING"
        else:
            return "WARNING"
