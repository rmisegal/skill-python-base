"""Code family orchestrator (Level 1). Coordinates code detection and fixing."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from ..domain.models.issue import Issue
from .detection.code_detector import CodeDetector
from .fixing.code_fixer import CodeFixer


@dataclass
class CodeDetectResult:
    """Detection results from CodeDetector."""
    overflow_issues: List[Issue] = field(default_factory=list)
    hebrew_content_issues: List[Issue] = field(default_factory=list)
    fstring_issues: List[Issue] = field(default_factory=list)
    other_issues: List[Issue] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.overflow_issues) + len(self.hebrew_content_issues) + \
               len(self.fstring_issues) + len(self.other_issues)

    @property
    def verdict(self) -> str:
        return "FAIL" if self.total > 0 else "PASS"


@dataclass
class CodeFixResult:
    """Results from code fix operations."""
    overflow_fixed: int = 0
    hebrew_fixed: int = 0
    content: str = ""


@dataclass
class CodeOrchestratorResult:
    """Combined orchestration result."""
    detect_result: Optional[CodeDetectResult] = None
    fix_result: Optional[CodeFixResult] = None
    skills_executed: Dict[str, str] = field(default_factory=dict)

    @property
    def verdict(self) -> str:
        if self.detect_result and self.detect_result.total > 0:
            fixed = (self.fix_result.overflow_fixed + self.fix_result.hebrew_fixed) if self.fix_result else 0
            return "PASS" if fixed >= self.detect_result.total else "WARNING"
        return "PASS"

    @property
    def status(self) -> str:
        return "DONE"


class CodeOrchestrator:
    """Level 1 family orchestrator for Code QA."""

    def __init__(self) -> None:
        self.detector = CodeDetector()
        self.fixer = CodeFixer()

    def run(self, content: str, file_path: str = "", apply_fixes: bool = True) -> CodeOrchestratorResult:
        """Run full Code QA pipeline."""
        result = CodeOrchestratorResult()
        result.skills_executed = {}
        # Phase 1: Detection
        detect = self._run_detection(content, file_path)
        result.detect_result = detect
        result.skills_executed["qa-code-detect"] = "DONE"
        # Phase 2: Fixes
        if apply_fixes and detect.total > 0:
            fix_result = self._run_fixes(content, detect)
            result.fix_result = fix_result
            result.skills_executed["qa-code-fix-overflow"] = "DONE" if detect.overflow_issues else "SKIP"
            result.skills_executed["qa-code-fix-hebrew"] = "DONE" if detect.hebrew_content_issues else "SKIP"
        else:
            result.skills_executed["qa-code-fix-overflow"] = "SKIP"
            result.skills_executed["qa-code-fix-hebrew"] = "SKIP"
        return result

    def _run_detection(self, content: str, file_path: str) -> CodeDetectResult:
        """Phase 1: Run detection."""
        result = CodeDetectResult()
        issues = self.detector.detect(content, file_path)
        for issue in issues:
            if issue.rule == "code-background-overflow":
                result.overflow_issues.append(issue)
            elif issue.rule == "code-hebrew-content":
                result.hebrew_content_issues.append(issue)
            elif issue.rule == "code-fstring-brace":
                result.fstring_issues.append(issue)
            else:
                result.other_issues.append(issue)
        return result

    def _run_fixes(self, content: str, detect: CodeDetectResult) -> CodeFixResult:
        """Phase 2: Run fixes."""
        result = CodeFixResult()
        fixed_content = content
        # Fix Hebrew content FIRST (before wrapping changes line numbers)
        if detect.hebrew_content_issues:
            fixed_content = self.fixer.fix(fixed_content, detect.hebrew_content_issues)
            result.hebrew_fixed = len(detect.hebrew_content_issues)
        # Fix overflow (wrap in english) LAST
        if detect.overflow_issues:
            fixed_content = self.fixer.fix(fixed_content, detect.overflow_issues)
            result.overflow_fixed = len(detect.overflow_issues)
        result.content = fixed_content
        return result

    def to_dict(self, result: CodeOrchestratorResult) -> Dict:
        """Convert to dictionary."""
        detect = result.detect_result or CodeDetectResult()
        fix = result.fix_result
        return {
            "family": "code", "status": result.status, "verdict": result.verdict,
            "detection": {"overflow": len(detect.overflow_issues),
                         "hebrew_content": len(detect.hebrew_content_issues),
                         "fstring": len(detect.fstring_issues), "total": detect.total},
            "fixes": {"overflow_fixed": fix.overflow_fixed if fix else 0,
                     "hebrew_fixed": fix.hebrew_fixed if fix else 0},
            "skills_executed": list(result.skills_executed.items()),
        }
