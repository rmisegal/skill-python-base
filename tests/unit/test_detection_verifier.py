"""Unit tests for DetectionVerifier."""

import pytest
from qa_engine.infrastructure.coordination.detection_verifier import (
    DetectionVerifier, DetectionEvidence, FamilyVerification,
    FAMILY_REQUIRED_DETECTORS,
)


class TestDetectionVerifier:
    """Test cases for DetectionVerifier."""

    def test_record_detection(self):
        """Test recording detection evidence."""
        verifier = DetectionVerifier()
        verifier.record_detection(
            detector_name="BiDiDetector",
            files_scanned=10,
            issues_found=5,
            rules_checked=["rule1", "rule2"],
        )

        assert "BiDiDetector" in verifier._evidence
        evidence = verifier._evidence["BiDiDetector"]
        assert evidence.files_scanned == 10
        assert evidence.issues_found == 5

    def test_verify_family_all_detectors_ran(self):
        """Test family verification when all detectors ran."""
        verifier = DetectionVerifier()
        verifier.record_detection("BiDiDetector", 10, 5)

        verification = verifier.verify_family("BiDi")

        assert verification.is_verified is True
        assert not verification.missing_detectors

    def test_verify_family_detector_missing(self):
        """Test family verification when detector didn't run."""
        verifier = DetectionVerifier()
        # Don't record any detection

        verification = verifier.verify_family("BiDi")

        assert verification.is_verified is False
        assert "BiDiDetector" in verification.missing_detectors

    def test_get_unverified_families(self):
        """Test getting list of unverified families."""
        verifier = DetectionVerifier()
        verifier.record_detection("BiDiDetector", 10, 5)
        # Don't record CodeDetector

        unverified = verifier.get_unverified_families(["BiDi", "code"])

        assert "code" in unverified
        assert "BiDi" not in unverified

    def test_get_verification_report(self):
        """Test verification report generation."""
        verifier = DetectionVerifier()
        verifier.record_detection("BiDiDetector", 10, 5)
        verifier.verify_family("BiDi")
        verifier.verify_family("code")

        report = verifier.get_verification_report()

        assert "BiDi" in report
        assert report["BiDi"]["verified"] is True
        assert "code" in report
        assert report["code"]["verified"] is False

    def test_clear_evidence(self):
        """Test clearing evidence for new run."""
        verifier = DetectionVerifier()
        verifier.record_detection("BiDiDetector", 10, 5)
        verifier.verify_family("BiDi")

        verifier.clear()

        assert len(verifier._evidence) == 0
        assert len(verifier._family_status) == 0

    def test_require_verification_passes(self):
        """Test require_verification returns True when verified."""
        verifier = DetectionVerifier()
        verifier.record_detection("BiDiDetector", 10, 5)

        result = verifier.require_verification("BiDi")

        assert result is True

    def test_require_verification_fails(self):
        """Test require_verification returns False when not verified."""
        verifier = DetectionVerifier()
        # Don't record detection

        result = verifier.require_verification("BiDi")

        assert result is False

    def test_family_required_detectors_defined(self):
        """Test that all main families have required detectors defined."""
        expected_families = ["BiDi", "code", "table", "typeset", "bib"]
        for family in expected_families:
            assert family in FAMILY_REQUIRED_DETECTORS
            assert len(FAMILY_REQUIRED_DETECTORS[family]) > 0

    def test_detection_evidence_fields(self):
        """Test DetectionEvidence has all required fields."""
        verifier = DetectionVerifier()
        verifier.record_detection(
            detector_name="TestDetector",
            files_scanned=5,
            issues_found=3,
            rules_checked=["r1"],
        )

        evidence = verifier._evidence["TestDetector"]
        assert evidence.detector_name == "TestDetector"
        assert evidence.invoked_at is not None
        assert evidence.files_scanned == 5
        assert evidence.issues_found == 3
        assert evidence.rules_checked == ["r1"]
