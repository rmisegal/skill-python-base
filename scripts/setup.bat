@echo off
REM Setup development environment

echo QA Engine - Development Setup
echo =============================

cd /d "%~dp0\.."

echo Installing dependencies...
uv sync --all-extras

echo.
echo Running architecture tests...
uv run pytest tests/arch/ -v

echo.
echo Setup complete!
echo Run 'scripts\run_tests.bat' to execute all tests.
