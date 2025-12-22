"""
QA Controller - main entry point for the QA system.

Implements FR-104 from PRD - orchestrates QA execution.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.interfaces import DetectorInterface, FixerInterface
from ..domain.models.issue import Issue
from ..domain.models.status import QAStatus
from ..domain.services.document_analyzer import DocumentAnalyzer
from ..infrastructure.coordination.coordinator import Coordinator
from ..infrastructure.detection import (
    BiDiDetector, CodeDetector, TypesetDetector, TableDetector, BibDetector
)
from ..infrastructure.fixing import (
    BiDiFixer, CodeFixer, TableFixer, BibFixer, TikzFixer
)
from ..shared.config import ConfigManager
from ..shared.logging import JsonLogger
from .executor import QAExecutor


class QAController:
    """
    Main controller for QA execution.

    Orchestrates detection and fixing operations according to
    configuration. Implements FR-104 acceptance criteria.
    """

    def __init__(
        self,
        project_path: str | Path,
        config_path: Optional[str | Path] = None,
    ) -> None:
        self._project_path = Path(project_path)
        self._config = ConfigManager()
        self._logger = JsonLogger()
        self._coordinator: Optional[Coordinator] = None

        if config_path:
            self._config.load(config_path)
        elif (self._project_path / "qa_setup.json").exists():
            self._config.load(self._project_path / "qa_setup.json")

        self._setup_logging()
        self._setup_coordinator()
        self._detectors: Dict[str, DetectorInterface] = {
            "BiDi": BiDiDetector(),
            "code": CodeDetector(),
            "table": TableDetector(),
            "bib": BibDetector(),
            "typeset": TypesetDetector(),
        }
        self._fixers: Dict[str, FixerInterface] = {
            "BiDi": BiDiFixer(),
            "code": CodeFixer(),
            "table": TableFixer(),
            "bib": BibFixer(),
        }
        self._executor = QAExecutor(
            self._detectors, self._logger, self._project_path,
            self._config.get_int("batch_processing.max_workers", 4),
            fixers=self._fixers,
        )

    def _setup_logging(self) -> None:
        """Configure logging."""
        log_dir = self._project_path / self._config.get_str("logging.log_dir", "qa-logs")
        self._logger.configure(log_dir, self._config.get_str("logging.level", "INFO"))

    def _setup_coordinator(self) -> None:
        """Set up coordination database."""
        db_path = self._project_path / ".qa_coordination.db"
        self._coordinator = Coordinator(db_path)

    def run(self, agent_id: Optional[str] = None) -> QAStatus:
        """Run full QA pipeline."""
        agent_id = agent_id or f"qa-{uuid.uuid4().hex[:8]}"
        run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        status = QAStatus(
            run_id=run_id,
            project_path=str(self._project_path),
            started_at=datetime.now(),
        )
        self._logger.log_event("QA_START", agent_id, run_id=run_id)

        analyzer = DocumentAnalyzer()
        metrics = analyzer.analyze(self._project_path)
        self._logger.log_event(
            "DOCUMENT_ANALYZED", agent_id,
            total_lines=metrics.total_lines,
            strategy=metrics.recommended_strategy.value,
        )

        families = self._config.get("enabled_families", ["BiDi", "code"])
        parallel = self._config.get_bool("parallel_families", True)

        if parallel:
            all_issues = self._executor.run_parallel(families, agent_id, status)
        else:
            all_issues = self._executor.run_sequential(families, agent_id, status)

        status.completed_at = datetime.now()
        self._logger.log_event(
            "QA_COMPLETE", agent_id,
            total_issues=len(all_issues),
            duration_seconds=(status.completed_at - status.started_at).total_seconds(),
        )
        return status

    def detect(self, family: str, content: str, file_path: str) -> List[Issue]:
        """Run detection for specific family on content."""
        detector = self._detectors.get(family)
        return detector.detect(content, file_path) if detector else []

    def get_status(self) -> Dict[str, Any]:
        """Get current execution status from coordinator."""
        return {"status": self._coordinator.get_all_status() if self._coordinator else []}

    def cleanup(self) -> None:
        """Clean up resources."""
        if self._coordinator:
            self._coordinator.cleanup()
