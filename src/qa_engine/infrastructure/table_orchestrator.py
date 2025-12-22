"""Table family orchestrator (Level 1). Coordinates table detection and fixing."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from ..table.detection.table_layout_detector import TableLayoutDetector
from ..table.detection.table_models import TableDetectResult
from ..infrastructure.fixing.table_fixer import TableFixer


@dataclass
class TableOrchestratorResult:
    """Combined orchestration result for table QA."""
    detect_result: Optional[TableDetectResult] = None
    total_issues: int = 0
    total_fixed: int = 0
    skills_executed: Dict[str, str] = field(default_factory=dict)

    @property
    def verdict(self) -> str:
        if self.total_issues > 0 and self.total_fixed < self.total_issues:
            return "WARNING"
        return "PASS"

    @property
    def status(self) -> str:
        return "DONE"


class TableOrchestrator:
    """Level 1 family orchestrator for Table QA."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.detector = TableLayoutDetector(project_root=self.project_root)
        self.fixer = TableFixer()

    def run(self, content: str, file_path: str = "", apply_fixes: bool = True) -> TableOrchestratorResult:
        """Run full Table QA pipeline."""
        result = TableOrchestratorResult()
        result.skills_executed = {}
        # Phase 1: Detection
        detect = self.detector.detect_content(content, file_path)
        result.detect_result = detect
        result.total_issues = detect.issues_found
        result.skills_executed["qa-table-detect"] = "DONE"
        # Phase 2: Fixes
        if apply_fixes and detect.issues_found > 0:
            fixed_content, fixes = self._run_fixes(content, detect)
            result.total_fixed = fixes
            result.skills_executed["qa-table-fix"] = "DONE" if fixes > 0 else "SKIP"
        else:
            result.skills_executed["qa-table-fix"] = "SKIP"
        return result

    def _run_fixes(self, content: str, detect: TableDetectResult) -> tuple:
        """Phase 2: Run table fixes using Issue-based API."""
        from ..domain.models.issue import Issue, Severity
        fixes = 0
        fixed_content = content
        issues = []
        for detail in detect.details:
            if "column_order" in detail.issue_type:
                issues.append(Issue(rule="table-plain-unstyled", file="", line=detail.line,
                                   content="", severity=Severity.WARNING))
                fixes += 1
        if issues:
            fixed_content = self.fixer.fix(fixed_content, issues)
        return fixed_content, fixes

    def to_dict(self, result: TableOrchestratorResult) -> Dict:
        """Convert to dictionary."""
        detect = result.detect_result or TableDetectResult()
        return {
            "family": "table", "status": result.status, "verdict": result.verdict,
            "detection": {"tables_found": detect.tables_found, "issues": detect.issues_found,
                         "caption": detect.caption_alignment_issues,
                         "column": detect.column_order_issues, "cell": detect.cell_alignment_issues},
            "fixes": {"total_fixed": result.total_fixed},
            "skills_executed": list(result.skills_executed.items()),
        }
