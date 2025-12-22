"""
BC Content Templates module.

Provides QA-compliant LaTeX templates for content generation.
These templates are designed to pass all QA checks with 0 issues.
"""

from .table_templates import TableTemplates
from .figure_templates import FigureTemplates
from .code_templates import CodeTemplates
from .bib_templates import BibTemplates
from .coverpage_templates import CoverpageTemplates

__all__ = [
    "TableTemplates",
    "FigureTemplates",
    "CodeTemplates",
    "BibTemplates",
    "CoverpageTemplates",
]
