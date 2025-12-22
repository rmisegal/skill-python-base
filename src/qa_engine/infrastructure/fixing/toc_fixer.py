"""
TOC configuration fixer.

Provides Python-based fixes for simple TOC issues.
Complex l@ command fixes remain LLM-only.
"""

from __future__ import annotations

import re
from typing import Tuple, Optional


class TOCFixer:
    """
    Fixes simple TOC configuration issues in CLS files.

    Python-fixable:
    - toc-numberline-double-wrap (remove wrapper)
    - toc-missing-thechapter (add definition)
    - toc-thechapter-no-wrapper (add textenglish)

    LLM-only:
    - toc-lchapter-no-rtl (complex macro restructuring)
    - toc-lsection-no-rtl
    - toc-lsubsection-no-rtl
    """

    def fix_numberline_double_wrap(self, content: str) -> Tuple[str, bool]:
        """
        Remove \textenglish{} from \numberline if counters handle it.

        Returns:
            Tuple of (fixed_content, was_changed)
        """
        pattern = r"\\renewcommand\{\\numberline\}\[1\]\{\\orig@numberline\{\\textenglish\{#1\}\}\}"
        replacement = r"% \\numberline wrapper removed - counters handle LTR"

        new_content, count = re.subn(pattern, replacement, content)
        return new_content, count > 0

    def fix_missing_thechapter(self, content: str) -> Tuple[str, bool]:
        """
        Add \thechapter definition before \thesection if missing.

        Returns:
            Tuple of (fixed_content, was_changed)
        """
        # Check if already has \thechapter with textenglish
        if re.search(r"\\renewcommand\{\\thechapter\}\{\\textenglish", content):
            return content, False

        # Find \thesection definition
        pattern = r"(% Section numbering.*\n)(\\renewcommand\{\\thesection\})"
        replacement = (
            r"% Chapter numbering - always LTR\n"
            r"\\renewcommand{\\thechapter}{\\textenglish{\\arabic{chapter}}}\n\n"
            r"\1\2"
        )

        new_content, count = re.subn(pattern, replacement, content)
        return new_content, count > 0

    def fix_thechapter_no_wrapper(self, content: str) -> Tuple[str, bool]:
        """
        Add \textenglish{} wrapper to \thechapter definition.

        Returns:
            Tuple of (fixed_content, was_changed)
        """
        pattern = r"\\renewcommand\{\\thechapter\}\{\\arabic\{chapter\}\}"
        replacement = r"\\renewcommand{\\thechapter}{\\textenglish{\\arabic{chapter}}}"

        new_content, count = re.subn(pattern, replacement, content)
        return new_content, count > 0

    def fix_thesection_no_wrapper(self, content: str) -> Tuple[str, bool]:
        """
        Add \textenglish{} wrapper to \thesection definition.
        """
        pattern = r"\\renewcommand\{\\thesection\}\{\\arabic\{section\}\}"
        replacement = r"\\renewcommand{\\thesection}{\\textenglish{\\arabic{section}}}"

        new_content, count = re.subn(pattern, replacement, content)
        return new_content, count > 0

    def fix_thesubsection_no_wrapper(self, content: str) -> Tuple[str, bool]:
        """
        Add \textenglish{} wrapper to \thesubsection definition.
        """
        pattern = r"\\renewcommand\{\\thesubsection\}\{\\arabic\{section\}\.\\arabic\{subsection\}\}"
        replacement = (
            r"\\renewcommand{\\thesubsection}"
            r"{\\textenglish{\\arabic{section}.\\arabic{subsection}}}"
        )
        new_content, count = re.subn(pattern, replacement, content)
        return new_content, count > 0

    def fix_all_counter_issues(self, content: str) -> Tuple[str, int]:
        """
        Apply all counter-related fixes.

        Returns:
            Tuple of (fixed_content, num_fixes_applied)
        """
        fixes = 0

        content, changed = self.fix_numberline_double_wrap(content)
        if changed:
            fixes += 1

        content, changed = self.fix_thechapter_no_wrapper(content)
        if changed:
            fixes += 1

        content, changed = self.fix_thesection_no_wrapper(content)
        if changed:
            fixes += 1

        content, changed = self.fix_thesubsection_no_wrapper(content)
        if changed:
            fixes += 1

        content, changed = self.fix_missing_thechapter(content)
        if changed:
            fixes += 1

        return content, fixes

    @staticmethod
    def requires_llm(rule: str) -> bool:
        """Check if a rule requires LLM for fixing."""
        llm_only_rules = {
            "toc-lchapter-no-rtl",
            "toc-lsection-no-rtl",
            "toc-lsubsection-no-rtl",
        }
        return rule in llm_only_rules
