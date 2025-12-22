"""
Bibliography QA module for LaTeX documents.

Provides detection and fixing for citation and bibliography issues.
"""

from .detection import (
    BibDetector, BibDetectResult, BibFixResult, BibOrchestratorResult,
    BibIssue, BibIssueType, BibSeverity, CitationLocation
)
from .fixing import BibFixer
from .bib_orchestrator import BibOrchestrator

__all__ = [
    "BibOrchestrator",
    "BibDetector",
    "BibFixer",
    "BibDetectResult",
    "BibFixResult",
    "BibOrchestratorResult",
    "BibIssue",
    "BibIssueType",
    "BibSeverity",
    "CitationLocation",
]
