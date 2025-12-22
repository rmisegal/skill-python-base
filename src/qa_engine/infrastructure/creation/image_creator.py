"""
Image creator for generating placeholder images.

Implements CreatorInterface - creates actual image files on disk.
Used when LaTeX references images that don't exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ...domain.interfaces import CreatorInterface
from ...domain.models.issue import Issue

# PIL import with graceful fallback
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class ImageConfig:
    """Configuration for placeholder image generation."""
    width: int = 800
    height: int = 600
    bg_color: str = "lightblue"
    border_color: str = "darkblue"
    text_color: str = "darkblue"
    border_width: int = 3
    text: str = "Placeholder Image"


class ImageCreator(CreatorInterface):
    """
    Creates placeholder images for missing files.

    Supports PNG, JPG, and PDF formats.
    Uses PIL (Pillow) for image generation.
    """

    SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg", ".pdf"]
    DEFAULT_CONFIG = ImageConfig()

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize creator with project root."""
        self._project_root = project_root or Path.cwd()
        self._config = self.DEFAULT_CONFIG

    def create(self, path: str, **options) -> bool:
        """Create a placeholder image at the specified path."""
        if not PIL_AVAILABLE:
            return False

        full_path = self._resolve_path(path)
        config = self._merge_config(options)

        # Create parent directory
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Create and save image
        img = self._create_placeholder_image(config, full_path.stem)
        return self._save_image(img, full_path)

    def create_from_issues(self, issues: List[Issue]) -> Dict[str, bool]:
        """Create placeholder images for all missing file issues."""
        results: Dict[str, bool] = {}

        for issue in issues:
            if issue.rule != "img-file-not-found":
                continue

            path = issue.context.get("image_path", issue.content)
            if path:
                results[path] = self.create(path)

        return results

    def get_supported_formats(self) -> List[str]:
        """Return list of supported image formats."""
        return self.SUPPORTED_FORMATS.copy()

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to project root."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self._project_root / path

    def _merge_config(self, options: Dict) -> ImageConfig:
        """Merge options with default config."""
        return ImageConfig(
            width=options.get("width", self._config.width),
            height=options.get("height", self._config.height),
            bg_color=options.get("bg_color", self._config.bg_color),
            border_color=options.get("border_color", self._config.border_color),
            text_color=options.get("text_color", self._config.text_color),
            border_width=options.get("border_width", self._config.border_width),
            text=options.get("text", self._config.text),
        )

    def _create_placeholder_image(self, config: ImageConfig, name: str) -> "Image":
        """Create a placeholder image with border and text."""
        img = Image.new("RGB", (config.width, config.height), color=config.bg_color)
        draw = ImageDraw.Draw(img)

        # Draw border
        margin = 50
        draw.rectangle(
            [margin, margin, config.width - margin, config.height - margin],
            outline=config.border_color,
            width=config.border_width,
        )

        # Draw text
        text = f"{config.text}\n{name}"
        self._draw_centered_text(draw, text, config)

        return img

    def _draw_centered_text(
        self, draw: "ImageDraw", text: str, config: ImageConfig
    ) -> None:
        """Draw centered text on image."""
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except (OSError, IOError):
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (config.width - text_width) // 2
        y = (config.height - text_height) // 2

        draw.text((x, y), text, fill=config.text_color, font=font)

    def _save_image(self, img: "Image", path: Path) -> bool:
        """Save image to file with appropriate format."""
        try:
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                img.save(path, "PDF", resolution=300)
            elif suffix in [".jpg", ".jpeg"]:
                img = img.convert("RGB")
                img.save(path, "JPEG", quality=95)
            else:
                img.save(path, "PNG")
            return True
        except Exception:
            return False
