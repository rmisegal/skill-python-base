"""
Unit tests for TOC fixer.

Tests Python-based fixes for TOC counter issues.
"""

import pytest

from qa_engine.infrastructure.fixing.toc_fixer import TOCFixer


class TestTOCFixerNumberline:
    """Tests for numberline double-wrap fix."""

    def setup_method(self):
        self.fixer = TOCFixer()

    def test_fix_numberline_double_wrap(self):
        """Remove textenglish from numberline."""
        content = r"\renewcommand{\numberline}[1]{\orig@numberline{\textenglish{#1}}}"
        fixed, changed = self.fixer.fix_numberline_double_wrap(content)
        assert changed
        assert r"\textenglish{#1}" not in fixed

    def test_no_change_when_no_double_wrap(self):
        """No change when numberline is correct."""
        content = r"\renewcommand{\numberline}[1]{\orig@numberline{#1}}"
        fixed, changed = self.fixer.fix_numberline_double_wrap(content)
        assert not changed


class TestTOCFixerThechapter:
    """Tests for thechapter fixes."""

    def setup_method(self):
        self.fixer = TOCFixer()

    def test_fix_thechapter_no_wrapper(self):
        """Add textenglish wrapper to thechapter."""
        content = r"\renewcommand{\thechapter}{\arabic{chapter}}"
        fixed, changed = self.fixer.fix_thechapter_no_wrapper(content)
        assert changed
        assert r"\textenglish{\arabic{chapter}}" in fixed

    def test_no_change_when_already_wrapped(self):
        """No change when thechapter already wrapped."""
        content = r"\renewcommand{\thechapter}{\textenglish{\arabic{chapter}}}"
        fixed, changed = self.fixer.fix_thechapter_no_wrapper(content)
        assert not changed


class TestTOCFixerAllCounters:
    """Tests for fixing all counter issues."""

    def setup_method(self):
        self.fixer = TOCFixer()

    def test_fix_all_counter_issues(self):
        """Fix multiple counter issues at once."""
        content = r"""
\renewcommand{\thechapter}{\arabic{chapter}}
\renewcommand{\thesection}{\arabic{section}}
"""
        fixed, count = self.fixer.fix_all_counter_issues(content)
        assert count >= 2
        assert r"\textenglish{\arabic{chapter}}" in fixed
        assert r"\textenglish{\arabic{section}}" in fixed


class TestTOCFixerLLMCheck:
    """Tests for LLM requirement check."""

    def test_l_at_rules_require_llm(self):
        """l@ command rules require LLM."""
        assert TOCFixer.requires_llm("toc-lchapter-no-rtl")
        assert TOCFixer.requires_llm("toc-lsection-no-rtl")
        assert TOCFixer.requires_llm("toc-lsubsection-no-rtl")

    def test_counter_rules_dont_require_llm(self):
        """Counter rules can be Python-fixed."""
        assert not TOCFixer.requires_llm("toc-thechapter-no-wrapper")
        assert not TOCFixer.requires_llm("toc-numberline-double-wrap")
