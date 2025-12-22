"""
Custom exceptions for the QA Engine.

All exceptions inherit from QAEngineError for easy catching.
"""


class QAEngineError(Exception):
    """Base exception for all QA Engine errors."""
    pass


class ConfigurationError(QAEngineError):
    """Raised when configuration is invalid or missing."""
    pass


class CoordinationError(QAEngineError):
    """Raised when coordination/locking fails."""
    pass


class DetectionError(QAEngineError):
    """Raised when detection process fails."""
    pass


class FixError(QAEngineError):
    """Raised when fix process fails."""
    pass


class SkillNotFoundError(QAEngineError):
    """Raised when a skill cannot be found."""
    pass


class LockAcquisitionError(CoordinationError):
    """Raised when unable to acquire a lock."""
    pass


class StaleAgentError(CoordinationError):
    """Raised when an agent is detected as stale."""
    pass
