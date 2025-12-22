"""
BC Validators module.

Provides validator classes that wrap QA detectors and fixers for inline
validation during content creation. Each validator follows the project's
architecture patterns: thread-safe, config-driven, no hardcoded data.
"""

from .base import BCValidatorInterface
from .result import ValidationResult, FixAttempt
from .config import BCConfigManager, BCConfigError
from .bidi_validator import BCBiDiValidator
from .code_validator import BCCodeValidator
from .table_validator import BCTableValidator
from .bib_validator import BCBibValidator
from .image_validator import BCImageValidator
from .coverpage_validator import BCCoverpageValidator
from .code_syntax_validator import BCCodeSyntaxValidator
from .tikz_syntax_validator import BCTikZSyntaxValidator

__all__ = [
    "BCValidatorInterface",
    "ValidationResult",
    "FixAttempt",
    "BCConfigManager",
    "BCConfigError",
    "BCBiDiValidator",
    "BCCodeValidator",
    "BCTableValidator",
    "BCBibValidator",
    "BCImageValidator",
    "BCCoverpageValidator",
    "BCCodeSyntaxValidator",
    "BCTikZSyntaxValidator",
]
