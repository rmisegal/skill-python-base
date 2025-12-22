"""
Failure classifier for QA mechanism improvement.

Classifies bugs by domain and identifies failure modes.
Aligned with qa-mechanism-improver Phase 1 & 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class FailureMode(Enum):
    """Failure modes as defined in skill.md Phase 3."""
    SKILL_NOT_INVOKED = "skill_not_invoked"
    MISSING_RULE = "missing_rule"
    INCOMPLETE_PATTERN = "incomplete_pattern"
    LOGIC_BUG = "logic_bug"
    VERSION_MISMATCH = "version_mismatch"
    UNKNOWN = "unknown"


@dataclass
class BugClassification:
    """Result of classifying a bug."""
    domain: str
    l1_family: str
    l2_detectors: List[str]
    failure_mode: FailureMode
    confidence: float
    keywords_matched: List[str]
    suggested_skill: str


class FailureClassifier:
    """
    Classifies bugs into QA domains and failure modes.

    Uses keyword matching to identify:
    - L1 family responsible
    - Common L2 detectors
    - Failure mode
    """

    # Domain classification table from skill.md
    DOMAIN_MAP: Dict[str, Tuple[str, List[str]]] = {
        # Bug domain keywords -> (L1 family, [L2 detectors])
        "rtl": ("qa-BiDi", ["qa-BiDi-detect"]),
        "ltr": ("qa-BiDi", ["qa-BiDi-detect"]),
        "direction": ("qa-BiDi", ["qa-BiDi-detect"]),
        "hebrew": ("qa-BiDi", ["qa-BiDi-detect", "qa-heb-math-detect"]),
        "math": ("qa-BiDi", ["qa-heb-math-detect"]),
        "section": ("qa-BiDi", ["qa-BiDi-detect"]),
        "page number": ("qa-BiDi", ["qa-BiDi-detect"]),
        "tcolorbox": ("qa-BiDi", ["qa-BiDi-detect"]),
        "table": ("qa-table", ["qa-table-detect"]),
        "tabular": ("qa-table", ["qa-table-detect"]),
        "caption": ("qa-table", ["qa-table-detect"]),
        "code": ("qa-code", ["qa-code-detect"]),
        "listing": ("qa-code", ["qa-code-detect"]),
        "pythonbox": ("qa-code", ["qa-code-detect"]),
        "image": ("qa-img", ["qa-img-detect"]),
        "figure": ("qa-img", ["qa-img-detect"]),
        "includegraphics": ("qa-img", ["qa-img-detect"]),
        "overfull": ("qa-typeset", ["qa-typeset-detect"]),
        "underfull": ("qa-typeset", ["qa-typeset-detect"]),
        "hbox": ("qa-typeset", ["qa-typeset-detect"]),
        "vbox": ("qa-typeset", ["qa-typeset-detect"]),
        "mdframed": ("qa-typeset", ["qa-mdframed-detect"]),
        "pagebreak": ("qa-typeset", ["qa-mdframed-detect"]),
        "structure": ("qa-infra", ["qa-infra-scan"]),
        "subfiles": ("qa-infra", ["qa-infra-subfiles-detect"]),
        "reorganize": ("qa-infra", ["qa-infra-scan"]),
    }

    # Failure mode indicators
    FAILURE_INDICATORS: Dict[FailureMode, List[str]] = {
        FailureMode.SKILL_NOT_INVOKED: [
            "skill never ran", "not invoked", "skipped", "not called"
        ],
        FailureMode.MISSING_RULE: [
            "no rule", "not covered", "missing detection", "unknown pattern"
        ],
        FailureMode.INCOMPLETE_PATTERN: [
            "partial match", "some cases", "only works for", "doesn't catch all"
        ],
        FailureMode.LOGIC_BUG: [
            "wrong detection", "false positive", "false negative", "incorrect"
        ],
        FailureMode.VERSION_MISMATCH: [
            "old version", "outdated", "deprecated", "stale"
        ],
    }

    def classify(self, bug_description: str) -> BugClassification:
        """Classify a bug based on its description."""
        desc_lower = bug_description.lower()

        # Find matching domain
        domain, l1_family, l2_detectors, matched_keywords = self._match_domain(desc_lower)

        # Identify failure mode
        failure_mode = self._identify_failure_mode(desc_lower)

        # Calculate confidence
        confidence = min(len(matched_keywords) * 0.25, 1.0)

        return BugClassification(
            domain=domain,
            l1_family=l1_family,
            l2_detectors=l2_detectors,
            failure_mode=failure_mode,
            confidence=confidence,
            keywords_matched=matched_keywords,
            suggested_skill=l2_detectors[0] if l2_detectors else l1_family,
        )

    def _match_domain(self, desc: str) -> Tuple[str, str, List[str], List[str]]:
        """Match bug description to domain."""
        matched_keywords = []
        best_match: Optional[Tuple[str, List[str]]] = None

        for keyword, (family, detectors) in self.DOMAIN_MAP.items():
            if keyword in desc:
                matched_keywords.append(keyword)
                if best_match is None:
                    best_match = (family, detectors)

        if best_match:
            domain = matched_keywords[0] if matched_keywords else "unknown"
            return domain, best_match[0], best_match[1], matched_keywords

        return "unknown", "qa-super", [], matched_keywords

    def _identify_failure_mode(self, desc: str) -> FailureMode:
        """Identify failure mode from description."""
        for mode, indicators in self.FAILURE_INDICATORS.items():
            for indicator in indicators:
                if indicator in desc:
                    return mode
        return FailureMode.UNKNOWN

    def get_domain_table(self) -> Dict[str, Tuple[str, List[str]]]:
        """Return the domain classification table."""
        return self.DOMAIN_MAP.copy()

    def suggest_investigation_path(self, classification: BugClassification) -> List[str]:
        """Suggest investigation steps based on classification."""
        steps = [
            f"1. Read skill file: {classification.suggested_skill}/skill.md",
            f"2. Check detection rules for: {classification.domain}",
        ]

        if classification.failure_mode == FailureMode.SKILL_NOT_INVOKED:
            steps.append("3. Check orchestrator invocation logic")
            steps.append("4. Verify skill is enabled in QA-CLAUDE.md")
        elif classification.failure_mode == FailureMode.MISSING_RULE:
            steps.append("3. Add new detection rule to skill")
            steps.append("4. Add corresponding fix pattern")
        elif classification.failure_mode == FailureMode.INCOMPLETE_PATTERN:
            steps.append("3. Expand existing regex pattern")
            steps.append("4. Add edge case handling")
        elif classification.failure_mode == FailureMode.LOGIC_BUG:
            steps.append("3. Debug detection logic")
            steps.append("4. Fix conditional statements")

        return steps
