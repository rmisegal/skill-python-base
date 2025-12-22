# Using Skills with UV Environment

## Overview

This project uses **UV** for fast Python package management. Skills that have Python tools need access to the `qa_engine` package, which requires either:

1. Running from within this project's UV environment
2. Installing the package globally
3. Temporarily activating this environment for skill execution

## Option 1: Local Project Usage (Recommended)

When working within the skill-python-base project:

```powershell
cd C:\path\to\skill-python-base

# Activate UV environment
.\.venv\Scripts\activate

# Run Claude CLI
claude

# Skills automatically have access to qa_engine
/qa-super "Run QA on my document"
```

## Option 2: Global Package Installation

Install qa_engine globally so any skill can use it:

```powershell
# Install in editable mode (updates reflect immediately)
pip install -e C:\path\to\skill-python-base

# Or build and install wheel
cd C:\path\to\skill-python-base
uv pip install build
python -m build
pip install dist\qa_engine-1.0.0-py3-none-any.whl
```

## Option 3: Skill-Level Environment Activation

For global skills that need this project's Python environment, modify `tool.py`:

```python
#!/usr/bin/env python3
"""Tool that activates skill-python-base environment."""
import subprocess
import sys
from pathlib import Path

# Path to skill-python-base
PROJECT_PATH = Path("C:/25D/GeneralLearning/skill-python-base")
VENV_PYTHON = PROJECT_PATH / ".venv" / "Scripts" / "python.exe"

def run_with_venv(script_content: str):
    """Execute script using project's venv Python."""
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", script_content],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_PATH)
    )
    return result.stdout, result.stderr

# Example usage
code = '''
from qa_engine.infrastructure.detection import BiDiDetector
detector = BiDiDetector()
print(detector.get_rules())
'''
stdout, stderr = run_with_venv(code)
print(stdout)
```

## Option 4: Path Injection in tool.py

For simpler cases, inject the source path:

```python
#!/usr/bin/env python3
"""Tool with path injection."""
import sys
from pathlib import Path

# Add qa_engine to path
QA_ENGINE_PATH = Path("C:/25D/GeneralLearning/skill-python-base/src")
sys.path.insert(0, str(QA_ENGINE_PATH))

# Now imports work
from qa_engine.infrastructure.detection import BiDiDetector

def detect(content: str, file_path: str = "") -> list:
    detector = BiDiDetector()
    issues = detector.detect(content, file_path)
    return [i.to_dict() for i in issues]
```

## Environment Variables

You can also use environment variables:

```powershell
# Set in system environment or .env file
$env:QA_ENGINE_PATH = "C:\25D\GeneralLearning\skill-python-base\src"
```

Then in `tool.py`:
```python
import os
import sys

qa_path = os.environ.get("QA_ENGINE_PATH")
if qa_path:
    sys.path.insert(0, qa_path)
```

## Checking Environment

Verify the environment is working:

```powershell
# From any directory, test import
python -c "from qa_engine import api; print('OK')"

# Check version
python -c "from qa_engine.shared.version import VERSION; print(VERSION)"
```

## Summary

| Method | Pros | Cons |
|--------|------|------|
| Local project | Simple, automatic | Must be in project dir |
| Global install | Works anywhere | Needs reinstall on changes |
| Venv activation | Full isolation | More complex tool.py |
| Path injection | Simple, no install | Hardcoded paths |
| Env variables | Configurable | Needs setup |
