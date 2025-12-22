"""
Improvement tracker for QA mechanism improvement.

Generates investigation and improvement reports.
Aligned with qa-mechanism-improver output formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .failure_classifier import BugClassification, FailureMode
from .skill_analyzer import SkillAnalysis


@dataclass
class InvestigationReport:
    """Investigation report matching skill.md format."""
    description: str
    discovered: str
    document: str
    responsible_family: str
    responsible_detector: str
    failure_mode: FailureMode
    root_cause: str
    classification: Optional[BugClassification] = None


@dataclass
class ImprovementReport:
    """Improvement report matching skill.md format."""
    skill_name: str
    old_version: str
    new_version: str
    new_rules: List[str] = field(default_factory=list)
    new_patterns: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    detection_test: str = "PENDING"
    fix_test: str = "PENDING"
    clean_verification: str = "PENDING"


class ImprovementTracker:
    """
    Tracks QA mechanism investigations and improvements.

    Generates reports in markdown format matching skill.md templates.
    """

    def __init__(self, output_path: Optional[Path] = None):
        """Initialize tracker with output path."""
        self.output_path = output_path or Path.cwd()
        self.investigations: List[InvestigationReport] = []
        self.improvements: List[ImprovementReport] = []

    def create_investigation(
        self,
        description: str,
        document: str,
        classification: BugClassification,
        root_cause: str,
    ) -> InvestigationReport:
        """Create investigation report from classification."""
        report = InvestigationReport(
            description=description,
            discovered="Manual testing",
            document=document,
            responsible_family=classification.l1_family,
            responsible_detector=classification.suggested_skill,
            failure_mode=classification.failure_mode,
            root_cause=root_cause,
            classification=classification,
        )
        self.investigations.append(report)
        return report

    def create_improvement(
        self,
        skill_analysis: SkillAnalysis,
        new_rules: List[str],
        new_patterns: List[str],
    ) -> ImprovementReport:
        """Create improvement report from skill analysis."""
        old_parts = skill_analysis.version.split(".")
        new_minor = int(old_parts[1]) + 1 if len(old_parts) > 1 else 1
        new_version = f"{old_parts[0]}.{new_minor}.0"

        report = ImprovementReport(
            skill_name=skill_analysis.skill_id,
            old_version=skill_analysis.version,
            new_version=new_version,
            new_rules=new_rules,
            new_patterns=new_patterns,
            files_modified=[f"{skill_analysis.skill_id}/skill.md"],
        )
        self.improvements.append(report)
        return report

    def format_investigation_markdown(self, report: InvestigationReport) -> str:
        """Format investigation report as markdown."""
        return f"""## QA Mechanism Investigation Report

### Problem
- **Description:** {report.description}
- **Discovered:** {report.discovered}
- **Document:** {report.document}

### Analysis
- **Responsible Family:** {report.responsible_family}
- **Responsible Detector:** {report.responsible_detector}
- **Failure Mode:** {report.failure_mode.value}
- **Root Cause:** {report.root_cause}

### Keywords Matched
{self._format_keywords(report.classification)}

### Suggested Investigation Path
{self._format_steps(report.classification)}
"""

    def format_improvement_markdown(self, report: ImprovementReport) -> str:
        """Format improvement report as markdown."""
        return f"""## QA Mechanism Improvement Report

### Changes Made
- **Skill:** {report.skill_name} v{report.old_version} → v{report.new_version}
- **New Rules:** {', '.join(report.new_rules) or 'None'}
- **New Patterns:** {', '.join(report.new_patterns) or 'None'}

### Files Modified
{self._format_list(report.files_modified)}

### Files Created
{self._format_list(report.files_created) or '- None'}

### Verification
- **Detection Test:** {report.detection_test}
- **Fix Test:** {report.fix_test}
- **Clean Verification:** {report.clean_verification}

### Impact
This improvement enables automatic detection and fixing of the identified bug pattern.
"""

    def _format_keywords(self, classification: Optional[BugClassification]) -> str:
        if not classification:
            return "- None"
        return "\n".join(f"- {kw}" for kw in classification.keywords_matched) or "- None"

    def _format_steps(self, classification: Optional[BugClassification]) -> str:
        if not classification:
            return "1. Manual investigation required"
        from .failure_classifier import FailureClassifier
        classifier = FailureClassifier()
        steps = classifier.suggest_investigation_path(classification)
        return "\n".join(steps)

    def _format_list(self, items: List[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else ""

    def to_dict(self, report: InvestigationReport) -> Dict[str, Any]:
        """Convert investigation report to dictionary."""
        return {
            "skill": "qa-mechanism-improver",
            "status": "DONE",
            "investigation": {
                "description": report.description,
                "discovered": report.discovered,
                "document": report.document,
                "responsible_family": report.responsible_family,
                "responsible_detector": report.responsible_detector,
                "failure_mode": report.failure_mode.value,
                "root_cause": report.root_cause,
            },
            "classification": {
                "domain": report.classification.domain if report.classification else "",
                "confidence": report.classification.confidence if report.classification else 0,
                "keywords": report.classification.keywords_matched if report.classification else [],
            },
            "timestamp": datetime.now().isoformat(),
        }
