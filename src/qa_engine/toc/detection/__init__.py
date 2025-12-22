"""
TOC detection module.

Provides comprehensive Table of Contents validation for
Hebrew-English bilingual LaTeX documents.

Exports:
    TOCComprehensiveDetector: Main orchestrator for all detection
    TOCEntryParser: Parser for .toc files
    TOCNumberingDetector: Numbering validation
    TOCBiDiDetector: BiDi direction validation
    TOCStructureDetector: Structure validation
    BaseTOCDetector: Abstract base class
"""

from .toc_comprehensive_detector import TOCComprehensiveDetector
from .toc_entry_parser import TOCEntryParser, TOCEntry
from .toc_numbering_detector import TOCNumberingDetector
from .toc_bidi_detector import TOCBiDiDetector
from .toc_structure_detector import TOCStructureDetector
from .base_toc_detector import BaseTOCDetector

__all__ = [
    "TOCComprehensiveDetector",
    "TOCEntryParser",
    "TOCEntry",
    "TOCNumberingDetector",
    "TOCBiDiDetector",
    "TOCStructureDetector",
    "BaseTOCDetector",
]
