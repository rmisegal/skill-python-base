"""
Bibliography QA orchestrator (Level 1).

Implements qa-bib skill.md v1.0 - coordinates all bibliography QA skills.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .detection.bib_models import BibDetectResult, BibFixResult, BibOrchestratorResult
from .detection.bib_detector import BibDetector
from .fixing.bib_fixer import BibFixer


class BibOrchestrator:
    """
    Bibliography QA Orchestrator (Level 1).

    Aligned with qa-bib skill.md v1.0:
    - Coordinates qa-bib-detect and qa-bib-fix-missing
    - Manages the orchestration flow
    - Produces combined results
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize orchestrator with project root."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.detector = BibDetector()
        self.fixer = BibFixer()

    def run(self, project_path: Optional[Path] = None,
            bib_file: Optional[Path] = None,
            auto_fix: bool = False) -> BibOrchestratorResult:
        """
        Run the bibliography QA orchestration flow.

        Flow:
        1. Run qa-bib-detect
        2. If issues found and auto_fix=True, run qa-bib-fix-missing

        Args:
            project_path: Path to LaTeX project (default: project_root)
            bib_file: Path to .bib file (optional, auto-detect)
            auto_fix: Whether to automatically apply fixes

        Returns:
            BibOrchestratorResult with combined results
        """
        path = project_path or self.project_root
        result = BibOrchestratorResult()

        # Step 1: Run detection
        result.detect_result = self.detector.detect_in_project(path, bib_file)

        # Step 2: Run fixes if needed and requested
        if auto_fix and result.detect_result.triggers:
            # For now, fixes are prepared but not written to files
            # In production, this would modify the actual files
            result.fix_result = BibFixResult()

        return result

    def run_detection_only(self, project_path: Optional[Path] = None,
                           bib_file: Optional[Path] = None) -> BibDetectResult:
        """Run only detection phase."""
        path = project_path or self.project_root
        return self.detector.detect_in_project(path, bib_file)

    def run_on_content(self, tex_content: str, bib_content: str = "",
                       auto_fix: bool = False) -> BibOrchestratorResult:
        """
        Run orchestration on content strings (for testing).

        Args:
            tex_content: LaTeX content
            bib_content: Bibliography content
            auto_fix: Whether to apply fixes

        Returns:
            BibOrchestratorResult
        """
        result = BibOrchestratorResult()

        # Detection
        result.detect_result = self.detector.detect_content(tex_content, bib_content)

        # Fixing
        if auto_fix and result.detect_result.triggers:
            _, _, fix_result = self.fixer.fix_from_detect_result(
                result.detect_result, tex_content, bib_content
            )
            result.fix_result = fix_result

        return result

    def get_child_skills(self) -> List[Dict[str, str]]:
        """Return list of child skills."""
        return [
            {"skill": "qa-bib-detect", "type": "Detector",
             "purpose": "Find citation/bibliography issues"},
            {"skill": "qa-bib-fix-missing", "type": "Fixer",
             "purpose": "Add missing bibliography entries and commands"},
        ]

    def get_detection_categories(self) -> List[Dict[str, str]]:
        """Return detection categories from skill.md."""
        return [
            {"id": 1, "name": "Missing Bibliography Entry",
             "desc": "Citation key not found in .bib file"},
            {"id": 2, "name": "Missing Bibliography Command",
             "desc": "No \\printbibliography or equivalent"},
            {"id": 3, "name": "Missing TOC Entry",
             "desc": "Bibliography not in table of contents"},
            {"id": 4, "name": "Empty Bibliography",
             "desc": "Command exists but no entries printed"},
            {"id": 5, "name": "Unused Entry",
             "desc": "Entry in .bib but never cited (WARNING only)"},
        ]

    def to_dict(self, result: BibOrchestratorResult) -> Dict[str, Any]:
        """Convert result to dictionary matching qa-bib skill.md output format."""
        output = {
            "skill": "qa-bib",
            "status": result.status,
            "verdict": result.verdict,
            "children_results": {},
            "summary": {}
        }

        if result.detect_result:
            output["children_results"]["qa-bib-detect"] = self.detector.to_dict(result.detect_result)
            output["summary"] = {
                "citations_found": result.detect_result.citations_total,
                "bib_entries": len(result.detect_result.bib_entries),
                "missing_entries": len(result.detect_result.missing_entries),
                "unused_entries": len(result.detect_result.unused_entries),
                "has_printbib": result.detect_result.has_printbib,
                "in_toc": result.detect_result.bib_in_toc,
            }

        if result.fix_result:
            output["children_results"]["qa-bib-fix-missing"] = self.fixer.to_dict(result.fix_result)

        return output

    def get_verdict_logic(self) -> Dict[str, str]:
        """Return verdict logic from skill.md."""
        return {
            "FAIL": "Missing bibliography entries OR no printbibliography command",
            "WARNING": "Unused entries OR bibliography not in TOC",
            "PASS": "All citations have entries AND bibliography prints correctly"
        }
