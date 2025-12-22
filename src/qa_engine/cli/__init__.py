"""
CLI interface for QA Engine management.

Provides command-line tools for managing:
- Skills (list, create, delete, enable, disable, duplicate)
- Tools (list, add, remove, generate)
- Resources (list, create, update)
- Pipeline (show, insert, remove, move, run)
"""

from .main import main

__all__ = ["main"]
