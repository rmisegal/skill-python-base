"""BC Orchestrator coordinating validators with threading and heartbeat."""

import sqlite3
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

from ..shared.logging import PrintManager, JsonLogger
from ..shared.threading import ResourceManager
from ..infrastructure.coordination.heartbeat import HeartbeatMonitor
from .validators import (
    BCValidatorInterface,
    BCBiDiValidator,
    BCCodeValidator,
    BCTableValidator,
    BCBibValidator,
    BCImageValidator,
    BCCoverpageValidator,
    ValidationResult,
)
from .validators.config import BCConfigManager


class BCOrchestrator:
    """Orchestrates BC validators with threading, heartbeat, and logging."""

    def __init__(
        self, project_path: str | Path, config_path: Optional[str | Path] = None
    ) -> None:
        self._project_path = Path(project_path)
        self._agent_id = f"bc-{uuid.uuid4().hex[:8]}"
        self._lock = threading.Lock()
        self._config = BCConfigManager()

        if config_path:
            self._config.load(config_path)
        elif (self._project_path / "bc_pipeline.json").exists():
            self._config.load(self._project_path / "bc_pipeline.json")

        self._logger = PrintManager()
        self._json_logger = JsonLogger()
        self._resource_manager = ResourceManager()

        db_path = self._project_path / ".bc_coordination.db"
        self._init_db(db_path)
        self._heartbeat = HeartbeatMonitor(
            db_path=db_path,
            stale_timeout=self._config.get("orchestration.stale_timeout", 120),
            check_interval=self._config.get("orchestration.heartbeat_interval", 30),
        )

        # All validators matching QA families
        self._validators: Dict[str, BCValidatorInterface] = {
            "BCBiDiValidator": BCBiDiValidator(),
            "BCCodeValidator": BCCodeValidator(),
            "BCTableValidator": BCTableValidator(),
            "BCBibValidator": BCBibValidator(),
            "BCImageValidator": BCImageValidator(),
            "BCCoverpageValidator": BCCoverpageValidator(),
        }
        self._max_workers = self._config.get("orchestration.max_workers", 4)

    def _init_db(self, db_path: Path) -> None:
        """Initialize database schema for heartbeat tracking."""
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("""CREATE TABLE IF NOT EXISTS qa_heartbeat (
                agent_id TEXT PRIMARY KEY, last_seen TEXT, current_task TEXT)""")
            conn.commit()
        finally:
            conn.close()

    def validate(
        self, content: str, validators: Optional[List[str]] = None, file_path: str = "inline"
    ) -> Dict[str, ValidationResult]:
        """Validate content with specified validators."""
        self._heartbeat.update_heartbeat(self._agent_id, f"Validating {file_path}")

        if validators is None:
            validators = [n for n, v in self._validators.items() if v.enabled]

        if self._config.get("performance.parallel_validation", True):
            return self._validate_parallel(content, validators, file_path)
        return self._validate_sequential(content, validators, file_path)

    def _validate_parallel(
        self, content: str, validators: List[str], file_path: str
    ) -> Dict[str, ValidationResult]:
        results: Dict[str, ValidationResult] = {}
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {
                executor.submit(self._run_validator, n, content, file_path): n
                for n in validators if n in self._validators
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    self._logger.error(f"Validator {name} failed: {e}")
        return results

    def _validate_sequential(
        self, content: str, validators: List[str], file_path: str
    ) -> Dict[str, ValidationResult]:
        return {
            n: self._run_validator(n, content, file_path)
            for n in validators if n in self._validators
        }

    def _run_validator(self, name: str, content: str, file_path: str) -> ValidationResult:
        with self._resource_manager.locked(f"validator:{name}", self._agent_id, 60.0):
            self._heartbeat.update_heartbeat(self._agent_id, f"Running {name}")
            return self._validators[name].validate_and_fix(content, file_path)

    def validate_and_fix(
        self, content: str, validators: Optional[List[str]] = None, file_path: str = "inline"
    ) -> tuple[str, Dict[str, ValidationResult]]:
        """Validate and auto-fix content. Returns (fixed_content, results)."""
        results = self.validate(content, validators, file_path)
        fixed = content
        for result in results.values():
            if result.content != content:
                fixed = result.content
        return fixed, results

    def cleanup(self) -> None:
        self._heartbeat.stop_watchdog()
        self._heartbeat.remove_agent(self._agent_id)
