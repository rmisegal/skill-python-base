"""
BC Code Syntax Validator - Detects incorrect LaTeX code block syntax.

CRITICAL: pythonbox uses SQUARE BRACKETS for title: \begin{pythonbox}[Title]
         NOT curly braces: \begin{pythonbox}{Title} <- WRONG!

This validator catches syntax issues BEFORE they cause compilation failures.
"""

import re
from typing import Dict, List
from .base import BCValidatorInterface, BCValidationIssue


class BCCodeSyntaxValidator(BCValidatorInterface):
    """Validates code block syntax in LaTeX content."""

    def get_rules(self) -> Dict[str, str]:
        """Return validation rules for code syntax."""
        return {
            "code-pythonbox-curly": "pythonbox uses {title} instead of [title]",
            "code-pythonbox-double-arg": "pythonbox has two arguments {a}{b}",
            "code-no-english-wrapper": "pythonbox not wrapped in english env",
            "code-hebrew-in-title": "Hebrew characters in code block title",
        }

    def validate(self, content: str, context: dict = None) -> List[BCValidationIssue]:
        """
        Validate code block syntax.

        Args:
            content: LaTeX content to validate
            context: Optional context (file path, etc.)

        Returns:
            List of validation issues found
        """
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Rule 1: pythonbox with curly braces instead of square brackets
            # WRONG: \begin{pythonbox}{Title}
            # RIGHT: \begin{pythonbox}[Title]
            curly_match = re.search(
                r"\\begin\{pythonbox\*?\}\{([^}]*)\}", line
            )
            if curly_match:
                issues.append(BCValidationIssue(
                    rule="code-pythonbox-curly",
                    severity="critical",
                    message=f"Line {i}: pythonbox uses curly braces {{title}} "
                            f"instead of square brackets [title]",
                    line=i,
                    suggestion="Change \\begin{pythonbox}{...} to "
                               "\\begin{pythonbox}[...]",
                    auto_fixable=True,
                ))

            # Rule 2: pythonbox with double arguments {a}{b}
            # WRONG: \begin{pythonbox}{Hebrew}{English}
            double_arg = re.search(
                r"\\begin\{pythonbox\*?\}\{[^}]*\}\{[^}]*\}", line
            )
            if double_arg:
                issues.append(BCValidationIssue(
                    rule="code-pythonbox-double-arg",
                    severity="critical",
                    message=f"Line {i}: pythonbox has two arguments - "
                            f"only one [title] is allowed",
                    line=i,
                    suggestion="Use single title: \\begin{pythonbox}[Title]",
                    auto_fixable=True,
                ))

            # Rule 3: Check for Hebrew in pythonbox title
            pythonbox_title = re.search(
                r"\\begin\{pythonbox\*?\}\[([^\]]*)\]", line
            )
            if pythonbox_title:
                title = pythonbox_title.group(1)
                if re.search(r"[\u0590-\u05FF]", title):
                    issues.append(BCValidationIssue(
                        rule="code-hebrew-in-title",
                        severity="warning",
                        message=f"Line {i}: Hebrew in pythonbox title - "
                                f"use English only for code blocks",
                        line=i,
                        suggestion="Use English title for code blocks",
                        auto_fixable=False,
                    ))

        # Rule 4: Check if pythonbox is wrapped in english environment
        # Find all pythonbox that are NOT preceded by \begin{english}
        pythonbox_pattern = re.compile(
            r"\\begin\{pythonbox\*?\}[\[\{]"
        )
        english_pattern = re.compile(
            r"\\begin\{english\}"
        )

        in_english = False
        for i, line in enumerate(lines, 1):
            if english_pattern.search(line):
                in_english = True
            if r"\end{english}" in line:
                in_english = False

            if pythonbox_pattern.search(line) and not in_english:
                # Check if english started on same line
                if not english_pattern.search(line):
                    issues.append(BCValidationIssue(
                        rule="code-no-english-wrapper",
                        severity="critical",
                        message=f"Line {i}: pythonbox not wrapped in "
                                f"\\begin{{english}}...\\end{{english}}",
                        line=i,
                        suggestion="Wrap pythonbox in english environment",
                        auto_fixable=True,
                    ))

        return issues
