"""
BC TikZ Syntax Validator - Detects incorrect wrapper usage in TikZ code.

CRITICAL: TikZ code is already in LTR/English context.
Using \\en{}, \\num{}, or \\textenglish{} inside TikZ BREAKS compilation.

This validator catches wrapper misuse BEFORE it causes compilation failures.
"""

import re
from typing import Dict, List
from .base import BCValidatorInterface, BCValidationIssue


class BCTikZSyntaxValidator(BCValidatorInterface):
    """Validates TikZ code doesn't contain illegal wrappers."""

    def get_rules(self) -> Dict[str, str]:
        """Return validation rules for TikZ syntax."""
        return {
            "tikz-en-wrapper": "\\en{} used inside TikZ - breaks parsing",
            "tikz-num-wrapper": "\\num{} used in TikZ coordinates",
            "tikz-textenglish": "\\textenglish{} in TikZ commands",
            "tikz-node-name-wrapper": "Wrapper in TikZ node name (id)",
        }

    def validate(self, content: str, context: dict = None) -> List[BCValidationIssue]:
        """
        Validate TikZ code doesn't contain illegal wrappers.

        Args:
            content: LaTeX content to validate
            context: Optional context (file path, etc.)

        Returns:
            List of validation issues found
        """
        issues = []
        lines = content.split("\n")

        # Track if we're inside a tikzpicture environment
        in_tikz = False
        tikz_start_line = 0

        for i, line in enumerate(lines, 1):
            # Track tikzpicture environment
            if r"\begin{tikzpicture}" in line:
                in_tikz = True
                tikz_start_line = i
            if r"\end{tikzpicture}" in line:
                in_tikz = False

            if not in_tikz:
                continue

            # Rule 1: \\en{} inside TikZ
            if r"\en{" in line:
                issues.append(BCValidationIssue(
                    rule="tikz-en-wrapper",
                    severity="critical",
                    message=f"Line {i}: \\en{{}} used inside TikZ "
                            f"(started at line {tikz_start_line})",
                    line=i,
                    suggestion="Remove \\en{} - TikZ is already LTR",
                    auto_fixable=True,
                ))

            # Rule 2: \\num{} inside TikZ coordinates
            if r"\num{" in line:
                issues.append(BCValidationIssue(
                    rule="tikz-num-wrapper",
                    severity="critical",
                    message=f"Line {i}: \\num{{}} in TikZ coordinates",
                    line=i,
                    suggestion="Use plain numbers: at (0, 0) not at (\\num{0}, \\num{0})",
                    auto_fixable=True,
                ))

            # Rule 3: \\textenglish{} inside TikZ
            if r"\textenglish{" in line:
                issues.append(BCValidationIssue(
                    rule="tikz-textenglish",
                    severity="critical",
                    message=f"Line {i}: \\textenglish{{}} inside TikZ",
                    line=i,
                    suggestion="Remove \\textenglish{} - TikZ is already LTR",
                    auto_fixable=True,
                ))

            # Rule 4: Wrapper in node name/id like (\en{input})
            node_name_wrapper = re.search(
                r"\(\\(en|num|textenglish)\{[^}]*\}\)", line
            )
            if node_name_wrapper:
                issues.append(BCValidationIssue(
                    rule="tikz-node-name-wrapper",
                    severity="critical",
                    message=f"Line {i}: Wrapper in TikZ node name",
                    line=i,
                    suggestion="Node names must be plain: (input) not (\\en{input})",
                    auto_fixable=True,
                ))

        return issues
