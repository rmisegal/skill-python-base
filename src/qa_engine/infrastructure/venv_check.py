"""Virtual environment and Python version check for QA system."""

import sys
from pathlib import Path


class VenvCheckError(Exception):
    """Raised when venv requirements are not met."""
    pass


def check_python_version(min_version: tuple = (3, 13)) -> bool:
    """Check if Python version meets minimum requirement."""
    return sys.version_info[:2] >= min_version


def check_venv_active() -> bool:
    """Check if running inside a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )


def get_venv_path() -> Path | None:
    """Get the virtual environment path if active."""
    if check_venv_active():
        return Path(sys.prefix)
    return None


def enforce_venv_requirements(min_version: tuple = (3, 13)) -> None:
    """
    Enforce venv and Python version requirements.
    
    Raises VenvCheckError if requirements not met.
    """
    errors = []
    
    if not check_venv_active():
        errors.append("Virtual environment is NOT active!")
        errors.append("Run: uv venv && source .venv/bin/activate (or .venv\Scripts\activate on Windows)")
    
    if not check_python_version(min_version):
        current = f"{sys.version_info.major}.{sys.version_info.minor}"
        required = f"{min_version[0]}.{min_version[1]}"
        errors.append(f"Python {current} detected, but {required}+ is required!")
        errors.append("Run: uv python install 3.13 && uv venv --python 3.13")
    
    if errors:
        msg = "\n".join(["=" * 60, "QA SYSTEM BLOCKED - Environment Check Failed", "=" * 60] + errors + ["=" * 60])
        raise VenvCheckError(msg)


def get_environment_info() -> dict:
    """Get current environment information."""
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "venv_active": check_venv_active(),
        "venv_path": str(get_venv_path()) if get_venv_path() else None,
        "meets_requirements": check_venv_active() and check_python_version(),
    }
