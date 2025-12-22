"""
Domain layer for QA Engine.

Contains core business logic, models, and service interfaces.
"""

from .models import Issue, Severity, SkillMetadata, QAStatus
from .interfaces import DetectorInterface, FixerInterface

__all__ = [
    "Issue",
    "Severity",
    "SkillMetadata",
    "QAStatus",
    "DetectorInterface",
    "FixerInterface",
]
