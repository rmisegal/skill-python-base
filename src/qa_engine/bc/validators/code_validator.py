"""
BC Code Validator.

Validates Python code blocks in LaTeX documents.
Wraps CodeDetector and CodeFixer from QA engine.
"""

from typing import Dict, Optional

from ...infrastructure.detection import CodeDetector
from ...infrastructure.fixing import CodeFixer
from .base import BCValidatorInterface


class BCCodeValidator(BCValidatorInterface):
    """
    Validator for code block issues.

    Checks for:
    - pythonbox/tcolorbox without english wrapper (code-background-overflow)
    - Hebrew text in code blocks (code-direction-hebrew)
    - Emoji characters in code (code-encoding-emoji)
    """

    def __init__(
        self,
        detector: Optional[CodeDetector] = None,
        fixer: Optional[CodeFixer] = None,
    ) -> None:
        """Initialize with Code detector and fixer."""
        super().__init__(
            detector=detector or CodeDetector(),
            fixer=fixer or CodeFixer(),
            validator_name="BCCodeValidator",
        )

    def get_rules(self) -> Dict[str, str]:
        """Return rule name -> description mapping."""
        return {
            "code-background-overflow": "Code block without english wrapper",
            "code-direction-hebrew": "Hebrew text in code block",
            "code-encoding-emoji": "Emoji characters in code",
            "code-hebrew-content": "Hebrew in comments/strings",
        }

    def validate_code_block(self, code: str) -> bool:
        """
        Quick check if code block has obvious issues.

        Returns True if code appears valid.
        """
        import re

        # Check for Hebrew characters
        if re.search(r"[א-ת]", code):
            return False

        # Check for emoji
        if re.search(r"[\U0001F300-\U0001F9FF]", code):
            return False

        return True

    def wrap_in_english(self, content: str) -> str:
        """
        Wrap pythonbox environments in english wrapper if needed.

        Returns modified content with proper wrapping.
        """
        import re

        # Pattern for pythonbox not already wrapped
        pattern = r"(?<!\\begin\{english\}\s*)\\begin\{pythonbox"

        if re.search(pattern, content):
            # Add english wrapper
            content = re.sub(
                r"(\\begin\{pythonbox)(\*?)(\})",
                r"\\begin{english}\n\1\2\3",
                content,
            )
            content = re.sub(
                r"(\\end\{pythonbox)(\*?)(\})",
                r"\1\2\3\n\\end{english}",
                content,
            )

        return content
