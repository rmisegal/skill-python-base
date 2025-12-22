"""
Full typeset detector combining all detection methods.

Implements qa-typeset-detect skill.md v1.5 complete workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .typeset_models import TypesetDetectResult
from .log_warning_detector import LogWarningDetector
from .tikz_detector import TikzDetector
from .itemsep_detector import ItemsepDetector


class FullTypesetDetector:
    """
    Complete typeset detector matching qa-typeset-detect skill.md v1.5.

    Combines:
    - Log warning detection (Step 2)
    - TikZ source analysis (Step 3)
    - Excessive vertical spacing detection (v1.5)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize detector."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.log_detector = LogWarningDetector()
        self.tikz_detector = TikzDetector()
        self.itemsep_detector = ItemsepDetector()

    def detect(
        self,
        log_path: Optional[Path] = None,
        tex_files: Optional[List[Path]] = None,
        preamble_path: Optional[Path] = None,
    ) -> TypesetDetectResult:
        """
        Run full typeset detection.

        Args:
            log_path: Path to .log file
            tex_files: List of .tex files to analyze for TikZ/itemsep
            preamble_path: Path to preamble.tex for raggedbottom check

        Returns:
            TypesetDetectResult with all warnings
        """
        result = TypesetDetectResult()

        # Step 2: Parse log file
        if log_path and log_path.exists():
            result = self.log_detector.detect_log(log_path)

        # Check for raggedbottom in preamble
        if preamble_path and preamble_path.exists():
            preamble_content = preamble_path.read_text(encoding="utf-8", errors="ignore")
            result.has_raggedbottom = self.itemsep_detector.check_raggedbottom(preamble_content)

        # Step 3: TikZ source analysis + v1.5 itemsep detection
        if tex_files:
            for tex_file in tex_files:
                # TikZ detection
                tikz_issues = self.tikz_detector.detect_in_file(tex_file)
                result.tikz_overflow_risk.extend(tikz_issues)

                # v1.5: Itemsep detection
                itemsep_issues = self.itemsep_detector.detect_in_file(
                    tex_file,
                    has_raggedbottom=result.has_raggedbottom,
                    underfull_vbox_count=result.underfull_vbox_count,
                )
                result.itemsep_issues.extend(itemsep_issues)

        return result

    def to_dict(self, result: TypesetDetectResult) -> Dict[str, Any]:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-typeset-detect",
            "status": "DONE",
            "verdict": result.verdict,
            "log_file": result.log_file,
            "warnings": {
                "overfull_hbox": [
                    {"amount_pt": w.amount_pt, "lines": w.lines,
                     "context": w.context, "severity": w.severity}
                    for w in result.overfull_hbox
                ],
                "underfull_hbox": [
                    {"badness": w.badness, "lines": w.lines,
                     "context": w.context, "severity": w.severity}
                    for w in result.underfull_hbox
                ],
                "overfull_vbox": [
                    {"amount_pt": w.amount_pt, "context": w.context, "severity": w.severity}
                    for w in result.overfull_vbox
                ],
                "underfull_vbox": [
                    {"badness": w.badness, "context": w.context, "severity": w.severity}
                    for w in result.underfull_vbox
                ],
                "undefined_references": [
                    {"reference": r.reference, "page": r.page,
                     "input_line": r.input_line, "severity": r.severity}
                    for r in result.undefined_references
                ],
                "undefined_citations": [
                    {"citation": c.citation, "page": c.page,
                     "input_line": c.input_line, "severity": c.severity}
                    for c in result.undefined_citations
                ],
                "float_too_large": [
                    {"overflow_pt": f.overflow_pt, "input_line": f.input_line,
                     "severity": f.severity}
                    for f in result.float_too_large
                ],
                "known_issues": [
                    {"type": k.type, "message": k.message, "cause": k.cause,
                     "severity": k.severity, "affects_output": k.affects_output}
                    for k in result.known_issues
                ],
                "tikz_overflow_risk": [
                    {"file": t.file, "line": t.line, "content": t.content,
                     "issue": t.issue, "severity": t.severity, "fix": t.fix}
                    for t in result.tikz_overflow_risk
                ],
            },
            "summary": self._build_summary(result),
            "triggers": result.triggers,
        }

    def _build_summary(self, result: TypesetDetectResult) -> Dict[str, int]:
        """Build summary counts."""
        all_items = (
            result.overfull_hbox + result.underfull_hbox +
            result.overfull_vbox + result.underfull_vbox +
            result.undefined_references + result.undefined_citations +
            result.float_too_large + result.known_issues +
            result.tikz_overflow_risk
        )
        return {
            "overfull_hbox": len(result.overfull_hbox),
            "underfull_hbox": len(result.underfull_hbox),
            "overfull_vbox": len(result.overfull_vbox),
            "underfull_vbox": len(result.underfull_vbox),
            "undefined_references": len(result.undefined_references),
            "undefined_citations": len(result.undefined_citations),
            "float_too_large": len(result.float_too_large),
            "known_issues": len(result.known_issues),
            "tikz_overflow_risk": len(result.tikz_overflow_risk),
            "total": len(all_items),
            "critical": sum(1 for i in all_items if getattr(i, "severity", "") == "CRITICAL"),
            "warnings": sum(1 for i in all_items if getattr(i, "severity", "") == "WARNING"),
            "info": sum(1 for i in all_items if getattr(i, "severity", "") == "INFO"),
        }

    def get_rules(self) -> Dict[str, str]:
        """Return detection rules."""
        return {
            "overfull_hbox_critical": "Overfull hbox > 10pt",
            "overfull_hbox_warning": "Overfull hbox 1-10pt",
            "overfull_hbox_info": "Overfull hbox < 1pt",
            "underfull_hbox_warning": "Underfull hbox badness >= 10000",
            "overfull_vbox_critical": "Overfull vbox any",
            "underfull_vbox_warning": "Underfull vbox badness >= 10000",
            "undefined_ref_critical": "Undefined reference",
            "undefined_citation_critical": "Undefined citation",
            "float_large_critical": "Float too large > 50pt",
            "float_large_warning": "Float too large <= 50pt",
            "tikz_no_constraint_warning": "TikZ no width constraint",
            "tikz_large_coords_critical": "TikZ large coordinates (>10)",
        }
