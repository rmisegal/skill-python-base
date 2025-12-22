"""Super orchestrator (Level 0) - coordinates all QA family orchestrators."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..domain.services.document_analyzer import DocumentAnalyzer, DocumentMetrics
from ..shared.config import ConfigManager
from ..bibliography.bib_orchestrator import BibOrchestrator
from .bidi_orchestrator import BiDiOrchestrator
from .code_orchestrator import CodeOrchestrator
from .image_orchestrator import ImageOrchestrator
from .table_orchestrator import TableOrchestrator
from .infra_orchestrator import InfraOrchestrator
from .typeset_orchestrator import TypesetOrchestrator
from .family_handlers import HANDLERS


@dataclass
class FamilyResult:
    """Result from a single family orchestrator."""
    family: str
    status: str = "DONE"
    verdict: str = "PASS"
    issues_found: int = 0
    issues_fixed: int = 0
    error: Optional[str] = None


@dataclass
class SuperOrchestratorResult:
    """Combined result from all families."""
    run_id: str = ""
    project_path: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    families_run: List[str] = field(default_factory=list)
    family_results: Dict[str, FamilyResult] = field(default_factory=dict)
    document_metrics: Optional[DocumentMetrics] = None

    @property
    def total_issues(self) -> int:
        return sum(r.issues_found for r in self.family_results.values())

    @property
    def total_fixed(self) -> int:
        return sum(r.issues_fixed for r in self.family_results.values())

    @property
    def verdict(self) -> str:
        if any(r.verdict == "FAIL" for r in self.family_results.values()):
            return "FAIL"
        return "WARNING" if any(r.verdict == "WARNING" for r in self.family_results.values()) else "PASS"

    @property
    def status(self) -> str:
        return "DONE"


class SuperOrchestrator:
    """Level 0 super orchestrator - coordinates all QA families."""

    def __init__(self, project_path: Optional[Path] = None, config_path: Optional[Path] = None) -> None:
        self.project_path = project_path or Path.cwd()
        self.config = ConfigManager()
        if config_path and config_path.exists():
            self.config.load(config_path)
        elif (self.project_path / "qa_setup.json").exists():
            self.config.load(self.project_path / "qa_setup.json")
        self.analyzer = DocumentAnalyzer()
        self._orchestrators = {
            "BiDi": BiDiOrchestrator(), "bib": BibOrchestrator(project_root=self.project_path),
            "code": CodeOrchestrator(), "img": ImageOrchestrator(project_root=self.project_path),
            "infra": InfraOrchestrator(project_root=self.project_path),
            "table": TableOrchestrator(project_root=self.project_path),
            "typeset": TypesetOrchestrator(project_root=self.project_path),
        }

    def run(self, content: str = "", file_path: str = "", families: List[str] = None,
            apply_fixes: bool = True) -> SuperOrchestratorResult:
        """Run full QA pipeline on content or project."""
        result = SuperOrchestratorResult(run_id=f"run-{uuid.uuid4().hex[:8]}",
                                         project_path=str(self.project_path), started_at=datetime.now())
        enabled = families or self.config.get("enabled_families", ["BiDi", "img"])
        result.families_run = [f for f in enabled if f in self._orchestrators]
        if self.project_path.exists():
            result.document_metrics = self.analyzer.analyze(self.project_path)
        for family in result.families_run:
            result.family_results[family] = self._run_family(family, content, file_path, apply_fixes)
        result.completed_at = datetime.now()
        return result

    def run_on_project(self, families: List[str] = None, apply_fixes: bool = True) -> SuperOrchestratorResult:
        """Run QA on all .tex files in project."""
        result = SuperOrchestratorResult(run_id=f"run-{uuid.uuid4().hex[:8]}",
                                         project_path=str(self.project_path), started_at=datetime.now())
        enabled = families or self.config.get("enabled_families", ["BiDi", "img"])
        result.families_run = [f for f in enabled if f in self._orchestrators]
        result.document_metrics = self.analyzer.analyze(self.project_path)
        tex_files = list(self.project_path.rglob("*.tex"))
        for family in result.families_run:
            agg = FamilyResult(family=family)
            for tex_file in tex_files:
                try:
                    content = tex_file.read_text(encoding="utf-8", errors="ignore")
                    fr = self._run_family(family, content, str(tex_file), apply_fixes)
                    agg.issues_found += fr.issues_found
                    agg.issues_fixed += fr.issues_fixed
                    if fr.verdict == "FAIL":
                        agg.verdict = "FAIL"
                except Exception as e:
                    agg.error = str(e)
            result.family_results[family] = agg
        result.completed_at = datetime.now()
        return result

    def _run_family(self, family: str, content: str, file_path: str, apply_fixes: bool) -> FamilyResult:
        """Run a single family orchestrator."""
        result = FamilyResult(family=family)
        orchestrator = self._orchestrators.get(family)
        if not orchestrator:
            result.status = "SKIP"
            return result
        try:
            handler = HANDLERS.get(family)
            if handler:
                handler(orchestrator, content, file_path, apply_fixes, result)
        except Exception as e:
            result.status, result.verdict, result.error = "ERROR", "FAIL", str(e)
        return result

    def to_dict(self, result: SuperOrchestratorResult) -> Dict[str, Any]:
        """Convert to dictionary matching qa-super skill.md output format."""
        return {
            "run_id": result.run_id, "status": result.status, "verdict": result.verdict,
            "project_path": result.project_path,
            "started_at": result.started_at.isoformat() if result.started_at else None,
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "families_run": result.families_run, "total_issues": result.total_issues,
            "issues_by_family": {f: r.issues_found for f, r in result.family_results.items()},
            "fixes_by_family": {f: r.issues_fixed for f, r in result.family_results.items()},
            "family_verdicts": {f: r.verdict for f, r in result.family_results.items()},
            "document_metrics": {"total_lines": result.document_metrics.total_lines,
                                "total_files": result.document_metrics.total_files,
                                "strategy": result.document_metrics.recommended_strategy.value,
                                } if result.document_metrics else None,
        }
