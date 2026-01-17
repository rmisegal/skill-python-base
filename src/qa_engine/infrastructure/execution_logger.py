"""
Execution Logger for QA Skills.

Tracks which skills, families, and rules were executed during QA run.
Used by qa-verify-execution to ensure complete coverage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class RuleExecution:
    """Record of a single rule execution."""
    rule_id: str
    family: str
    skill: str
    executed_at: datetime
    issues_found: int = 0
    status: str = "executed"  # executed, skipped, failed


@dataclass
class SkillExecution:
    """Record of a skill execution."""
    skill_id: str
    family: str
    level: int  # 0, 1, or 2
    executed_at: datetime
    rules_executed: List[str] = field(default_factory=list)
    issues_found: int = 0
    status: str = "executed"


@dataclass
class ExecutionLog:
    """Complete execution log for a QA run."""
    run_id: str
    started_at: datetime
    version: int = 0
    completed_at: Optional[datetime] = None
    families_executed: Set[str] = field(default_factory=set)
    skills_executed: Dict[str, SkillExecution] = field(default_factory=dict)
    rules_executed: Dict[str, RuleExecution] = field(default_factory=dict)


class ExecutionLogger:
    """
    Singleton logger for tracking QA execution.

    Usage:
        logger = ExecutionLogger.get_instance()
        logger.start_run("run-123")
        logger.log_skill("qa-BiDi-detect", "BiDi", 2)
        logger.log_rule("bidi-numbers", "BiDi", "qa-BiDi-detect", issues=3)
        logger.end_run()
        report = logger.get_verification_report()
    """

    _instance: Optional[ExecutionLogger] = None
    _log: Optional[ExecutionLog] = None

    @classmethod
    def get_instance(cls) -> ExecutionLogger:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset logger for new run."""
        cls._instance = None
        cls._log = None

    def start_run(self, run_id: str) -> None:
        """Start a new QA run."""
        self._log = ExecutionLog(
            run_id=run_id,
            started_at=datetime.now(),
        )

    def end_run(self) -> None:
        """Mark run as completed."""
        if self._log:
            self._log.completed_at = datetime.now()

    def log_family(self, family: str) -> None:
        """Log that a family was executed."""
        if self._log:
            self._log.families_executed.add(family)

    def log_skill(
        self, skill_id: str, family: str, level: int, status: str = "executed"
    ) -> None:
        """Log skill execution."""
        if not self._log:
            return
        self._log.skills_executed[skill_id] = SkillExecution(
            skill_id=skill_id,
            family=family,
            level=level,
            executed_at=datetime.now(),
            status=status,
        )
        self._log.families_executed.add(family)

    def log_rule(
        self,
        rule_id: str,
        family: str,
        skill: str,
        issues: int = 0,
        status: str = "executed",
    ) -> None:
        """Log rule execution."""
        if not self._log:
            return
        self._log.rules_executed[rule_id] = RuleExecution(
            rule_id=rule_id,
            family=family,
            skill=skill,
            executed_at=datetime.now(),
            issues_found=issues,
            status=status,
        )
        # Update skill's rule list
        if skill in self._log.skills_executed:
            self._log.skills_executed[skill].rules_executed.append(rule_id)
            self._log.skills_executed[skill].issues_found += issues

    def get_execution_log(self) -> Optional[ExecutionLog]:
        """Get current execution log."""
        return self._log

    def get_verification_report(
        self, expected_families: List[str], expected_rules: Dict[str, List[str]]
    ) -> Dict:
        """
        Generate verification report comparing expected vs actual execution.

        Args:
            expected_families: List of families that should have run
            expected_rules: Dict of family -> list of rules that should run

        Returns:
            Verification report with missing items
        """
        if not self._log:
            return {"error": "No execution log available"}

        missing_families = set(expected_families) - self._log.families_executed
        missing_rules: Dict[str, List[str]] = {}

        for family, rules in expected_rules.items():
            executed = {
                r for r, e in self._log.rules_executed.items()
                if e.family == family
            }
            missing = set(rules) - executed
            if missing:
                missing_rules[family] = list(missing)

        all_passed = not missing_families and not missing_rules

        return {
            "run_id": self._log.run_id,
            "started_at": self._log.started_at.isoformat(),
            "completed_at": (
                self._log.completed_at.isoformat()
                if self._log.completed_at else None
            ),
            "verification_passed": all_passed,
            "families_expected": expected_families,
            "families_executed": list(self._log.families_executed),
            "families_missing": list(missing_families),
            "rules_missing": missing_rules,
            "total_skills_executed": len(self._log.skills_executed),
            "total_rules_executed": len(self._log.rules_executed),
            "total_issues_found": sum(
                r.issues_found for r in self._log.rules_executed.values()
            ),
        }

    def save_log(self, output_dir: Path) -> Optional[Path]:
        """Save execution log to versioned JSON file with FIFO rotation."""
        if not self._log:
            return None
        from .log_manager import LogManager
        manager = LogManager(output_dir)
        self._log.version = manager.get_next_version()
        data = self._build_log_data()
        return manager.save_with_rotation(json.dumps(data, indent=2, ensure_ascii=False))

    def _build_log_data(self) -> Dict:
        """Build log data dictionary."""
        return {
            "run_id": self._log.run_id, "version": self._log.version,
            "started_at": self._log.started_at.isoformat(),
            "completed_at": self._log.completed_at.isoformat() if self._log.completed_at else None,
            "families_executed": list(self._log.families_executed),
            "skills_executed": {
                k: {"skill_id": v.skill_id, "family": v.family, "level": v.level,
                    "executed_at": v.executed_at.isoformat(), "rules_executed": v.rules_executed,
                    "issues_found": v.issues_found, "status": v.status}
                for k, v in self._log.skills_executed.items()},
            "rules_executed": {
                k: {"rule_id": v.rule_id, "family": v.family, "skill": v.skill,
                    "executed_at": v.executed_at.isoformat(), "issues_found": v.issues_found,
                    "status": v.status}
                for k, v in self._log.rules_executed.items()},
        }

    @staticmethod
    def clear_logs(log_dir: Path) -> int:
        """Clear all log files in directory. Returns count of deleted files."""
        from .log_manager import LogManager
        return LogManager(log_dir).clear_logs()
