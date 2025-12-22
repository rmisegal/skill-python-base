"""
Typeset fixing tools for QA Engine.

Provides fixers for mdframed page break, section orphan, hbox, and vbox issues.
"""

from .mdframed_fixer import MdframedFixer, MdframedFixResult, FixApplied
from .orphan_fixer import SectionOrphanFixer, OrphanFixResult, OrphanFixApplied
from .hbox_fixer import HboxFixer, HboxFixResult, HboxFix, ManualReview
from .vbox_fixer import VboxFixer, VboxFixResult, VboxFix, VboxManualReview, VboxFixType

__all__ = [
    "MdframedFixer",
    "MdframedFixResult",
    "FixApplied",
    "SectionOrphanFixer",
    "OrphanFixResult",
    "OrphanFixApplied",
    "HboxFixer",
    "HboxFixResult",
    "HboxFix",
    "ManualReview",
    "VboxFixer",
    "VboxFixResult",
    "VboxFix",
    "VboxManualReview",
    "VboxFixType",
]
