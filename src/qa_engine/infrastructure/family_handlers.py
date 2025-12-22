"""Family-specific handlers for SuperOrchestrator."""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .super_orchestrator import FamilyResult


def handle_bidi(orchestrator, content: str, file_path: str, apply_fixes: bool, result: "FamilyResult") -> None:
    """Handle BiDi family."""
    orch_result = orchestrator.run(content, file_path, apply_fixes)
    result.verdict = orch_result.verdict
    if orch_result.detect_result:
        result.issues_found = orch_result.detect_result.total
    if orch_result.fix_result:
        result.issues_fixed = (orch_result.fix_result.text_fixed + orch_result.fix_result.numbers_fixed +
                              orch_result.fix_result.math_fixed + orch_result.fix_result.tikz_fixed)


def handle_code(orchestrator, content: str, file_path: str, apply_fixes: bool, result: "FamilyResult") -> None:
    """Handle code family."""
    orch_result = orchestrator.run(content, file_path, apply_fixes)
    result.verdict = orch_result.verdict
    if orch_result.detect_result:
        result.issues_found = orch_result.detect_result.total
    if orch_result.fix_result:
        result.issues_fixed = orch_result.fix_result.overflow_fixed + orch_result.fix_result.hebrew_fixed


def handle_img(orchestrator, content: str, file_path: str, apply_fixes: bool, result: "FamilyResult") -> None:
    """Handle img family."""
    orch_result = orchestrator.run(content, file_path, apply_fixes, create_missing=False, validate=True)
    result.verdict = orch_result.verdict
    if orch_result.detect_result:
        result.issues_found = orch_result.detect_result.total
    if orch_result.fix_result:
        result.issues_fixed = orch_result.fix_result.paths_fixed


def handle_bib(orchestrator, content: str, file_path: str, apply_fixes: bool, result: "FamilyResult") -> None:
    """Handle bib family."""
    orch_result = orchestrator.run_on_content(content, "", apply_fixes)
    result.verdict = orch_result.verdict
    if orch_result.detect_result:
        result.issues_found = len(orch_result.detect_result.issues)


def handle_table(orchestrator, content: str, file_path: str, apply_fixes: bool, result: "FamilyResult") -> None:
    """Handle table family."""
    orch_result = orchestrator.run(content, file_path, apply_fixes)
    result.verdict = orch_result.verdict
    result.issues_found = orch_result.total_issues
    result.issues_fixed = orch_result.total_fixed


def handle_infra(orchestrator, content: str, file_path: str, apply_fixes: bool, result: "FamilyResult") -> None:
    """Handle infra family."""
    orch_result = orchestrator.run(apply_fixes)
    result.verdict = orch_result.verdict
    result.issues_found = orch_result.total_issues
    result.issues_fixed = orch_result.total_fixed


def handle_typeset(orchestrator, content: str, file_path: str, apply_fixes: bool, result: "FamilyResult") -> None:
    """Handle typeset family."""
    log_content = ""
    if file_path:
        log_path = Path(file_path).with_suffix(".log")
        if log_path.exists():
            log_content = log_path.read_text(encoding="utf-8", errors="ignore")
    orch_result = orchestrator.run(log_content, content, file_path, apply_fixes)
    result.verdict = orch_result.verdict
    result.issues_found = orch_result.total_detected
    result.issues_fixed = orch_result.total_fixed


HANDLERS = {
    "BiDi": handle_bidi, "bib": handle_bib, "code": handle_code,
    "img": handle_img, "infra": handle_infra, "table": handle_table, "typeset": handle_typeset,
}
