"""
QA Engine - Python backend for QA Skill System.

This package provides deterministic detection and fix tools
for Hebrew-English LaTeX document quality assurance.
"""

__version__ = "1.0.0"
__author__ = "QA Team"

from .interfaces import (
    Severity,
    Issue,
    DetectorInterface,
    FixerInterface,
)

__all__ = [
    "Severity",
    "Issue",
    "DetectorInterface",
    "FixerInterface",
    "__version__",
]
