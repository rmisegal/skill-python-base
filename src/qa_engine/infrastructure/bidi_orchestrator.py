"""
BiDi family orchestrator (Level 1).

Coordinates BiDi detectors and fixers in parallel, matching qa-BiDi skill.md.
Phase 1: Run detectors (BiDiDetector, HebMathDetector)
Phase 2: Run fixers based on detection results
Phase 3: Aggregate and report
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..domain.models.issue import Issue
from .detection.bidi_detector import BiDiDetector
from .detection.heb_math_detector import HebMathDetector
from .fixing.bidi_fixer import BiDiFixer
from .fixing.heb_math_fixer import HebMathFixer
from .fixing.tikz_fixer import TikzFixer


@dataclass
class BiDiDetectResult:
    """Detection results from all BiDi detectors."""
    text_issues: List[Issue] = field(default_factory=list)
    number_issues: List[Issue] = field(default_factory=list)
    math_hebrew_issues: List[Issue] = field(default_factory=list)
    tikz_issues: List[Issue] = field(default_factory=list)
    acronym_issues: List[Issue] = field(default_factory=list)
    other_issues: List[Issue] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(len(lst) for lst in [
            self.text_issues, self.number_issues, self.math_hebrew_issues,
            self.tikz_issues, self.acronym_issues, self.other_issues
        ])

    @property
    def verdict(self) -> str:
        return "FAIL" if self.total > 0 else "PASS"


@dataclass
class BiDiFixResult:
    """Results from BiDi fix operations."""
    text_fixed: int = 0
    numbers_fixed: int = 0
    math_fixed: int = 0
    tikz_fixed: int = 0
    content: str = ""


@dataclass
class BiDiOrchestratorResult:
    """Combined orchestration result matching skill.md output format."""
    detect_result: Optional[BiDiDetectResult] = None
    fix_result: Optional[BiDiFixResult] = None
    skills_executed: Dict[str, str] = field(default_factory=dict)

    @property
    def verdict(self) -> str:
        if self.detect_result:
            remaining = self.detect_result.total
            if self.fix_result:
                remaining -= (self.fix_result.text_fixed + self.fix_result.numbers_fixed +
                             self.fix_result.math_fixed + self.fix_result.tikz_fixed)
            return "PASS" if remaining <= 0 else "FAIL"
        return "PASS"

    @property
    def status(self) -> str:
        return "DONE"


class BiDiOrchestrator:
    """
    Level 1 family orchestrator for BiDi QA.

    Coordinates all BiDi detectors and fixers following skill.md workflow.
    """

    def __init__(self) -> None:
        self.bidi_detector = BiDiDetector()
        self.heb_math_detector = HebMathDetector()
        self.bidi_fixer = BiDiFixer()
        self.heb_math_fixer = HebMathFixer()
        self.tikz_fixer = TikzFixer()

    def run(self, content: str, file_path: str = "", apply_fixes: bool = True) -> BiDiOrchestratorResult:
        """Run full BiDi QA pipeline."""
        result = BiDiOrchestratorResult()
        result.skills_executed = {}
        # Phase 1: Detection
        detect = self._run_detection(content, file_path)
        result.detect_result = detect
        result.skills_executed["qa-BiDi-detect"] = "DONE"
        result.skills_executed["qa-heb-math-detect"] = "DONE"
        # Phase 2: Fixes (if enabled and issues found)
        if apply_fixes and detect.total > 0:
            fix_result = self._run_fixes(content, detect)
            result.fix_result = fix_result
            self._update_fix_statuses(result, detect)
        else:
            result.skills_executed.update({
                "qa-BiDi-fix-text": "SKIP", "qa-BiDi-fix-numbers": "SKIP",
                "qa-heb-math-fix": "SKIP", "qa-BiDi-fix-tikz": "SKIP"
            })
        return result

    def _run_detection(self, content: str, file_path: str) -> BiDiDetectResult:
        """Phase 1: Run all detectors."""
        result = BiDiDetectResult()
        # BiDiDetector - general BiDi issues
        bidi_issues = self.bidi_detector.detect(content, file_path)
        for issue in bidi_issues:
            if issue.rule in ("bidi-english", "bidi-hebrew-in-english"):
                result.text_issues.append(issue)
            elif issue.rule == "bidi-numbers":
                result.number_issues.append(issue)
            elif issue.rule == "bidi-tikz-rtl":
                result.tikz_issues.append(issue)
            elif issue.rule == "bidi-acronym":
                result.acronym_issues.append(issue)
            else:
                result.other_issues.append(issue)
        # HebMathDetector - Hebrew in math mode
        math_issues = self.heb_math_detector.detect(content, file_path)
        result.math_hebrew_issues.extend(math_issues)
        return result

    def _run_fixes(self, content: str, detect: BiDiDetectResult) -> BiDiFixResult:
        """Phase 2: Run applicable fixers."""
        result = BiDiFixResult()
        fixed_content = content
        # Fix text direction issues
        text_issues = detect.text_issues + detect.acronym_issues
        if text_issues:
            fixed_content = self.bidi_fixer.fix(fixed_content, text_issues)
            result.text_fixed = len(text_issues)
        # Fix number issues
        if detect.number_issues:
            fixed_content = self.bidi_fixer.fix(fixed_content, detect.number_issues)
            result.numbers_fixed = len(detect.number_issues)
        # Fix Hebrew in math
        if detect.math_hebrew_issues:
            fixed_content = self.heb_math_fixer.fix(fixed_content, detect.math_hebrew_issues)
            result.math_fixed = len(detect.math_hebrew_issues)
        # Fix TikZ issues
        if detect.tikz_issues:
            fixed_content = self.tikz_fixer.fix(fixed_content, detect.tikz_issues)
            result.tikz_fixed = len(detect.tikz_issues)
        result.content = fixed_content
        return result

    def _update_fix_statuses(self, result: BiDiOrchestratorResult, detect: BiDiDetectResult) -> None:
        """Update skill execution statuses based on what was fixed."""
        result.skills_executed["qa-BiDi-fix-text"] = "DONE" if detect.text_issues or detect.acronym_issues else "SKIP"
        result.skills_executed["qa-BiDi-fix-numbers"] = "DONE" if detect.number_issues else "SKIP"
        result.skills_executed["qa-heb-math-fix"] = "DONE" if detect.math_hebrew_issues else "SKIP"
        result.skills_executed["qa-BiDi-fix-tikz"] = "DONE" if detect.tikz_issues else "SKIP"

    def to_dict(self, result: BiDiOrchestratorResult) -> Dict:
        """Convert to dictionary matching skill.md output format."""
        detect = result.detect_result or BiDiDetectResult()
        fix = result.fix_result
        return {
            "skill": "qa-BiDi", "status": result.status, "verdict": result.verdict,
            "detection_summary": {
                "text_direction_issues": len(detect.text_issues),
                "number_ltr_issues": len(detect.number_issues),
                "math_hebrew_issues": len(detect.math_hebrew_issues),
                "tikz_bidi_issues": len(detect.tikz_issues),
                "acronym_issues": len(detect.acronym_issues),
                "other_issues": len(detect.other_issues),
                "total_issues": detect.total,
            },
            "skills_executed": [
                {"skill": k, "status": v, "issues_fixed": self._count_fixed(k, fix)}
                for k, v in result.skills_executed.items()
            ],
        }

    def _count_fixed(self, skill: str, fix: Optional[BiDiFixResult]) -> int:
        if not fix:
            return 0
        counts = {
            "qa-BiDi-fix-text": fix.text_fixed, "qa-BiDi-fix-numbers": fix.numbers_fixed,
            "qa-heb-math-fix": fix.math_fixed, "qa-BiDi-fix-tikz": fix.tikz_fixed
        }
        return counts.get(skill, 0)
