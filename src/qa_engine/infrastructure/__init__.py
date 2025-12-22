"""
Infrastructure layer for QA Engine.

Contains concrete implementations of detection and fix tools,
coordination services, backup utilities, and external integrations.
"""

from .backup import ProjectBackupUtility, BackupResult
from .coordination import Coordinator, HeartbeatMonitor
from .detection import BiDiDetector, CodeDetector, TypesetDetector
from .bidi_orchestrator import BiDiOrchestrator, BiDiOrchestratorResult, BiDiDetectResult, BiDiFixResult
from .image_orchestrator import ImageOrchestrator, ImageOrchestratorResult, ImageDetectResult, ImageFixResult
from .super_orchestrator import SuperOrchestrator, SuperOrchestratorResult, FamilyResult
from .typeset_orchestrator import TypesetOrchestrator, TypesetOrchestratorResult

__all__ = [
    "BackupResult",
    "Coordinator",
    "HeartbeatMonitor",
    "ProjectBackupUtility",
    "BiDiDetector",
    "BiDiOrchestrator",
    "BiDiOrchestratorResult",
    "BiDiDetectResult",
    "BiDiFixResult",
    "CodeDetector",
    "FamilyResult",
    "ImageOrchestrator",
    "ImageOrchestratorResult",
    "ImageDetectResult",
    "ImageFixResult",
    "SuperOrchestrator",
    "SuperOrchestratorResult",
    "TypesetDetector",
    "TypesetOrchestrator",
    "TypesetOrchestratorResult",
]
