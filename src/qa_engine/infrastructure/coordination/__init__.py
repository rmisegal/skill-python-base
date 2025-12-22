"""
Coordination services for multi-agent QA execution.

Provides resource locking, heartbeat monitoring, and shared status.
"""

from .coordinator import Coordinator
from .heartbeat import HeartbeatMonitor
from .detection_verifier import (
    DetectionVerifier, DetectionEvidence, FamilyVerification,
    FAMILY_REQUIRED_DETECTORS,
)

__all__ = [
    "Coordinator",
    "HeartbeatMonitor",
    "DetectionVerifier",
    "DetectionEvidence",
    "FamilyVerification",
    "FAMILY_REQUIRED_DETECTORS",
]
