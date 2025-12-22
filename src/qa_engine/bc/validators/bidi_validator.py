"""
BC BiDi Validator.

Validates bidirectional text formatting in Hebrew-English content.
Wraps BiDiDetector and BiDiFixer from QA engine.
"""

from typing import Dict, Optional

from ...infrastructure.detection import BiDiDetector
from ...infrastructure.fixing import BiDiFixer
from .base import BCValidatorInterface


class BCBiDiValidator(BCValidatorInterface):
    """
    Validator for bidirectional text issues.

    Checks for:
    - Numbers without LTR wrapper (bidi-numbers)
    - English text without LTR wrapper (bidi-english)
    - Acronyms without wrapper (bidi-acronym)
    - Year ranges without wrapper (bidi-year-range)
    - TikZ without english wrapper (bidi-tikz-rtl)
    - tcolorbox without wrapper (bidi-tcolorbox)
    """

    def __init__(
        self,
        detector: Optional[BiDiDetector] = None,
        fixer: Optional[BiDiFixer] = None,
    ) -> None:
        """Initialize with BiDi detector and fixer."""
        super().__init__(
            detector=detector or BiDiDetector(),
            fixer=fixer or BiDiFixer(),
            validator_name="BCBiDiValidator",
        )

    def get_rules(self) -> Dict[str, str]:
        """Return rule name -> description mapping."""
        return {
            "bidi-numbers": "Numbers without LTR wrapper in Hebrew context",
            "bidi-english": "English words without LTR wrapper in Hebrew",
            "bidi-acronym": "Uppercase acronyms without LTR wrapper",
            "bidi-year-range": "Year range without LTR wrapper",
            "bidi-tikz-rtl": "TikZ figure without english wrapper",
            "bidi-tcolorbox": "tcolorbox without english wrapper",
            "bidi-section-english": "English in Hebrew section title",
            "bidi-missing-hebrewchapter": "Missing hebrewchapter counter",
        }

    def validate_inline_content(self, content: str) -> bool:
        """
        Quick check if content has obvious BiDi issues.

        Returns True if content appears valid (no obvious issues).
        For full validation use validate() or validate_and_fix().
        """
        # Quick pattern checks without full detection
        import re

        # Check for bare English in Hebrew context
        hebrew_pattern = r"[א-ת]"
        english_pattern = r"(?<![\\a-zA-Z])([a-zA-Z]{3,})(?![}a-zA-Z])"

        has_hebrew = bool(re.search(hebrew_pattern, content))
        if not has_hebrew:
            return True  # No Hebrew = no BiDi issues

        # Check for unwrapped English
        for match in re.finditer(english_pattern, content):
            pos = match.start()
            # Check if already wrapped
            before = content[max(0, pos - 10) : pos]
            if "\\en{" not in before and "\\textenglish{" not in before:
                return False

        return True
