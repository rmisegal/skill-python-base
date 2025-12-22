"""Pytest configuration for the test suite."""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# BLOCKING CHECK: Enforce venv with Python 3.13+
from qa_engine.infrastructure.venv_check import enforce_venv_requirements, VenvCheckError

try:
    enforce_venv_requirements(min_version=(3, 13))
except VenvCheckError as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)
