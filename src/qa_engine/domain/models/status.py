"""
QA execution status model.

Tracks execution status and progress for QA operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionState(Enum):
    """Execution state values."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StatusEntry:
    """
    Single status entry for a skill execution.

    Attributes:
        skill_name: Name of the skill
        state: Current execution state
        started_at: Execution start time
        completed_at: Execution end time
        issues_found: Number of issues detected
        error_message: Error message if failed
        agent_id: Executing agent identifier
    """

    skill_name: str
    state: ExecutionState
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    issues_found: int = 0
    error_message: Optional[str] = None
    agent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "skill_name": self.skill_name,
            "state": self.state.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "issues_found": self.issues_found,
            "error_message": self.error_message,
            "agent_id": self.agent_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StatusEntry:
        """Create from dictionary."""
        return cls(
            skill_name=data["skill_name"],
            state=ExecutionState(data["state"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            issues_found=data.get("issues_found", 0),
            error_message=data.get("error_message"),
            agent_id=data.get("agent_id"),
        )


@dataclass
class QAStatus:
    """
    Overall QA execution status.

    Aggregates status entries for all skills in a QA run.
    """

    run_id: str
    project_path: str
    started_at: datetime
    entries: Dict[str, StatusEntry] = field(default_factory=dict)
    completed_at: Optional[datetime] = None

    def add_entry(self, entry: StatusEntry) -> None:
        """Add or update a status entry."""
        self.entries[entry.skill_name] = entry

    def get_entry(self, skill_name: str) -> Optional[StatusEntry]:
        """Get status entry by skill name."""
        return self.entries.get(skill_name)

    def mark_started(self, skill_name: str, agent_id: str) -> None:
        """Mark a skill as started."""
        self.entries[skill_name] = StatusEntry(
            skill_name=skill_name,
            state=ExecutionState.RUNNING,
            started_at=datetime.now(),
            agent_id=agent_id,
        )

    def mark_completed(
        self,
        skill_name: str,
        issues_found: int = 0,
    ) -> None:
        """Mark a skill as completed."""
        if skill_name in self.entries:
            entry = self.entries[skill_name]
            entry.state = ExecutionState.COMPLETED
            entry.completed_at = datetime.now()
            entry.issues_found = issues_found

    def mark_failed(self, skill_name: str, error: str) -> None:
        """Mark a skill as failed."""
        if skill_name in self.entries:
            entry = self.entries[skill_name]
            entry.state = ExecutionState.FAILED
            entry.completed_at = datetime.now()
            entry.error_message = error

    @property
    def total_issues(self) -> int:
        """Get total issues found across all skills."""
        return sum(e.issues_found for e in self.entries.values())

    @property
    def progress_percent(self) -> float:
        """Calculate completion percentage."""
        if not self.entries:
            return 0.0
        completed = sum(
            1 for e in self.entries.values()
            if e.state in (ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.SKIPPED)
        )
        return (completed / len(self.entries)) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "run_id": self.run_id,
            "project_path": self.project_path,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
            "total_issues": self.total_issues,
            "progress_percent": self.progress_percent,
        }
