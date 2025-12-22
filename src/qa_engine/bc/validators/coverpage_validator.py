"""
BC Coverpage Validator.

Validates cover page metadata for BiDi correctness.
Wraps CoverpageDetector from QA engine.
"""

from typing import Dict, Optional

from ...infrastructure.detection import CoverpageDetector
from .base import BCValidatorInterface


class BCCoverpageValidator(BCValidatorInterface):
    """
    Validator for cover page issues.

    Checks for:
    - Date format (cover-date-format)
    - English in Hebrew metadata (cover-english-in-hebrew)
    - Unwrapped numbers (cover-numbers-unwrapped)
    - Unwrapped acronyms (cover-acronym-unwrapped)
    """

    def __init__(
        self,
        detector: Optional[CoverpageDetector] = None,
    ) -> None:
        """Initialize with Coverpage detector."""
        super().__init__(
            detector=detector or CoverpageDetector(),
            fixer=None,
            validator_name="BCCoverpageValidator",
        )

    def get_rules(self) -> Dict[str, str]:
        """Return rule name -> description mapping."""
        return {
            "cover-date-format": "Date format should use DD-MM-YYYY with \\en{}",
            "cover-english-in-hebrew": "English text in Hebrew metadata",
            "cover-numbers-unwrapped": "Numbers without \\en{} wrapper",
            "cover-acronym-unwrapped": "Acronym without \\en{} wrapper",
        }

    def validate_metadata(self, content: str) -> bool:
        """
        Quick check if cover metadata is properly formatted.

        Returns True if metadata appears valid.
        """
        import re

        # Check date format
        date_match = re.search(r"\\hebrewdate\{([^}]+)\}", content)
        if date_match:
            date = date_match.group(1)
            # Should have \en{} wrapped date
            if not re.search(r"\\en\{", date):
                return False

        # Check version format - CRITICAL
        version_match = re.search(r"\\hebrewversion\{([^}]+)\}", content)
        if version_match:
            version = version_match.group(1)
            # Check for wrong \num{} usage - should use \en{}
            if re.search(r"\\num\{\d+\}[.,]\d+", version):
                return False  # FAIL: \num{1}.0 instead of \en{1.0}
            # Check for unwrapped decimal version
            if re.search(r"\d+\.\d+", version):
                if not re.search(r"\\en\{\d+\.\d+\}", version):
                    return False  # FAIL: X.Y without \en{}

        return True

    def generate_date(self, day: int, month: int, year: int) -> str:
        """Generate properly formatted Hebrew date."""
        return f"\\en{{{day:02d}-{month:02d}-{year}}}"

    def generate_version(self, version: str) -> str:
        """Generate properly formatted version string."""
        return f"גרסה \\en{{{version}}}"
