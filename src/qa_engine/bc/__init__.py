"""
BC (Book Creator) module for content creation with QA validation.

Provides validators that wrap QA detectors/fixers for inline validation
during content creation, following the same architecture patterns as
the QA engine.
"""

from .validators import (
    BCValidatorInterface,
    BCBiDiValidator,
    BCCodeValidator,
    BCTableValidator,
    BCBibValidator,
    ValidationResult,
    FixAttempt,
)
from .validators.config import BCConfigManager
from .orchestrator import BCOrchestrator

__all__ = [
    "BCValidatorInterface",
    "BCBiDiValidator",
    "BCCodeValidator",
    "BCTableValidator",
    "BCBibValidator",
    "ValidationResult",
    "FixAttempt",
    "BCConfigManager",
    "BCOrchestrator",
]
