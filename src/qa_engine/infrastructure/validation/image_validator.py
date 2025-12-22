"""Image validator for post-fix verification. Aligned with qa-img-validate skill."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

@dataclass
class FigureComparison:
    """Before/after comparison for a figure."""
    figure: int
    before: str  # MISSING, EMPTY_BOX, PLACEHOLDER
    after: str  # RENDERED, MISSING, EMPTY_BOX

@dataclass
class ValidationResult:
    """Result of image validation."""
    figures_verified: int = 0
    all_rendered: bool = True
    comparison: List[FigureComparison] = field(default_factory=list)
    still_missing: List[int] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return "PASS" if self.all_rendered else "FAIL"

    @property
    def status(self) -> str:
        return "DONE"

class ImageValidator:
    """
    Validates images render correctly after fixes.

    Source-level validation (Python):
    - Check image files exist after creation
    - Verify includegraphics paths resolve
    - Compare before/after issue counts

    PDF-level validation (LLM required):
    - Visual verification of rendered images
    - Empty box detection in PDF
    """
    INCLUDEGRAPHICS = re.compile(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}')
    FIGURE_ENV = re.compile(r'\\begin\{figure\}.*?\\end\{figure\}', re.DOTALL)
    CAPTION = re.compile(r'\\caption\{([^}]+)\}')

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize validator with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self._before_state: Dict[int, str] = {}

    def record_before_state(self, issues: List[Dict]) -> None:
        """Record the state before fixes are applied."""
        self._before_state.clear()
        for i, issue in enumerate(issues, 1):
            if "image" in issue.get("rule", "").lower() or "missing" in str(issue).lower():
                self._before_state[i] = "MISSING"

    def validate_after_fixes(self, content: str, source_dir: Optional[Path] = None) -> ValidationResult:
        """Validate images after fixes have been applied."""
        result = ValidationResult()
        dir_path = source_dir or self.project_root

        # Find all includegraphics commands
        figures = self._find_figures(content)
        result.figures_verified = len(figures)

        # Check each figure
        for fig_num, (img_path, caption) in enumerate(figures, 1):
            before = self._before_state.get(fig_num, "UNKNOWN")
            after = "RENDERED" if self._image_exists(img_path, dir_path) else "MISSING"

            result.comparison.append(FigureComparison(figure=fig_num, before=before, after=after))
            if after == "MISSING":
                result.all_rendered = False
                result.still_missing.append(fig_num)

        return result

    def validate_content(self, content: str, before_issues: List[Dict] = None,
                        source_dir: Optional[Path] = None) -> ValidationResult:
        """Full validation: record before state and validate after."""
        if before_issues:
            self.record_before_state(before_issues)
        return self.validate_after_fixes(content, source_dir)

    def _find_figures(self, content: str) -> List[Tuple[str, str]]:
        """Find all figures with their image paths and captions."""
        figures = []
        for match in self.FIGURE_ENV.finditer(content):
            fig_content = match.group(0)
            img_match = self.INCLUDEGRAPHICS.search(fig_content)
            cap_match = self.CAPTION.search(fig_content)
            if img_match:
                img_path = img_match.group(1)
                caption = cap_match.group(1)[:50] if cap_match else ""
                figures.append((img_path, caption))
        # Also find standalone includegraphics
        for match in self.INCLUDEGRAPHICS.finditer(content):
            img_path = match.group(1)
            if not any(img_path == f[0] for f in figures):
                figures.append((img_path, ""))
        return figures

    def _image_exists(self, img_path: str, source_dir: Path) -> bool:
        """Check if image file exists in common locations."""
        search_paths = [
            source_dir / img_path, source_dir / "images" / img_path,
            source_dir / "figures" / img_path, self.project_root / img_path,
            self.project_root / "images" / img_path,
        ]
        if not Path(img_path).suffix:
            for ext in [".png", ".jpg", ".jpeg", ".pdf"]:
                search_paths.extend([p.with_suffix(ext) for p in search_paths[:5]])
        return any(p.exists() for p in search_paths)

    def to_dict(self, result: ValidationResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-img-validate", "status": result.status, "verdict": result.verdict,
            "figures_verified": result.figures_verified, "all_rendered": result.all_rendered,
            "comparison": [{"figure": c.figure, "before": c.before, "after": c.after} for c in result.comparison],
            "still_missing": result.still_missing
        }
