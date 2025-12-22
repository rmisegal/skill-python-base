"""
Shared components for QA Engine.

Provides common utilities including configuration, logging,
version management, threading primitives, and DI container.
"""

from .version import VersionManager
from .config import ConfigManager
from .logging import PrintManager, JsonLogger
from .threading import ResourceManager
from .di import DIContainer

__all__ = [
    "VersionManager",
    "ConfigManager",
    "PrintManager",
    "JsonLogger",
    "ResourceManager",
    "DIContainer",
]
