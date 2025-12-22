"""
TOC QA module for comprehensive Table of Contents validation.

Provides 48 detection rules for Hebrew-English bilingual documents:
- 4 Numbering rules
- 16 BiDi direction rules (numbers, parentheticals, text, alignment)
- 8 Structure rules
- 8 Validation rules

All configuration loaded from JSON files - no hardcoded data.
"""

from .detection import (
    TOCComprehensiveDetector,
    TOCEntryParser,
    TOCEntry,
    TOCNumberingDetector,
    TOCBiDiDetector,
    TOCStructureDetector,
)
from .config import TOCConfigLoader

__all__ = [
    "TOCComprehensiveDetector",
    "TOCEntryParser",
    "TOCEntry",
    "TOCNumberingDetector",
    "TOCBiDiDetector",
    "TOCStructureDetector",
    "TOCConfigLoader",
]
