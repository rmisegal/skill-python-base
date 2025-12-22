"""Infrastructure family orchestrator (Level 1). Coordinates infra scan and reorganize."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from .detection.infra_scanner import InfraScanner, ScanResult
from .fixing.infra_reorganizer import InfraReorganizer, ReorganizeResult


@dataclass
class InfraOrchestratorResult:
    """Combined orchestration result for infra QA."""
    scan_result: Optional[ScanResult] = None
    reorg_result: Optional[ReorganizeResult] = None
    skills_executed: Dict[str, str] = field(default_factory=dict)

    @property
    def total_issues(self) -> int:
        if self.scan_result:
            return self.scan_result.misplaced + len(self.scan_result.missing_dirs)
        return 0

    @property
    def total_fixed(self) -> int:
        if self.reorg_result:
            return self.reorg_result.files_moved + len(self.reorg_result.directories_created)
        return 0

    @property
    def verdict(self) -> str:
        if self.total_issues > 0 and self.total_fixed < self.total_issues:
            return "WARNING"
        return "PASS"

    @property
    def status(self) -> str:
        return "DONE"


class InfraOrchestrator:
    """Level 1 family orchestrator for Infrastructure QA."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.scanner = InfraScanner(project_root=self.project_root)
        self.reorganizer = InfraReorganizer(project_root=self.project_root)

    def run(self, apply_fixes: bool = True) -> InfraOrchestratorResult:
        """Run full Infrastructure QA pipeline."""
        result = InfraOrchestratorResult()
        result.skills_executed = {}
        # Phase 1: Scan
        scan = self.scanner.scan()
        result.scan_result = scan
        result.skills_executed["qa-infra-scan"] = "DONE"
        # Phase 2: Reorganize
        if apply_fixes and scan.misplaced > 0:
            misplaced_list = [{"file": f.file, "current": f.current, "target": f.target,
                              "reason": f.reason} for f in scan.misplaced_files]
            reorg = self.reorganizer.reorganize(misplaced_list)
            result.reorg_result = reorg
            result.skills_executed["qa-infra-reorganize"] = "DONE"
        else:
            result.skills_executed["qa-infra-reorganize"] = "SKIP"
        return result

    def to_dict(self, result: InfraOrchestratorResult) -> Dict:
        """Convert to dictionary."""
        scan = result.scan_result or ScanResult()
        reorg = result.reorg_result
        return {
            "family": "infra", "status": result.status, "verdict": result.verdict,
            "scan": {"dirs_required": scan.required_dirs, "dirs_present": scan.present_dirs,
                    "missing_dirs": scan.missing_dirs, "files_total": scan.total_files,
                    "files_misplaced": scan.misplaced},
            "reorganize": {"dirs_created": reorg.directories_created if reorg else [],
                          "files_moved": reorg.files_moved if reorg else 0},
            "skills_executed": list(result.skills_executed.items()),
        }
