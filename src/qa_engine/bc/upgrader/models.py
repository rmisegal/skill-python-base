"""Data models for BC-QA upgrader."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any


class IssueCategory(Enum):
    """Issue category prefixes."""
    BIDI = "BIDI"
    CODE = "CODE"
    TABLE = "TABLE"
    BIB = "BIB"
    IMG = "IMG"
    TYPE = "TYPE"


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ParsedIssue:
    """Parsed issue from command argument."""
    issue_id: str
    category: IssueCategory
    number: int
    description: str = ""


@dataclass
class QARule:
    """QA detection rule."""
    rule_id: str
    family: str
    description: str
    pattern: str
    fix_pattern: str
    severity: Severity
    auto_fixable: bool


@dataclass
class BCSkillMapping:
    """Mapping of BC skill to issues it can cause."""
    skill_name: str
    skill_path: str
    issue_categories: List[IssueCategory]
    content_types: List[str]
    validators: List[str]


@dataclass
class GapAnalysis:
    """Analysis of gap between BC skill and QA rule."""
    issue: ParsedIssue
    qa_rules: List[QARule]
    bc_skills: List[BCSkillMapping]
    root_cause: str
    impact: str


@dataclass
class UpgradeAction:
    """Single upgrade action to apply."""
    action_type: str  # "template", "config", "validator", "skill"
    target_path: str
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpgradePlan:
    """Complete upgrade plan for an issue."""
    issue: ParsedIssue
    gap_analysis: GapAnalysis
    actions: List[UpgradeAction]
    requires_user_action: bool = False
    user_action_message: str = ""


@dataclass
class UpgradeResult:
    """Result of applying an upgrade."""
    action: UpgradeAction
    success: bool
    message: str
    error: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation result after upgrade."""
    issue: ParsedIssue
    passed: bool
    remaining_issues: int
    details: str
