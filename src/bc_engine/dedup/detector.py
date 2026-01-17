"""
Dedup Detector - Implements DetectorInterface for QA integration.

Detects semantic duplicates across chapters.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional

from qa_engine.domain.interfaces import DetectorInterface
from qa_engine.domain.models.issue import Issue, Severity

from .config import DedupConfig
from .orchestrator import DedupOrchestrator


class DedupDetector(DetectorInterface):
    """
    Detector for chapter duplicates.

    Implements DetectorInterface for integration with QA pipeline.
    Uses DedupOrchestrator for actual detection logic.
    """

    RULES = {
        "dedup-semantic-duplicate": "Semantic duplication - content repeats earlier chapter",
        "dedup-imbalanced-chapter": "Chapter significantly larger than average",
        "dedup-missing-reference": "Content should reference earlier chapter",
    }

    def __init__(
        self,
        project_path: Optional[str | Path] = None,
        config_path: Optional[str | Path] = None,
        llm_callback: Optional[Callable[[str], str]] = None,
    ) -> None:
        """
        Initialize detector.

        Args:
            project_path: Root of book project
            config_path: Path to bc_dedup.json
            llm_callback: LLM function for semantic comparison
        """
        self._project_path = Path(project_path) if project_path else Path.cwd()
        self._config_path = config_path
        self._llm_callback = llm_callback
        self._config = DedupConfig()
        if config_path:
            self._config.load(config_path)

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """
        Detect deduplication issues.

        Note: For full deduplication, use detect_project() which
        compares across all chapters. This method is for single-file
        compatibility with DetectorInterface.

        Args:
            content: File content (used for balance check)
            file_path: Path to file
            offset: Line offset

        Returns:
            List of Issue objects
        """
        issues: List[Issue] = []

        # For single file, just check balance
        word_count = len(content.split())
        config_threshold = self._config.min_chunk_words * 100

        if word_count > config_threshold:
            issues.append(
                Issue(
                    rule="dedup-imbalanced-chapter",
                    file=file_path,
                    line=1 + offset,
                    content=f"Chapter has {word_count} words",
                    severity=Severity.INFO,
                    fix="Consider splitting into smaller sections",
                    context={"word_count": word_count},
                )
            )

        return issues

    def detect_project(self) -> List[Issue]:
        """
        Detect duplicates across entire project.

        Returns:
            List of Issue objects for all duplicates
        """
        orchestrator = DedupOrchestrator(
            project_path=self._project_path,
            config_path=self._config_path,
            llm_callback=self._llm_callback,
        )

        result = orchestrator.detect()
        issues: List[Issue] = []

        # Convert DedupIssues to standard Issues
        for dedup_issue in result.issues:
            severity = Severity(dedup_issue.severity.value)
            issues.append(
                Issue(
                    rule=dedup_issue.rule,
                    file=dedup_issue.file,
                    line=dedup_issue.line,
                    content=dedup_issue.content,
                    severity=severity,
                    fix=dedup_issue.fix,
                    context={
                        "source_chapter": dedup_issue.source_chapter,
                        "target_chapter": dedup_issue.target_chapter,
                        **dedup_issue.context,
                    },
                )
            )

        # Add balance warnings as INFO issues
        for warning in result.balance_warnings:
            issues.append(
                Issue(
                    rule="dedup-imbalanced-chapter",
                    file="",
                    line=0,
                    content=warning,
                    severity=Severity.INFO,
                )
            )

        return issues

    def get_rules(self) -> Dict[str, str]:
        """Return supported detection rules."""
        return self.RULES.copy()
