"""
QA Super Controller - enhanced controller matching qa-super skill.md.

Adds CLS version checking, detection verification, and QA-REPORT.md generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from ..domain.models.issue import Issue
from ..domain.models.status import QAStatus
from ..infrastructure.coordination.detection_verifier import DetectionVerifier
from ..infrastructure.detection.cls_detector import CLSDetector
from ..infrastructure.fixing.cls_fixer import CLSFixer
from ..infrastructure.fixing.cls_tex_updater import CLSTexUpdater
from ..infrastructure.reporting.qa_super_formatter import (
    QASuperFormatter, QASuperReport, CLSCheckResult, FamilyResult,
)
from .controller import QAController


class QASuperController(QAController):
    """
    Enhanced QA controller matching qa-super skill.md workflow.

    Adds:
    - Phase 0: CLS version check (blocking)
    - Detection verification
    - QA-REPORT.md generation
    """

    def __init__(self, project_path: str | Path, config_path: Optional[str | Path] = None) -> None:
        super().__init__(project_path, config_path)
        self._cls_detector = CLSDetector()
        self._cls_fixer = CLSFixer()
        self._cls_tex_updater = CLSTexUpdater()
        self._detection_verifier = DetectionVerifier()
        self._report_formatter = QASuperFormatter()
        self._cls_check_result: Optional[CLSCheckResult] = None

    def run(self, agent_id: Optional[str] = None) -> QAStatus:
        """Run full QA pipeline with Phase 0 CLS check."""
        # Phase 0: CLS Version Check (BLOCKING)
        cls_ok = self._run_cls_check()
        if not cls_ok:
            self._logger.log_event("CLS_CHECK_BLOCKED", agent_id or "unknown")

        # Clear detection verifier for new run
        self._detection_verifier.clear()

        # Run standard pipeline
        status = super().run(agent_id)

        # Verify detection ran for all families
        self._verify_detections(status)

        return status

    def _run_cls_check(self) -> bool:
        """Run Phase 0 CLS version check."""
        cls_files = list(self._project_path.rglob("*.cls"))
        if not cls_files:
            self._cls_check_result = CLSCheckResult(status="SKIPPED", action_taken="No CLS file found")
            return True

        for cls_file in cls_files:
            content = cls_file.read_text(encoding="utf-8")
            issues = self._cls_detector.detect(content, str(cls_file))

            if any(i.rule == "cls-version-mismatch" for i in issues):
                # Fix: Copy reference CLS
                fix_result = self._cls_fixer.fix_file(cls_file)
                if fix_result.success:
                    # Update .tex files to use new CLS
                    update_report = self._cls_tex_updater.update_project(self._project_path)
                    self._cls_check_result = CLSCheckResult(
                        status="FIXED",
                        version=fix_result.new_version or "",
                        action_taken=f"Updated CLS and {update_report.files_updated} .tex files",
                    )
                else:
                    self._cls_check_result = CLSCheckResult(
                        status="FAILED", action_taken=fix_result.message,
                    )
                    return False
            else:
                self._cls_check_result = CLSCheckResult(status="CURRENT")

        return True

    def _verify_detections(self, status: QAStatus) -> None:
        """Verify detection ran for all families."""
        families = self._config.get("enabled_families", ["BiDi", "code"])
        for family in families:
            if family in status.entries:
                entry = status.entries[family]
                self._detection_verifier.record_detection(
                    detector_name=f"{family}Detector",
                    files_scanned=len(list(self._project_path.rglob("*.tex"))),
                    issues_found=entry.issues_found,
                )

    def generate_report(self, status: QAStatus, issues: List[Issue]) -> str:
        """Generate QA-REPORT.md content."""
        report = self._report_formatter.from_status(
            status, issues, self._project_path.name,
        )
        report.cls_check = self._cls_check_result

        # Add verification status to family results
        for family_result in report.families:
            verification = self._detection_verifier.verify_family(family_result.family)
            family_result.detection_verified = verification.is_verified

        return self._report_formatter.format(report)

    def save_report(self, status: QAStatus, issues: List[Issue]) -> Path:
        """Generate and save QA-REPORT.md."""
        content = self.generate_report(status, issues)
        report_path = self._project_path / "QA-REPORT.md"
        report_path.write_text(content, encoding="utf-8")
        return report_path

    def get_verification_report(self) -> dict:
        """Get detection verification status."""
        return self._detection_verifier.get_verification_report()
