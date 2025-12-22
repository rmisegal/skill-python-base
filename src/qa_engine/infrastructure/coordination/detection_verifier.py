"""
Detection verifier for QA orchestration.

Ensures L1 family detectors actually run before accepting PASS verdict.
Implements the "MANDATORY DETECTION" requirement from qa-super skill.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set


@dataclass
class DetectionEvidence:
    """Evidence that a detector actually ran."""
    detector_name: str
    invoked_at: datetime
    files_scanned: int
    issues_found: int
    rules_checked: List[str] = field(default_factory=list)


@dataclass
class FamilyVerification:
    """Verification status for a family."""
    family: str
    required_detectors: List[str]
    evidence: Dict[str, DetectionEvidence] = field(default_factory=dict)

    @property
    def is_verified(self) -> bool:
        """Check if all required detectors have evidence."""
        return all(d in self.evidence for d in self.required_detectors)

    @property
    def missing_detectors(self) -> List[str]:
        """Get list of detectors that didn't run."""
        return [d for d in self.required_detectors if d not in self.evidence]


# Required detectors per family (from qa-super skill.md)
FAMILY_REQUIRED_DETECTORS: Dict[str, List[str]] = {
    "BiDi": ["BiDiDetector"],  # Must run main detector
    "code": ["CodeDetector"],
    "table": ["TableDetector"],
    "typeset": ["TypesetDetector"],
    "bib": ["BibDetector"],
    "img": ["ImageDetector"],
    "heb_math": ["HebMathDetector"],
}


class DetectionVerifier:
    """
    Verifies that detection skills actually execute.

    Prevents false PASS reports when detection is skipped.
    """

    def __init__(self) -> None:
        self._evidence: Dict[str, DetectionEvidence] = {}
        self._family_status: Dict[str, FamilyVerification] = {}

    def record_detection(
        self,
        detector_name: str,
        files_scanned: int,
        issues_found: int,
        rules_checked: Optional[List[str]] = None,
    ) -> None:
        """Record evidence that a detector ran."""
        self._evidence[detector_name] = DetectionEvidence(
            detector_name=detector_name,
            invoked_at=datetime.now(),
            files_scanned=files_scanned,
            issues_found=issues_found,
            rules_checked=rules_checked or [],
        )

    def verify_family(self, family: str) -> FamilyVerification:
        """Verify all required detectors ran for a family."""
        required = FAMILY_REQUIRED_DETECTORS.get(family, [])
        verification = FamilyVerification(
            family=family,
            required_detectors=required,
        )

        for detector in required:
            if detector in self._evidence:
                verification.evidence[detector] = self._evidence[detector]

        self._family_status[family] = verification
        return verification

    def get_unverified_families(self, families: List[str]) -> List[str]:
        """Get families that haven't passed verification."""
        unverified = []
        for family in families:
            verification = self.verify_family(family)
            if not verification.is_verified:
                unverified.append(family)
        return unverified

    def get_verification_report(self) -> Dict[str, Dict]:
        """Generate verification report for all families."""
        report = {}
        for family, verification in self._family_status.items():
            report[family] = {
                "verified": verification.is_verified,
                "required": verification.required_detectors,
                "ran": list(verification.evidence.keys()),
                "missing": verification.missing_detectors,
            }
        return report

    def clear(self) -> None:
        """Clear all evidence (for new run)."""
        self._evidence.clear()
        self._family_status.clear()

    def require_verification(self, family: str) -> bool:
        """
        Check if family verdict can be accepted.

        Returns False if detection was not verified, meaning
        the PASS verdict should be rejected.
        """
        if family not in self._family_status:
            self.verify_family(family)
        return self._family_status[family].is_verified
