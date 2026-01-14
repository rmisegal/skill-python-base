# How to Create an Academic Book with This Project

A step-by-step guide for creating Hebrew-English academic LaTeX books using the QA & BC Engine.

## Prerequisites

- Python 3.9+ (3.13 recommended)
- [UV package manager](https://github.com/astral-sh/uv) (recommended)
- LuaLaTeX (MiKTeX distribution)
- Claude CLI

## Quick Start with UV (No Manual venv Required)

UV can run Python scripts directly without manually creating a virtual environment:

```powershell
# Install UV (one-time)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Run any Python script directly with UV
uv run python -c "from qa_engine import api; print('Ready!')"

# Run tests directly
uv run pytest tests/ -v

# Run the QA engine
uv run python -m qa_engine.cli.main run --project ./book
```

UV automatically creates and manages the virtual environment in `.venv/` when you use `uv run`.

## Step 1: Initialize Your Book Project

```powershell
# Clone or create your book directory
mkdir my-academic-book
cd my-academic-book

# Copy the LaTeX template structure
xcopy /E /I "C:\25D\GeneralLearning\skill-python-base\book" ".\book"
```

### Book Structure

```
my-academic-book/
├── book/
│   ├── main.tex                     # Master document
│   ├── chapters/
│   │   ├── chapter-01.tex           # Chapters
│   │   └── ...
│   ├── bibliography/
│   │   └── references.bib           # BibTeX database
│   ├── images/                      # Figures
│   ├── preamble.tex                 # Package includes
│   └── hebrew-academic-template.cls # Document class v6.3.4
└── qa-orchestration/                # QA reports
```

## Step 2: Generate Content with BC Engine

Use Claude CLI with BC (Book Creator) skills:

```bash
# Start Claude CLI
claude

# Generate full book pipeline (research -> content -> review -> dedup)
/bc-super "Write a chapter on neural networks for machine learning"

# Or run specific stages:
/bc-research "Find academic sources on deep learning"
/bc-content "Write section on gradient descent with code examples"
/bc-review "Polish chapter 2 for publication"
```

### BC Pipeline Stages

| Stage | Skills | Purpose |
|-------|--------|---------|
| 1. Research | `bc-source-research` | Gather sources, prepare BibTeX |
| 2. Content | `bc-content-drafting`, `bc-code`, `bc-math`, `bc-drawing` | Draft content with QA validation |
| 3. Review | `bc-architect`, `bc-hebrew` | Polish narrative, Hebrew editing |
| 4. Dedup | `bc-dedup` | Remove semantic duplicates |

## Step 3: Run QA on Your Book

### Option A: Using Claude CLI

```bash
claude
/qa-super "Run full QA on my book"

# Or specific families:
/qa-BiDi "Fix bidirectional text issues"
/qa-img "Check and fix image references"
/qa-table "Fix table RTL rendering"
```

### Option B: Using Python Directly with UV

```powershell
# Run full QA pipeline
uv run python -c "
from pathlib import Path
from qa_engine.infrastructure import SuperOrchestrator

orchestrator = SuperOrchestrator(project_path=Path('book'))
result = orchestrator.run_on_project(
    families=['BiDi', 'code', 'table', 'img', 'bib'],
    apply_fixes=True
)

print(f'Issues found: {result.total_issues}')
print(f'Issues fixed: {result.total_fixed}')
print(f'Verdict: {result.verdict}')
"
```

### Option C: Using Python Script

Create `run_qa.py`:

```python
from pathlib import Path
from qa_engine.infrastructure import SuperOrchestrator

def main():
    orchestrator = SuperOrchestrator(project_path=Path("book"))
    result = orchestrator.run_on_project(apply_fixes=True)
    print(f"Verdict: {result.verdict}")

if __name__ == "__main__":
    main()
```

Run with: `uv run python run_qa.py`

## Step 4: Compile LaTeX

```powershell
cd book

# First pass
lualatex -interaction=nonstopmode main.tex

# Bibliography
biber main

# Second pass (for TOC, references)
lualatex main.tex

# Optional: third pass for final cross-references
lualatex main.tex
```

## Step 5: Post-Compilation QA

After compilation, run typeset QA to fix warnings from the `.log` file:

```bash
/qa-typeset "Fix compilation warnings from main.log"
```

Or programmatically:

```powershell
uv run python -c "
from pathlib import Path
from qa_engine.infrastructure import TypesetOrchestrator

log_content = Path('book/main.log').read_text(encoding='utf-8', errors='ignore')
tex_content = Path('book/main.tex').read_text(encoding='utf-8')

orchestrator = TypesetOrchestrator()
result = orchestrator.run(log_content, tex_content, 'main.tex', apply_fixes=True)
print(f'Warnings fixed: {result.fix_result.fixes_applied if result.fix_result else 0}')
"
```

## QA Families Reference

| Family | Detects | Auto-Fixes |
|--------|---------|------------|
| **BiDi** | Numbers, English, acronyms in Hebrew | `\num{}`, `\en{}` wrappers |
| **code** | Code block formatting, encoding | Background, emoji removal |
| **table** | RTL table issues | `rtltabular`, column order |
| **img** | Missing images, wrong paths | Path fixes, placeholder creation |
| **bib** | Missing citations, .bib files | Citation keys, bibliography setup |
| **typeset** | Overfull hbox/vbox, float issues | Spacing, `\sloppy`, `\raggedbottom` |

## Custom LaTeX Commands

The template provides these commands for Hebrew/English mixing:

| Command | Usage | Example |
|---------|-------|---------|
| `\num{123}` | Numbers in Hebrew text | `בשנת \num{2024}` |
| `\en{text}` | English in Hebrew text | `מודל \en{CNN}` |
| `\he{טקסט}` | Hebrew in English text | `The \he{מודל} works` |
| `\hebyear{2024}` | Years | `\hebyear{2024}` |
| `\percent{50}` | Percentages | `\percent{50}` |

## Troubleshooting

### "Module not found" errors

```powershell
# Ensure you're in the project directory
cd C:\25D\GeneralLearning\skill-python-base

# Sync dependencies
uv sync
```

### BiDi rendering issues

Run BiDi QA specifically:
```bash
/qa-BiDi "Fix all bidirectional text issues in chapter-01.tex"
```

### Images not rendering

```bash
/qa-img "Detect and fix all image issues"
```

## Complete Workflow Example

```powershell
# 1. Setup
cd C:\25D\GeneralLearning\skill-python-base

# 2. Generate content (in Claude CLI)
# /bc-super "Write chapter 1 on introduction to AI"

# 3. Run QA
uv run python -c "
from pathlib import Path
from qa_engine.infrastructure import SuperOrchestrator
orchestrator = SuperOrchestrator(project_path=Path('book'))
result = orchestrator.run_on_project(apply_fixes=True)
print(f'QA Complete: {result.verdict}')
"

# 4. Compile
cd book
lualatex main.tex && biber main && lualatex main.tex

# 5. Review PDF
start main.pdf
```

## Additional Resources

- [UV Environment Guide](UV-ENVIRONMENT.md)
- [BC Mechanism](BC-MECHANISM.md)
- [When to Use This Project](WHEN-TO-USE.md)
- [Main README](../README.md)
