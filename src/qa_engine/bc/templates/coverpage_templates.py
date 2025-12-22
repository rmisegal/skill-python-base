"""
QA-compliant coverpage templates for BC content generation.

All templates pass these QA rules:
- cover-date-format: Date uses DD-MM-YYYY with \en{}
- cover-english-in-hebrew: English properly wrapped
- cover-numbers-unwrapped: Numbers wrapped with \en{}
- cover-acronym-unwrapped: Acronyms wrapped with \en{}
"""


class CoverpageTemplates:
    """QA-compliant coverpage templates."""

    @staticmethod
    def format_date(day: int, month: int, year: int) -> str:
        """
        Format date in QA-compliant format.

        Args:
            day: Day (1-31)
            month: Month (1-12)
            year: Year (e.g., 2025)

        Returns:
            Formatted date string with \en{} wrapper
        """
        return f"\\en{{{day:02d}-{month:02d}-{year}}}"

    @staticmethod
    def format_version(version: str) -> str:
        """
        Format version string in QA-compliant format.

        Args:
            version: Version string (e.g., "1.0", "2.5.1")

        Returns:
            Formatted version with \en{} wrapper
        """
        return f"גרסה \\en{{{version}}}"

    @staticmethod
    def format_title_with_acronym(hebrew_text: str, acronym: str) -> str:
        """
        Format title containing acronym.

        Args:
            hebrew_text: Hebrew part of title
            acronym: English acronym (e.g., "LLM", "AI")

        Returns:
            Formatted title with proper wrapping
        """
        return f"{hebrew_text} \\en{{{acronym}}}"

    @staticmethod
    def book_metadata(
        title_heb: str,
        subtitle_heb: str,
        author_heb: str,
        version: str,
        day: int,
        month: int,
        year: int,
    ) -> str:
        """
        Generate complete book metadata section.

        Args:
            title_heb: Hebrew book title
            subtitle_heb: Hebrew subtitle
            author_heb: Hebrew author name
            version: Version string
            day: Day of publication
            month: Month of publication
            year: Year of publication

        Returns:
            LaTeX metadata commands
        """
        date_str = CoverpageTemplates.format_date(day, month, year)
        version_str = CoverpageTemplates.format_version(version)

        return f"""\\hebrewtitle{{{title_heb}}}
\\hebrewsubtitle{{{subtitle_heb}}}
\\hebrewauthor{{{author_heb}}}
\\hebrewversion{{{version_str}}}
\\hebrewdate{{{date_str}}}"""

    @staticmethod
    def chapter_title(hebrew_text: str, english_terms: list = None) -> str:
        """
        Format chapter title with English terms properly wrapped.

        Args:
            hebrew_text: Hebrew title text
            english_terms: List of English terms to wrap

        Returns:
            Formatted chapter title
        """
        if not english_terms:
            return hebrew_text

        result = hebrew_text
        for term in english_terms:
            # Wrap each English term
            result = result.replace(term, f"\\en{{{term}}}")
        return result

    @staticmethod
    def section_title(hebrew_text: str, english_terms: list = None) -> str:
        """
        Format section title with English terms properly wrapped.

        Args:
            hebrew_text: Hebrew title text
            english_terms: List of English terms to wrap

        Returns:
            Formatted section title
        """
        return CoverpageTemplates.chapter_title(hebrew_text, english_terms)
