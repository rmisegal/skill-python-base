@echo off
REM Run all tests with coverage

echo Running QA Engine Tests
echo =======================

cd /d "%~dp0\.."

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run tests with coverage
uv run pytest tests/ -v --cov=src/qa_engine --cov-report=html --cov-report=term

echo.
echo Tests completed. Coverage report in htmlcov/index.html
