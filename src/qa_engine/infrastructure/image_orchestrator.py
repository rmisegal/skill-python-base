"""
Image family orchestrator (Level 1).

Coordinates image detection, fixing, creation, and validation.
Matches qa-img skill.md workflow:
Phase 1: Detection (ImageDetector)
Phase 2: Fixing (ImageFixer) + Creation (ImageCreator)
Phase 3: Validation (ImageValidator)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..domain.models.issue import Issue
from .detection.image_detector import ImageDetector
from .detection.caption_length_detector import CaptionLengthDetector
from .fixing.image_fixer import ImageFixer
from .fixing.caption_length_fixer import CaptionLengthFixer
from .creation.image_creator import ImageCreator
from .validation.image_validator import ImageValidator, ValidationResult


@dataclass
class ImageDetectResult:
    """Detection results from ImageDetector."""
    issues: List[Issue] = field(default_factory=list)
    caption_issues: List[Issue] = field(default_factory=list)
    by_rule: Dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.issues) + len(self.caption_issues)

    @property
    def verdict(self) -> str:
        return "FAIL" if self.total > 0 else "PASS"


@dataclass
class ImageFixResult:
    """Results from image fix operations."""
    paths_fixed: int = 0
    images_created: int = 0
    placeholders_replaced: int = 0
    captions_fixed: int = 0
    graphicspath_added: bool = False
    content: str = ""
    created_files: Dict[str, bool] = field(default_factory=dict)


@dataclass
class ImageOrchestratorResult:
    """Combined orchestration result matching qa-img skill.md format."""
    detect_result: Optional[ImageDetectResult] = None
    fix_result: Optional[ImageFixResult] = None
    validate_result: Optional[ValidationResult] = None
    skills_executed: Dict[str, str] = field(default_factory=dict)

    @property
    def verdict(self) -> str:
        if self.validate_result:
            return self.validate_result.verdict
        if self.detect_result and self.detect_result.total == 0:
            return "PASS"
        return "FAIL" if self.detect_result else "PASS"

    @property
    def status(self) -> str:
        return "DONE"


class ImageOrchestrator:
    """
    Level 1 family orchestrator for Image QA.

    Coordinates detection, fixing, creation, and validation.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.detector = ImageDetector(project_root=self.project_root)
        self.caption_detector = CaptionLengthDetector()
        self.fixer = ImageFixer()
        self.caption_fixer = CaptionLengthFixer()
        self.creator = ImageCreator(project_root=self.project_root)
        self.validator = ImageValidator(project_root=self.project_root)

    def run(self, content: str, file_path: str = "", apply_fixes: bool = True,
            create_missing: bool = True, validate: bool = True) -> ImageOrchestratorResult:
        """Run full Image QA pipeline."""
        result = ImageOrchestratorResult()
        result.skills_executed = {}
        # Phase 1: Detection
        detect = self._run_detection(content, file_path)
        result.detect_result = detect
        result.skills_executed["qa-img-detect"] = "DONE"
        # Phase 2: Fixes (if enabled and issues found)
        if apply_fixes and detect.total > 0:
            fix_result = self._run_fixes(content, detect, create_missing)
            result.fix_result = fix_result
            result.skills_executed["qa-img-fix-paths"] = "DONE" if fix_result.paths_fixed > 0 else "SKIP"
            result.skills_executed["qa-img-fix-missing"] = "DONE" if fix_result.images_created > 0 else "SKIP"
        else:
            result.skills_executed["qa-img-fix-paths"] = "SKIP"
            result.skills_executed["qa-img-fix-missing"] = "SKIP"
        # Phase 3: Validation (if enabled)
        if validate:
            fixed_content = result.fix_result.content if result.fix_result else content
            before_issues = [{"rule": i.rule, "content": i.content} for i in detect.issues]
            val_result = self.validator.validate_content(fixed_content, before_issues)
            result.validate_result = val_result
            result.skills_executed["qa-img-validate"] = "DONE"
        else:
            result.skills_executed["qa-img-validate"] = "SKIP"
        return result

    def _run_detection(self, content: str, file_path: str) -> ImageDetectResult:
        """Phase 1: Run detection."""
        result = ImageDetectResult()
        # Image file detection
        issues = self.detector.detect(content, file_path)
        result.issues = issues
        # Caption length detection
        caption_issues = self.caption_detector.detect(content, file_path)
        result.caption_issues = caption_issues
        # Count by rule
        for issue in issues + caption_issues:
            rule = issue.rule
            result.by_rule[rule] = result.by_rule.get(rule, 0) + 1
        return result

    def _run_fixes(self, content: str, detect: ImageDetectResult, create_missing: bool) -> ImageFixResult:
        """Phase 2: Run fixes and create missing images."""
        result = ImageFixResult()
        fixed_content = content
        # Apply path fixes
        fixed_content = self.fixer.fix(fixed_content, detect.issues)
        result.paths_fixed = sum(1 for i in detect.issues if i.rule in (
            "img-file-not-found", "img-wrong-extension", "img-case-mismatch", "img-no-size-spec"
        ))
        # Check if graphicspath was added
        if "\\graphicspath" in fixed_content and "\\graphicspath" not in content:
            result.graphicspath_added = True
        # Count placeholder replacements
        result.placeholders_replaced = sum(1 for i in detect.issues if i.rule == "img-placeholder-box")
        # Apply caption length fixes
        if detect.caption_issues:
            fixed_content = self.caption_fixer.fix(fixed_content, detect.caption_issues)
            result.captions_fixed = len(detect.caption_issues)
        # Create missing images
        if create_missing:
            missing_issues = [i for i in detect.issues if i.rule == "img-file-not-found"]
            if missing_issues:
                created = self.creator.create_from_issues(missing_issues)
                result.created_files = created
                result.images_created = sum(1 for v in created.values() if v)
        result.content = fixed_content
        return result

    def fix_preamble(self, preamble_path: Path) -> bool:
        """Fix graphicspath in preamble file by auto-detecting image directories."""
        return self.fixer.fix_preamble_graphicspath(preamble_path, self.project_root)

    def to_dict(self, result: ImageOrchestratorResult) -> Dict:
        """Convert to dictionary matching qa-img skill.md output format."""
        detect = result.detect_result or ImageDetectResult()
        fix = result.fix_result
        validate = result.validate_result
        return {
            "family": "img", "status": result.status, "verdict": result.verdict,
            "phases": {
                "source_detection": {
                    "tool": "ImageDetector", "issues": len(detect.issues),
                    "caption_issues": len(detect.caption_issues),
                    "by_rule": detect.by_rule,
                },
                "source_fixing": {
                    "tool": "ImageFixer",
                    "paths_fixed": fix.paths_fixed if fix else 0,
                    "images_created": fix.images_created if fix else 0,
                    "captions_fixed": fix.captions_fixed if fix else 0,
                    "graphicspath_added": fix.graphicspath_added if fix else False,
                },
                "validation": {
                    "tool": "ImageValidator",
                    "figures_verified": validate.figures_verified if validate else 0,
                    "all_rendered": validate.all_rendered if validate else False,
                    "verdict": validate.verdict if validate else "SKIP",
                },
            },
            "skills_executed": [
                {"skill": k, "status": v} for k, v in result.skills_executed.items()
            ],
        }
