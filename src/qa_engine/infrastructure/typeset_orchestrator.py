"""
Typeset orchestrator (Level 1) - coordinates all typeset QA components.

Matches qa-typeset skill.md workflow:
1. Compile - (external) generate .log file
2. Detect - parse .log for warnings
3. Fix - apply appropriate fixes
4. Verify - (external) re-compile
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..typeset.detection import FullTypesetDetector, TypesetDetectResult
from ..typeset.fixing import HboxFixer, HboxFixResult, VboxFixer, VboxFixResult
from ..infrastructure.fixing.float_fixer import FloatFixer, FloatFixResult


@dataclass
class TypesetOrchestratorResult:
    """Result from typeset orchestration."""
    status: str = "DONE"
    verdict: str = "PASS"
    detect_result: Optional[TypesetDetectResult] = None
    hbox_result: Optional[HboxFixResult] = None
    vbox_result: Optional[VboxFixResult] = None
    float_result: Optional[FloatFixResult] = None
    fixed_content: str = ""
    llm_prompts: List[str] = field(default_factory=list)

    @property
    def total_detected(self) -> int:
        if not self.detect_result:
            return 0
        dr = self.detect_result
        return (len(dr.overfull_hbox) + len(dr.underfull_hbox) +
                len(dr.overfull_vbox) + len(dr.underfull_vbox) +
                len(dr.undefined_references) + len(dr.undefined_citations) +
                len(dr.float_too_large) + len(dr.tikz_overflow_risk))

    @property
    def total_fixed(self) -> int:
        total = 0
        if self.hbox_result:
            total += len(self.hbox_result.fixes_applied)
        if self.vbox_result:
            total += len(self.vbox_result.fixes_applied)
        if self.float_result:
            total += self.float_result.fixes_applied
        return total

    @property
    def manual_review_count(self) -> int:
        count = 0
        if self.hbox_result:
            count += len(self.hbox_result.manual_review)
        if self.vbox_result:
            count += len(self.vbox_result.manual_review)
        if self.float_result:
            count += len(self.float_result.llm_required)
        return count


class TypesetOrchestrator:
    """
    Level 1 typeset family orchestrator.

    Coordinates:
    - FullTypesetDetector (detection from logs + TikZ + itemsep)
    - HboxFixer (auto-fix + manual_review)
    - VboxFixer (raggedbottom, vfill, enlargethispage)
    - FloatFixer (deterministic patterns + LLM for splitting)
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.detector = FullTypesetDetector(project_root=self.project_root)
        self.hbox_fixer = HboxFixer()
        self.vbox_fixer = VboxFixer()
        self.float_fixer = FloatFixer()

    def run(self, log_content: str = "", tex_content: str = "", file_path: str = "",
            apply_fixes: bool = True) -> TypesetOrchestratorResult:
        """Run full typeset QA pipeline."""
        result = TypesetOrchestratorResult(fixed_content=tex_content)
        # Phase 1: Detection
        result.detect_result = self._detect(log_content, file_path)
        result.verdict = result.detect_result.verdict if result.detect_result else "PASS"
        if not apply_fixes or result.total_detected == 0:
            return result
        # Phase 2: Apply fixes
        result = self._apply_fixes(tex_content, file_path, result)
        return result

    def run_from_files(self, log_path: Path, tex_path: Path, apply_fixes: bool = True,
                       preamble_path: Optional[Path] = None) -> TypesetOrchestratorResult:
        """Run from file paths."""
        log_content = log_path.read_text(encoding="utf-8", errors="ignore") if log_path.exists() else ""
        tex_content = tex_path.read_text(encoding="utf-8", errors="ignore") if tex_path.exists() else ""
        result = TypesetOrchestratorResult(fixed_content=tex_content)
        # Detection with file paths
        result.detect_result = self.detector.detect(
            log_path=log_path, tex_files=[tex_path] if tex_path.exists() else None,
            preamble_path=preamble_path
        )
        result.verdict = result.detect_result.verdict if result.detect_result else "PASS"
        if not apply_fixes or result.total_detected == 0:
            return result
        result = self._apply_fixes(tex_content, str(tex_path), result)
        if result.fixed_content != tex_content:
            tex_path.write_text(result.fixed_content, encoding="utf-8")
        return result

    def _detect(self, log_content: str, file_path: str) -> TypesetDetectResult:
        """Run detection phase."""
        from ..infrastructure.detection.typeset_detector import TypesetDetector
        basic_detector = TypesetDetector()
        issues = basic_detector.detect(log_content, file_path)
        # Convert to TypesetDetectResult
        result = TypesetDetectResult(log_file=file_path)
        for issue in issues:
            self._add_issue_to_result(issue, result)
        return result

    def _add_issue_to_result(self, issue, result: TypesetDetectResult) -> None:
        """Add Issue to TypesetDetectResult."""
        from ..typeset.detection.typeset_models import (
            HboxWarning, VboxWarning, UndefinedReference, UndefinedCitation, FloatTooLarge
        )
        rule = issue.rule
        if rule == "typeset-overfull-hbox":
            result.overfull_hbox.append(HboxWarning(
                type="overfull", amount_pt=self._extract_pt(issue.content),
                lines=[issue.line], context=issue.content, severity="WARNING"
            ))
        elif rule == "typeset-underfull-hbox":
            result.underfull_hbox.append(HboxWarning(
                type="underfull", badness=self._extract_badness(issue.content),
                lines=[issue.line], context=issue.content, severity="INFO"
            ))
        elif rule == "typeset-overfull-vbox":
            result.overfull_vbox.append(VboxWarning(
                type="overfull", amount_pt=self._extract_pt(issue.content),
                context=issue.content, severity="CRITICAL"
            ))
        elif rule == "typeset-underfull-vbox":
            result.underfull_vbox.append(VboxWarning(
                type="underfull", badness=self._extract_badness(issue.content),
                context=issue.content, severity="WARNING"
            ))
        elif rule == "typeset-undefined-ref":
            result.undefined_references.append(UndefinedReference(
                reference=issue.content, page=0, input_line=issue.line, severity="CRITICAL"
            ))
        elif rule == "typeset-undefined-citation":
            result.undefined_citations.append(UndefinedCitation(
                citation=issue.content, page=0, input_line=issue.line, severity="CRITICAL"
            ))
        elif rule == "typeset-float-too-large":
            result.float_too_large.append(FloatTooLarge(
                overflow_pt=issue.context.get("overflow_pt", 0) if issue.context else 0,
                input_line=issue.line, severity="CRITICAL"
            ))

    def _extract_pt(self, content: str) -> float:
        import re
        m = re.search(r"(\d+\.?\d*)pt", content)
        return float(m.group(1)) if m else 0.0

    def _extract_badness(self, content: str) -> int:
        import re
        m = re.search(r"badness (\d+)", content)
        return int(m.group(1)) if m else 0

    def _apply_fixes(self, content: str, file_path: str,
                     result: TypesetOrchestratorResult) -> TypesetOrchestratorResult:
        """Apply all fixes."""
        fixed = content
        dr = result.detect_result
        # Hbox fixes
        if dr and (dr.overfull_hbox or dr.underfull_hbox):
            issues = [{"line": w.lines[0] if w.lines else 0, "type": w.type}
                      for w in dr.overfull_hbox + dr.underfull_hbox if w.lines]
            fixed, result.hbox_result = self.hbox_fixer.fix_content(fixed, file_path, issues)
            for r in result.hbox_result.manual_review:
                result.llm_prompts.append(self.hbox_fixer.generate_llm_prompt(r))
        # Vbox fixes
        if dr and (dr.overfull_vbox or dr.underfull_vbox):
            fixed, result.vbox_result = self.vbox_fixer.fix_preamble(fixed, file_path)
            for vb in dr.underfull_vbox:
                review = self.vbox_fixer.create_review(file_path, 0, "underfull", vb.badness)
                if result.vbox_result:
                    result.vbox_result.manual_review.append(review)
                    result.llm_prompts.append(self.vbox_fixer.generate_llm_prompt(review))
        # Float fixes
        if dr and dr.float_too_large:
            overflow = dr.float_too_large[0].overflow_pt if dr.float_too_large else 0
            fixed, result.float_result = self.float_fixer.fix_content(fixed, file_path, overflow)
            for llm in result.float_result.llm_required:
                result.llm_prompts.append(f"Float fix needed: {llm.get('suggestion', '')}")
        result.fixed_content = fixed
        result.verdict = "PASS" if result.manual_review_count == 0 else "WARNING"
        return result

    def to_dict(self, result: TypesetOrchestratorResult) -> Dict[str, Any]:
        """Convert to dictionary matching skill.md output format."""
        return {
            "skill": "qa-typeset", "status": result.status, "verdict": result.verdict,
            "detection": self.detector.to_dict(result.detect_result) if result.detect_result else None,
            "fixes": {
                "hbox": self.hbox_fixer.to_dict(result.hbox_result) if result.hbox_result else None,
                "vbox": self.vbox_fixer.to_dict(result.vbox_result) if result.vbox_result else None,
                "float": {"fixes_applied": result.float_result.fixes_applied,
                          "llm_required": result.float_result.llm_required} if result.float_result else None,
            },
            "summary": {
                "total_detected": result.total_detected, "total_fixed": result.total_fixed,
                "manual_review": result.manual_review_count, "llm_prompts_count": len(result.llm_prompts),
            },
        }
