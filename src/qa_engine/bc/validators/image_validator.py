"""
BC Image Validator.

Validates figure environments have actual images.
Wraps ImageDetector from QA engine.
"""

from typing import Dict, Optional

from ...infrastructure.detection import ImageDetector
from .base import BCValidatorInterface


class BCImageValidator(BCValidatorInterface):
    """
    Validator for image/figure issues.

    Checks for:
    - Empty figure environments (img-empty-figure)
    - Missing image files (img-file-not-found)
    - Placeholder boxes (img-placeholder-box)
    """

    def __init__(
        self,
        detector: Optional[ImageDetector] = None,
    ) -> None:
        """Initialize with Image detector."""
        super().__init__(
            detector=detector or ImageDetector(),
            fixer=None,  # No auto-fixer - requires image generation
            validator_name="BCImageValidator",
        )

    def get_rules(self) -> Dict[str, str]:
        """Return rule name -> description mapping."""
        return {
            "img-empty-figure": "Figure environment without includegraphics",
            "img-file-not-found": "Referenced image file not found",
            "img-placeholder-box": "Figure contains placeholder box",
        }

    def validate_figure(self, content: str) -> bool:
        """
        Quick check if figure has actual image content.

        Returns True if figure appears valid.
        """
        import re

        # Check for figure environment
        if not re.search(r"\\begin\{(figure|hebrewfigure)\}", content):
            return True  # No figure = no issue

        # Check for includegraphics inside figure
        if re.search(r"\\includegraphics", content):
            return True

        # Check for tikzpicture (also valid)
        if re.search(r"\\begin\{tikzpicture\}", content):
            return True

        return False

    def generate_figure_template(
        self, caption_heb: str, caption_eng: str, label: str, image_path: str
    ) -> str:
        """
        Generate a proper figure environment with image.

        Returns LaTeX figure code ready for RTL document.
        """
        return f"""\\begin{{hebrewfigure}}
\\centering
\\includegraphics[width=0.8\\textwidth]{{{image_path}}}
\\caption{{{caption_heb}}}
\\label{{{label}}}
\\end{{hebrewfigure}}"""
