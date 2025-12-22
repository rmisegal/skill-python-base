"""
BC Bibliography Validator.

Validates bibliography entries and citations.
Wraps BibDetector and BibFixer from QA engine.
"""

from typing import Dict, Optional

from ...infrastructure.detection import BibDetector
from ...infrastructure.fixing import BibFixer
from .base import BCValidatorInterface


class BCBibValidator(BCValidatorInterface):
    """
    Validator for bibliography issues.

    Checks for:
    - Malformed citation keys with LaTeX commands (bib-malformed-cite-key)
    - Missing bibliography file (bib-missing-file)
    - Empty citation commands (bib-empty-cite)
    """

    def __init__(
        self,
        detector: Optional[BibDetector] = None,
        fixer: Optional[BibFixer] = None,
    ) -> None:
        """Initialize with Bib detector and fixer."""
        super().__init__(
            detector=detector or BibDetector(),
            fixer=fixer or BibFixer(),
            validator_name="BCBibValidator",
        )

    def get_rules(self) -> Dict[str, str]:
        """Return rule name -> description mapping."""
        return {
            "bib-malformed-cite-key": "Citation key contains LaTeX commands",
            "bib-missing-file": "Bibliography file not found",
            "bib-empty-cite": "Empty citation command",
            "bib-undefined-cite": "Citation key not defined",
        }

    def validate_cite_key(self, key: str) -> bool:
        """
        Check if citation key is valid.

        Returns True if key is alphanumeric without LaTeX commands.
        """
        import re

        # Check for LaTeX commands in key
        if re.search(r"\\(hebyear|en|num|textenglish)\{", key):
            return False

        # Key should be alphanumeric with underscores/hyphens
        if not re.match(r"^[a-zA-Z0-9_-]+$", key):
            return False

        return True

    def clean_cite_key(self, key: str) -> str:
        """
        Clean citation key by removing LaTeX commands.

        Returns cleaned alphanumeric key.
        """
        import re

        # Remove LaTeX commands
        cleaned = re.sub(r"\\hebyear\{([^}]+)\}", r"\1", key)
        cleaned = re.sub(r"\\en\{([^}]+)\}", r"\1", key)
        cleaned = re.sub(r"\\num\{([^}]+)\}", r"\1", key)
        cleaned = re.sub(r"\\textenglish\{([^}]+)\}", r"\1", key)

        # Remove non-alphanumeric except underscore/hyphen
        cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", cleaned)

        return cleaned

    def validate_bibtex_entry(self, entry: str) -> bool:
        """
        Quick check if BibTeX entry has proper structure.

        Returns True if entry appears valid.
        """
        import re

        # Check for required fields
        required = ["author", "title", "year"]
        for field in required:
            if not re.search(rf"{field}\s*=", entry, re.IGNORECASE):
                return False

        return True
