"""
Execution logic for QA operations.

Handles parallel and sequential execution of detection and fixing families.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..domain.interfaces import DetectorInterface, FixerInterface
from ..domain.models.issue import Issue
from ..domain.models.status import QAStatus
from ..shared.config import ConfigManager
from ..shared.logging import JsonLogger, LogLevel


class QAExecutor:
    """Executes detection and fixing families in parallel or sequential mode."""

    def __init__(
        self,
        detectors: Dict[str, DetectorInterface],
        logger: JsonLogger,
        project_path: Path,
        max_workers: int = 4,
        fixers: Optional[Dict[str, FixerInterface]] = None,
    ) -> None:
        self._detectors = detectors
        self._fixers = fixers or {}
        self._logger = logger
        self._project_path = project_path
        self._max_workers = max_workers
        self._config = ConfigManager()

    def run_parallel(
        self,
        families: List[str],
        agent_id: str,
        status: QAStatus,
    ) -> List[Issue]:
        """Run families in parallel using thread pool."""
        all_issues: List[Issue] = []

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {
                executor.submit(self._run_family, family, agent_id): family
                for family in families
                if family in self._detectors
            }

            for future in as_completed(futures):
                family = futures[future]
                try:
                    issues = future.result()
                    all_issues.extend(issues)
                    status.mark_completed(family, len(issues))
                except Exception as e:
                    status.mark_failed(family, str(e))
                    self._logger.log(
                        LogLevel.ERROR, "FAMILY_ERROR", agent_id,
                        family=family, error=str(e),
                    )

        return all_issues

    def run_sequential(
        self,
        families: List[str],
        agent_id: str,
        status: QAStatus,
    ) -> List[Issue]:
        """Run families sequentially."""
        all_issues: List[Issue] = []

        for family in families:
            if family not in self._detectors:
                continue

            status.mark_started(family, agent_id)
            try:
                issues = self._run_family(family, agent_id)
                all_issues.extend(issues)
                status.mark_completed(family, len(issues))
            except Exception as e:
                status.mark_failed(family, str(e))

        return all_issues

    def _run_family(self, family: str, agent_id: str) -> List[Issue]:
        """Run detection for a single family."""
        detector = self._detectors.get(family)
        if not detector:
            return []

        self._logger.log_event("SKILL_START", agent_id, skill=family)
        all_issues: List[Issue] = []
        tex_files = list(self._project_path.rglob("*.tex"))

        # Get family config for auto_fix rules
        family_config = self._config.get(f"families.{family}", {})
        rules_config = family_config.get("rules", {})
        auto_fix_enabled = self._config.get_bool("auto_fix", False)

        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding="utf-8", errors="ignore")
                issues = detector.detect(content, str(tex_file))

                # Filter issues by enabled rules
                enabled_issues = [
                    i for i in issues
                    if rules_config.get(i.rule, {}).get("enabled", True)
                ]
                all_issues.extend(enabled_issues)

                # Apply fixes if auto_fix enabled
                if auto_fix_enabled and enabled_issues:
                    fixed_content = self._apply_fixes(
                        family, content, enabled_issues, str(tex_file), rules_config
                    )
                    if fixed_content != content:
                        tex_file.write_text(fixed_content, encoding="utf-8")
                        self._logger.log_event(
                            "FILE_FIXED", agent_id,
                            file=str(tex_file), fixes=len(enabled_issues),
                        )
            except Exception:
                continue

        self._logger.log_event(
            "SKILL_COMPLETE", agent_id,
            skill=family, issues_count=len(all_issues),
        )
        return all_issues

    def _apply_fixes(
        self,
        family: str,
        content: str,
        issues: List[Issue],
        file_path: str,
        rules_config: Dict,
    ) -> str:
        """Apply fixes for issues that have auto_fix enabled."""
        fixer = self._fixers.get(family)
        if not fixer:
            return content

        # Filter to only auto_fix enabled issues
        fixable = [
            i for i in issues
            if rules_config.get(i.rule, {}).get("auto_fix", False)
        ]
        if not fixable:
            return content

        return fixer.fix(content, fixable)
