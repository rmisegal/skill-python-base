"""
Detection tools for QA Engine.

Provides concrete detector implementations for BiDi, code, typeset, and CLS issues.
"""

from .bib_detector import BibDetector
from .bidi_detector import BiDiDetector
from .cls_detector import CLSDetector, CLSVersionInfo
from .code_detector import CodeDetector
from .coverpage_detector import CoverpageDetector
from .heb_math_detector import HebMathDetector
from .image_detector import ImageDetector
from .infra_scanner import InfraScanner, ScanResult, MisplacedFile
from .infra_validator import InfraValidator, ValidationResult, ValidationIssue
from .subfiles_detector import SubfilesDetector
from .table_detector import TableDetector
from .toc_detector import TOCDetector
from .typeset_detector import TypesetDetector
from .caption_length_detector import CaptionLengthDetector
from .cls_sync_detector import CLSSyncDetector, CLSFileInfo

__all__ = [
    "BibDetector",
    "BiDiDetector",
    "CLSDetector",
    "CLSVersionInfo",
    "CodeDetector",
    "CoverpageDetector",
    "HebMathDetector",
    "ImageDetector",
    "InfraScanner",
    "InfraValidator",
    "MisplacedFile",
    "ScanResult",
    "SubfilesDetector",
    "TableDetector",
    "TOCDetector",
    "TypesetDetector",
    "ValidationIssue",
    "ValidationResult",
    "CaptionLengthDetector",
    "CLSSyncDetector",
    "CLSFileInfo",
]
