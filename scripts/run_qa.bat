@echo off
REM Run QA analysis on a project

echo QA Engine - LaTeX Document Analysis
echo ====================================

if "%1"=="" (
    echo Usage: run_qa.bat ^<project_path^>
    exit /b 1
)

cd /d "%~dp0\.."

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run QA controller
uv run python -c "from qa_engine.sdk import QAController; c = QAController('%1'); print(c.run().to_dict())"
