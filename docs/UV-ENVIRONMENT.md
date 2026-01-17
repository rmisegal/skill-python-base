# Understanding Skills, Python Tools, and UV Environment Setup

**Document Version:** 2.1.0
**Date:** 2025-12-22
**Audience:** Developers learning Claude CLI skills and Python tool integration

---

## Table of Contents

1. [What is This Document?](#1-what-is-this-document)
2. [Understanding Claude CLI Skills](#2-understanding-claude-cli-skills)
3. [What are QA and BC Skills?](#3-what-are-qa-and-bc-skills)
4. [Skill vs Tool: When to Use What](#4-skill-vs-tool-when-to-use-what)
5. [Where Are Skills Located?](#5-where-are-skills-located)
6. [What is UV?](#6-what-is-uv)
7. [Installing This Project](#7-installing-this-project)
8. [Why Can't We Use Regular Global Skills?](#8-why-cant-we-use-regular-global-skills)
9. [Environment Setup Options](#9-environment-setup-options)
10. [Complete Skills Reference Table](#10-complete-skills-reference-table)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. What is This Document?

### The Problem We're Solving

Imagine you have a helper robot (Claude CLI) that can do tasks for you. Normally, you just tell it what to do in plain English, and it figures it out. But sometimes, you want the robot to do something very specific and fast - like checking if your homework has spelling mistakes.

For these specific tasks, we create **"skills"** - special instructions that tell Claude exactly what to do. Some skills are just text instructions (like a recipe), but others need **Python code** (like a calculator program) to do the work quickly and accurately.

**This document explains:**
- What skills are and how they work
- Why some skills need Python code
- What UV is and why we use it instead of regular pip
- How to set up your computer so Python-based skills work correctly
- Different ways to install and use this project

### When Do You Need This Document?

| Situation | Do You Need This? |
|-----------|-------------------|
| You want to run QA (quality check) on LaTeX documents | Yes |
| You want to create Hebrew-English academic books | Yes |
| You're developing new skills with Python tools | Yes |
| You just want to chat with Claude CLI | No |
| You're using skills that are pure text (no Python) | No |

---

## 2. Understanding Claude CLI Skills

### What is a Skill?

Think of a **skill** like a recipe card for Claude. Instead of explaining the same task every time, you write the instructions once, and Claude follows them whenever you ask.

**Example without a skill:**
```
You: "Please check my LaTeX document for Hebrew text direction problems.
      Look for numbers that aren't wrapped in \en{}, English words in
      Hebrew paragraphs, TikZ diagrams without english environment..."
```

**Example with a skill:**
```
You: /qa-super "check my document"
```

The skill contains all those detailed instructions, so you don't have to repeat them.

### Parts of a Skill

Every skill lives in a folder with at least one file:

```
my-skill/
├── skill.md          # Required: The instructions (like a recipe)
├── tool.py           # Optional: Python code for fast/accurate work
├── templates/        # Optional: Pre-made text patterns
└── fixtures/         # Optional: Test files
```

#### skill.md (Required)
This is a text file with instructions. It tells Claude:
- What this skill does
- When to use it
- Step-by-step instructions
- Rules to follow

#### tool.py (Optional but Important)
This is Python code that does the actual work. It's used when:
- We need exact pattern matching (like finding Hebrew characters)
- We need speed (checking 1000 lines of code)
- We need consistency (same check = same result, every time)

**Think of it like this:**
- `skill.md` = The recipe that explains what to cook
- `tool.py` = The food processor that does the chopping

---

## 3. What are QA and BC Skills?

### QA Skills (Quality Assurance)

**QA skills check your work for problems.** They're like a teacher who reviews your homework before you submit it.

**QA = "Quality Assurance"** = Making sure everything is correct

QA skills look for issues like:
- Hebrew text going the wrong direction (right-to-left problems)
- Code blocks that will break when compiled
- Images that won't display correctly
- Numbers and English words not properly formatted

### BC Skills (Book Creator)

**BC skills create content for academic books.** They're like a team of writers who each specialize in something different.

**BC = "Book Creator"** = Making new content

BC skills create:
- Chapter content in academic style
- Diagrams and figures
- Code examples
- Mathematical formulas
- Citations and references

### How QA and BC Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                     THE BOOK CREATION PIPELINE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   STEP 1: BC Skills CREATE Content                              │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│   │bc-content│ │bc-drawing│ │bc-code  │ │bc-math  │              │
│   │ (text)   │ │(diagrams)│ │(examples)│ │(formulas)│             │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
│        │           │           │           │                     │
│        └───────────┴───────────┴───────────┘                     │
│                         │                                        │
│                         ▼                                        │
│   STEP 2: QA Skills CHECK Content                               │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│   │qa-BiDi  │ │qa-code  │ │qa-table │ │qa-typeset│              │
│   │(text dir)│ │(code)   │ │(tables) │ │(compile) │              │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
│        │           │           │           │                     │
│        └───────────┴───────────┴───────────┘                     │
│                         │                                        │
│                         ▼                                        │
│   STEP 3: Fix Any Problems Found                                │
│                         │                                        │
│                         ▼                                        │
│   STEP 4: Compile Final PDF                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Skill vs Tool: When to Use What

### The Big Question: LLM Text or Python Code?

When creating a skill, you must decide: should this be done by Claude (LLM) reading instructions, or by Python code running automatically?

### Comparison Table

| Aspect | Skill (LLM Text) | Tool (Python Code) |
|--------|------------------|-------------------|
| **What it is** | Instructions Claude reads | Code computer runs |
| **Speed** | Slower (Claude thinks) | Fast (instant) |
| **Creativity** | High (can adapt) | None (follows rules) |
| **Consistency** | May vary slightly | Always the same |
| **Token cost** | Uses API tokens | Free (local) |
| **Best for** | Writing, decisions, creativity | Checking, counting, patterns |

### Decision Guide

**Use Skill (LLM Text) when:**
- You need creative writing (chapter content, explanations)
- The task requires understanding context
- You need to make decisions based on meaning
- The output should be different each time

**Use Tool (Python Code) when:**
- You're checking for specific patterns (regex)
- You need exact counts or measurements
- The same input should always give the same output
- Speed matters (checking many files)
- You're doing math or data processing

### Real Examples

| Task | Best Choice | Why |
|------|-------------|-----|
| Write a chapter introduction | Skill (LLM) | Needs creativity and writing ability |
| Find Hebrew characters in code | Tool (Python) | Pattern matching, must be consistent |
| Decide if a diagram is clear | Skill (LLM) | Needs understanding and judgment |
| Count lines in a file | Tool (Python) | Simple counting, must be exact |
| Create an analogy to explain AI | Skill (LLM) | Needs creativity |
| Check if all figures are referenced | Tool (Python) | Pattern matching across file |

---

## 5. Where Are Skills Located?

### Global Skills Location

**Global skills** work from anywhere on your computer. They live in your user folder:

```
Windows:
C:\Users\YOUR_USERNAME\.claude\skills\

Linux/WSL:
/home/YOUR_USERNAME/.claude/skills/

macOS:
/Users/YOUR_USERNAME/.claude/skills/
```

### Global Skills Folder Structure

```
C:\Users\YOUR_USERNAME\.claude\
├── CLAUDE.md                    # Your global instructions
├── settings.json                # Claude CLI settings
│
└── skills/                      # All your global skills
    │
    ├── qa-super/                # QA orchestrator skill
    │   ├── skill.md             # Skill instructions
    │   └── tool.py              # Python detection code
    │
    ├── qa-BiDi/                 # Bidirectional text checker
    │   ├── skill.md
    │   └── tool.py
    │
    ├── qa-code/                 # Code block checker
    │   ├── skill.md
    │   └── tool.py
    │
    ├── bc-content/              # Content creator
    │   └── skill.md
    │
    ├── bc-drawing/              # Diagram creator
    │   ├── skill.md
    │   ├── tool.py              # TikZ validator
    │   └── templates/           # Diagram templates
    │
    └── [more skills...]
```

### Project-Local Skills

**Project skills** only work when you're in that project folder. They live in:

```
your-project/
├── .claude/
│   └── skills/              # Skills for THIS project only
│       └── my-local-skill/
│           └── skill.md
└── [your project files]
```

### Where is skill-python-base?

The **skill-python-base** project contains Python code that skills need to run. It's a development project, not a skill folder.

**Recommended installation location:**
```
Windows:
C:\25D\GeneralLearning\skill-python-base\

Linux/WSL:
~/projects/skill-python-base/
```

**Why this location?**
- Short path (less typing)
- Away from system folders (safe)
- Easy to remember
- Not inside `.claude` (which is for skills only)

---

## 6. What is UV?

### UV vs pip: Why We Use UV

**UV** is a super-fast Python package manager written in Rust. It's like `pip` but **10-100x faster**.

Think of it like this:
- `pip` = A car that gets you there
- `uv` = A sports car that gets you there much faster

### Speed Comparison

| Operation | pip | uv |
|-----------|-----|-----|
| Create virtual environment | 5-10 seconds | < 1 second |
| Install 50 packages | 30-60 seconds | 2-5 seconds |
| Resolve dependencies | 10-30 seconds | < 1 second |

### UV Commands vs pip Commands

| Task | Old way (pip) | New way (uv) |
|------|---------------|--------------|
| Create virtual environment | `python -m venv .venv` | `uv venv` |
| Install package | `pip install requests` | `uv pip install requests` |
| Install from requirements | `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| Install editable | `pip install -e .` | `uv pip install -e .` |
| Build wheel | `pip install build && python -m build` | `uv build` |
| Show package info | `pip show package` | `uv pip show package` |
| List packages | `pip list` | `uv pip list` |
| Sync from lock file | (no equivalent) | `uv sync` |

### Installing UV

**Windows PowerShell:**
```powershell
# Method 1: Using PowerShell installer (recommended)
irm https://astral.sh/uv/install.ps1 | iex

# Method 2: Using pip (if you already have Python)
pip install uv

# Method 3: Using winget
winget install astral-sh.uv

# Verify installation
uv --version
```

**Windows CMD:**
```cmd
REM Using pip
pip install uv

REM Verify
uv --version
```

**WSL / Linux:**
```bash
# Method 1: Using shell installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Method 2: Using pip
pip install uv

# Verify installation
uv --version
```

### UV Lock File (uv.lock)

UV creates a `uv.lock` file that records the exact version of every package. This ensures everyone on the team has identical packages.

```
pyproject.toml     → What packages you WANT
uv.lock            → What exact versions you HAVE
```

**Why is this important?**
- **Without lock file:** "Works on my machine" problems
- **With lock file:** Everyone has identical setup

---

## 7. Installing This Project

### Step 1: Install UV First

If you don't have UV installed, install it now:

**Windows PowerShell:**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**WSL / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Download from GitHub

#### Using Git (Recommended)

**Windows PowerShell:**
```powershell
# Navigate to where you want the project
cd C:\25D\GeneralLearning

# Clone the repository
git clone https://github.com/YOUR_ORG/skill-python-base.git

# Enter the project folder
cd skill-python-base
```

**Windows CMD:**
```cmd
REM Navigate to where you want the project
cd C:\25D\GeneralLearning

REM Clone the repository
git clone https://github.com/YOUR_ORG/skill-python-base.git

REM Enter the project folder
cd skill-python-base
```

**WSL (Linux on Windows):**
```bash
# Navigate to where you want the project
cd ~/projects

# Clone the repository
git clone https://github.com/YOUR_ORG/skill-python-base.git

# Enter the project folder
cd skill-python-base
```

#### Download ZIP (Alternative)

1. Go to `https://github.com/YOUR_ORG/skill-python-base`
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract to `C:\25D\GeneralLearning\skill-python-base`

### Step 3: Create UV Environment and Install Dependencies

This project requires Python 3.10 or newer.

**Windows PowerShell:**
```powershell
# Go to project folder
cd C:\25D\GeneralLearning\skill-python-base

# Create virtual environment using UV (super fast!)
uv venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# You'll see (.venv) appear in your prompt:
# (.venv) PS C:\25D\GeneralLearning\skill-python-base>

# Install all dependencies using UV (uses uv.lock for exact versions)
uv sync

# Or if there's no uv.lock, install from pyproject.toml
uv pip install -e .
```

**Windows CMD:**
```cmd
REM Go to project folder
cd C:\25D\GeneralLearning\skill-python-base

REM Create virtual environment using UV
uv venv

REM Activate the virtual environment
.venv\Scripts\activate.bat

REM Install dependencies
uv sync
```

**WSL / Linux:**
```bash
# Go to project folder
cd ~/projects/skill-python-base

# Create virtual environment using UV
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install all dependencies
uv sync
```

### What Each Command Does

| Command | What It Does |
|---------|--------------|
| `uv venv` | Creates `.venv` folder with isolated Python environment (< 1 second!) |
| `.\.venv\Scripts\Activate.ps1` | Tells PowerShell to use this project's Python |
| `uv sync` | Installs exact package versions from `uv.lock` file |
| `uv pip install -e .` | Installs this project in editable mode |

---

## 8. Why Can't We Use Regular Global Skills?

### The Problem

Regular global skills are just text files (`skill.md`). Claude reads them and follows the instructions. But our QA and BC skills have **Python tools** (`tool.py`) that need special Python packages to run.

**Imagine this situation:**
```
You type: /qa-super "check my document"

Claude tries to run: tool.py
Tool.py tries to: import qa_engine
Python says: ERROR! I don't know what qa_engine is!
```

### Why This Happens

1. **Skills are just text files** - Claude reads `skill.md` and sees "run tool.py"
2. **tool.py needs Python packages** - It has `import qa_engine` at the top
3. **Python doesn't know where qa_engine is** - It's not installed globally

### The Solution

We need to tell Python where to find the `qa_engine` package. There are several ways to do this, explained in the next section.

### Visual Explanation

```
WITHOUT SETUP:
┌─────────────────────────────────────────────────────────────────┐
│  Claude CLI                                                      │
│     │                                                            │
│     ▼                                                            │
│  /qa-super "check document"                                     │
│     │                                                            │
│     ▼                                                            │
│  Reads: C:\Users\you\.claude\skills\qa-super\skill.md           │
│     │                                                            │
│     ▼                                                            │
│  Runs: tool.py                                                  │
│     │                                                            │
│     ▼                                                            │
│  tool.py: "import qa_engine"                                    │
│     │                                                            │
│     ▼                                                            │
│  Python: "ModuleNotFoundError: No module named 'qa_engine'"  ❌ │
└─────────────────────────────────────────────────────────────────┘

WITH SETUP:
┌─────────────────────────────────────────────────────────────────┐
│  Claude CLI                                                      │
│     │                                                            │
│     ▼                                                            │
│  /qa-super "check document"                                     │
│     │                                                            │
│     ▼                                                            │
│  Reads: C:\Users\you\.claude\skills\qa-super\skill.md           │
│     │                                                            │
│     ▼                                                            │
│  Runs: tool.py                                                  │
│     │                                                            │
│     ▼                                                            │
│  tool.py: "import qa_engine"                                    │
│     │                                                            │
│     ▼                                                            │
│  Python finds qa_engine (installed via UV)                   ✅ │
│     │                                                            │
│     ▼                                                            │
│  Returns: List of issues found in document                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Environment Setup Options

There are 5 ways to make Python find the `qa_engine` package. Each has pros and cons.

---

### Option 1: Local Project Usage with UV (Best for Development)

**What is this?**
You work directly inside the skill-python-base project folder. UV creates and manages the virtual environment with all packages installed.

**What's unique?**
- Fastest setup (UV is lightning fast)
- Changes to code are immediately available
- Exact package versions via `uv.lock`
- Best for developing and testing skills

**When to use:**
- You're developing new skills
- You're testing changes to qa_engine
- You want the simplest and fastest setup

**When NOT to use:**
- You need to run skills from other folders
- You're just using skills, not developing them

#### Windows PowerShell

```powershell
# Step 1: Go to the project folder
cd C:\25D\GeneralLearning\skill-python-base

# Step 2: Create UV environment (if not already created)
uv venv

# Step 3: Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# You'll see (.venv) appear in your prompt:
# (.venv) PS C:\25D\GeneralLearning\skill-python-base>

# Step 4: Sync dependencies (installs exact versions from uv.lock)
uv sync

# Step 5: Run Claude CLI
claude

# Step 6: Now you can use skills!
# Type this in the Claude CLI:
/qa-super "Run QA on my document"
```

#### Windows CMD

```cmd
REM Step 1: Go to the project folder
cd C:\25D\GeneralLearning\skill-python-base

REM Step 2: Create UV environment
uv venv

REM Step 3: Activate the virtual environment
.venv\Scripts\activate.bat

REM Step 4: Sync dependencies
uv sync

REM Step 5: Run Claude CLI
claude
```

#### WSL (Linux on Windows)

```bash
# Step 1: Go to the project folder
cd ~/projects/skill-python-base

# Step 2: Create UV environment
uv venv

# Step 3: Activate the virtual environment
source .venv/bin/activate

# Step 4: Sync dependencies
uv sync

# Step 5: Run Claude CLI
claude
```

#### Expected Output

When you run `/qa-super "Run QA on my document"`:

```
📋 QA Super Orchestrator Starting...

Phase 0: CLS Version Check
✅ CLS Version: CURRENT (v5.11.5)

Phase 1: Running Detection Families
├── qa-BiDi: Running...
├── qa-code: Running...
├── qa-table: Running...
└── qa-typeset: Running...

Results:
┌──────────────┬────────┬────────┬───────┐
│ Family       │ Issues │ Fixed  │ Status│
├──────────────┼────────┼────────┼───────┤
│ qa-BiDi      │ 3      │ 3      │ ✅    │
│ qa-code      │ 1      │ 1      │ ✅    │
│ qa-table     │ 0      │ 0      │ ✅    │
│ qa-typeset   │ 2      │ -      │ ⚠️    │
└──────────────┴────────┴────────┴───────┘

📄 Report saved to: qa-orchestration/QA-REPORT.md
```

**Where is the output?**
- **Console:** You see the summary above
- **Report file:** `qa-orchestration/QA-REPORT.md` in your document's folder
- **Task file:** `qa-orchestration/QA-TASKS.md` with detailed status

---

### Option 2: Global Package Installation with UV (Best for Regular Use)

**What is this?**
You install `qa_engine` as a Python package on your computer using UV. After installation, it works from anywhere.

**What's unique?**
- Works from any folder
- No need to activate virtual environment each time
- Super fast installation with UV
- "Just works" after setup

**When to use:**
- You're done developing and want to use skills regularly
- You want skills to work from any project folder
- You don't want to think about virtual environments

**When NOT to use:**
- You're actively developing qa_engine (use editable mode instead)
- You need to test unreleased changes

#### Understanding the Commands

**What is "editable mode" (`uv pip install -e`)?**

Editable mode creates a link from Python to your source code folder. When you change the code, the changes are immediately available - no reinstall needed.

```
Normal install:         Editable install:
┌─────────────┐         ┌─────────────┐
│ Your code   │         │ Your code   │
│ folder      │         │ folder      │◄─────┐
└──────┬──────┘         └─────────────┘      │
       │ copy                                │ link
       ▼                                     │
┌─────────────┐         ┌─────────────┐      │
│ Python      │         │ Python      │──────┘
│ packages    │         │ packages    │
└─────────────┘         └─────────────┘
Changes need reinstall   Changes work immediately
```

**What is a "wheel" file?**

A wheel (`.whl` file) is like a ZIP file containing your Python package. It's the standard way to distribute Python packages.

```
qa_engine-1.0.0-py3-none-any.whl
    │       │    │   │    │
    │       │    │   │    └── Works on any platform
    │       │    │   └─────── No specific OS required
    │       │    └─────────── Python 3
    │       └──────────────── Version 1.0.0
    └──────────────────────── Package name
```

#### Method A: Editable Install with UV (Recommended for Development)

**Windows PowerShell:**
```powershell
# Install qa_engine in "editable" mode using UV
# -e means "editable" - changes to code work immediately
uv pip install -e C:\25D\GeneralLearning\skill-python-base

# Verify installation
uv pip show qa_engine
# Should show: Name: qa_engine, Version: 1.0.0, Location: ...
```

**What this command does:**
1. Reads `pyproject.toml` in the project
2. Creates a link from Python's package folder to your source code
3. Now `import qa_engine` works from anywhere
4. Any code changes are immediately available (no reinstall needed)

**Windows CMD:**
```cmd
uv pip install -e C:\25D\GeneralLearning\skill-python-base
uv pip show qa_engine
```

**WSL:**
```bash
uv pip install -e ~/projects/skill-python-base
uv pip show qa_engine
```

#### Method B: Build and Install Wheel with UV (For Distribution)

**Windows PowerShell:**
```powershell
# Step 1: Go to project folder
cd C:\25D\GeneralLearning\skill-python-base

# Step 2: Build the wheel using UV (super fast!)
uv build
# This creates dist/qa_engine-1.0.0-py3-none-any.whl

# Step 3: Install the wheel globally
uv pip install dist\qa_engine-1.0.0-py3-none-any.whl
# This copies the package to Python's site-packages folder

# Step 4: Verify installation
uv pip show qa_engine
```

**Where does the wheel get installed?**

```powershell
# Find where Python packages are installed
python -c "import site; print(site.getsitepackages())"
# Output: ['C:\\Users\\you\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages']

# After installation, you'll find:
# C:\Users\you\AppData\Local\Programs\Python\Python311\Lib\site-packages\qa_engine\
```

**Windows CMD:**
```cmd
cd C:\25D\GeneralLearning\skill-python-base
uv build
uv pip install dist\qa_engine-1.0.0-py3-none-any.whl
uv pip show qa_engine
```

**WSL:**
```bash
cd ~/projects/skill-python-base
uv build
uv pip install dist/qa_engine-1.0.0-py3-none-any.whl
uv pip show qa_engine
```

#### Verifying Installation

```powershell
# Test 1: Check if package is listed
uv pip list | findstr qa_engine
# Should show: qa_engine    1.0.0

# Test 2: Check package details
uv pip show qa_engine
# Should show name, version, location, etc.

# Test 3: Try importing
python -c "from qa_engine import api; print('SUCCESS!')"
# Should print: SUCCESS!

# Test 4: Check version
python -c "from qa_engine import __version__; print(__version__)"
# Should print: 1.0.0
```

---

### Option 3: Path Injection in tool.py (Simplest Code Change)

**What is this?**
Each `tool.py` file tells Python where to find qa_engine by adding the path at the start of the code.

**What's unique?**
- No installation required
- Each tool handles its own path
- Works immediately after code change
- No UV or pip needed

**When to use:**
- You can't or don't want to install packages globally
- You want each skill to be self-contained
- Quick testing without setup

**When NOT to use:**
- You have many tools (tedious to update all)
- The project path might change
- You want cleaner code

#### How to Modify tool.py

Open the skill's `tool.py` file and add these lines at the very top:

```python
#!/usr/bin/env python3
"""
Tool with path injection.
This tool adds the qa_engine path before importing.
"""
import sys
from pathlib import Path

# ============================================================
# PATH INJECTION - Add this section to any tool.py
# ============================================================
# This tells Python where to find the qa_engine package
# Change this path to match your installation location!

# For Windows:
QA_ENGINE_PATH = Path("C:/25D/GeneralLearning/skill-python-base/src")

# For WSL/Linux, use this instead:
# QA_ENGINE_PATH = Path.home() / "projects" / "skill-python-base" / "src"

# Add to Python's search path (at the beginning, so it's found first)
sys.path.insert(0, str(QA_ENGINE_PATH))
# ============================================================

# Now imports work!
from qa_engine.validators import BiDiDetector

def detect(content: str, file_path: str = "") -> list:
    """Detect BiDi issues in content."""
    detector = BiDiDetector()
    issues = detector.detect(content, file_path)
    return [i.to_dict() for i in issues]

if __name__ == "__main__":
    # Test the tool
    sample = r"\hebrewchapter{מבוא} בשנת 2024 פותח מודל AI חדש."
    results = detect(sample, "test.tex")
    print(f"Found {len(results)} issues")
```

**What `sys.path.insert(0, str(QA_ENGINE_PATH))` does:**

```
Python's Search Path (sys.path):
Before: ['', 'C:\\Python311\\Lib', 'C:\\Python311\\Lib\\site-packages', ...]
After:  ['C:\\25D\\...\\skill-python-base\\src', '', 'C:\\Python311\\Lib', ...]
         ▲
         └── Now Python looks here FIRST for imports
```

---

### Option 4: UV Virtual Environment Activation in tool.py (Full Isolation)

**What is this?**
The tool.py runs a subprocess using the project's UV-managed Python interpreter, which has all packages installed with exact versions.

**What's unique?**
- Complete isolation from system Python
- Uses exact versions from `uv.lock`
- Most reliable for complex dependencies
- Benefits from UV's speed

**When to use:**
- You have conflicting package versions
- You need exact version control
- The tool needs many packages

**When NOT to use:**
- Simple tools (overhead is unnecessary)
- You need maximum speed
- You're debugging (harder to trace)

#### How to Modify tool.py

```python
#!/usr/bin/env python3
"""
Tool that runs using the project's UV-managed virtual environment.
This ensures all dependencies are available with exact versions.
"""
import subprocess
import sys
import json
from pathlib import Path

# ============================================================
# UV VIRTUAL ENVIRONMENT CONFIGURATION
# ============================================================
# Path to the skill-python-base project
PROJECT_PATH = Path("C:/25D/GeneralLearning/skill-python-base")

# Path to Python in the UV-managed virtual environment
# Windows:
VENV_PYTHON = PROJECT_PATH / ".venv" / "Scripts" / "python.exe"
# Linux/WSL:
# VENV_PYTHON = PROJECT_PATH / ".venv" / "bin" / "python"
# ============================================================

def run_with_uv_venv(script_content: str) -> tuple[str, str]:
    """
    Execute Python script using project's UV-managed virtual environment.

    Args:
        script_content: Python code to execute

    Returns:
        Tuple of (stdout, stderr)
    """
    if not VENV_PYTHON.exists():
        raise FileNotFoundError(
            f"UV virtual environment Python not found at {VENV_PYTHON}\n"
            f"Please run: cd {PROJECT_PATH} && uv venv && uv sync"
        )

    result = subprocess.run(
        [str(VENV_PYTHON), "-c", script_content],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_PATH)
    )
    return result.stdout, result.stderr

def detect_bidi_issues(content: str, file_path: str = "") -> list:
    """Detect BiDi issues using the project's UV environment."""

    # This Python code will run in the UV virtual environment
    script = f'''
import json
from qa_engine.validators import BiDiDetector

detector = BiDiDetector()
content = {repr(content)}
file_path = {repr(file_path)}
issues = detector.detect(content, file_path)
print(json.dumps([i.to_dict() for i in issues]))
'''

    stdout, stderr = run_with_uv_venv(script)

    if stderr:
        print(f"Warning: {stderr}", file=sys.stderr)

    return json.loads(stdout) if stdout.strip() else []

if __name__ == "__main__":
    # Test the tool
    sample = r"\hebrewchapter{מבוא} בשנת 2024 פותח מודל AI חדש."
    results = detect_bidi_issues(sample, "test.tex")
    print(f"Found {len(results)} issues")
    for issue in results:
        print(f"  - {issue['rule']}: {issue['message']}")
```

---

### Option 5: Environment Variables (Most Flexible)

**What is this?**
You set a system-wide variable that tells Python where to find qa_engine. tool.py reads this variable.

**What's unique?**
- Path is configurable without changing code
- Works across all tools automatically
- Can change path without editing files

**When to use:**
- Different computers have different paths
- You want one configuration for all tools
- Team members have different setups

**When NOT to use:**
- You forget what environment variables you set
- Simple single-user setup
- You want everything in one place

#### Setting Environment Variables

**Windows PowerShell (Temporary - Current Session Only):**
```powershell
# Set for current session
$env:QA_ENGINE_PATH = "C:\25D\GeneralLearning\skill-python-base\src"

# Verify it's set
echo $env:QA_ENGINE_PATH
```

**Windows PowerShell (Permanent - Survives Restart):**
```powershell
# Add to your PowerShell profile
# First, find your profile location:
echo $PROFILE
# Usually: C:\Users\you\Documents\PowerShell\Microsoft.PowerShell_profile.ps1

# Create profile if it doesn't exist:
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# Add the environment variable to your profile:
Add-Content -Path $PROFILE -Value '$env:QA_ENGINE_PATH = "C:\25D\GeneralLearning\skill-python-base\src"'

# Reload profile (or restart PowerShell):
. $PROFILE

# Verify:
echo $env:QA_ENGINE_PATH
```

**Windows CMD (Temporary):**
```cmd
set QA_ENGINE_PATH=C:\25D\GeneralLearning\skill-python-base\src
echo %QA_ENGINE_PATH%
```

**Windows CMD (Permanent):**
```cmd
REM Set system-wide (requires admin rights)
setx QA_ENGINE_PATH "C:\25D\GeneralLearning\skill-python-base\src"

REM Or use System Properties:
REM 1. Press Win+R, type: sysdm.cpl
REM 2. Click "Environment Variables"
REM 3. Under "User variables", click "New"
REM 4. Variable name: QA_ENGINE_PATH
REM 5. Variable value: C:\25D\GeneralLearning\skill-python-base\src
```

**WSL / Linux (Temporary):**
```bash
export QA_ENGINE_PATH=~/projects/skill-python-base/src
echo $QA_ENGINE_PATH
```

**WSL / Linux (Permanent):**
```bash
# Add to your shell profile (~/.bashrc for bash, ~/.zshrc for zsh)
echo 'export QA_ENGINE_PATH=~/projects/skill-python-base/src' >> ~/.bashrc

# Reload profile
source ~/.bashrc

# Verify
echo $QA_ENGINE_PATH
```

#### Using in tool.py

```python
#!/usr/bin/env python3
"""Tool that uses environment variable for path."""
import os
import sys
from pathlib import Path

# ============================================================
# ENVIRONMENT VARIABLE PATH INJECTION
# ============================================================
qa_path = os.environ.get("QA_ENGINE_PATH")

if qa_path:
    sys.path.insert(0, qa_path)
    print(f"Using qa_engine from: {qa_path}")
else:
    print("WARNING: QA_ENGINE_PATH not set!")
    print("Set it with:")
    print("  PowerShell: $env:QA_ENGINE_PATH = 'C:\\path\\to\\skill-python-base\\src'")
    print("  CMD:        set QA_ENGINE_PATH=C:\\path\\to\\skill-python-base\\src")
    print("  WSL/Linux:  export QA_ENGINE_PATH=~/path/to/skill-python-base/src")
# ============================================================

# Now try to import
try:
    from qa_engine.validators import BiDiDetector
except ImportError as e:
    print(f"ERROR: Could not import qa_engine: {e}")
    sys.exit(1)

def detect(content: str, file_path: str = "") -> list:
    detector = BiDiDetector()
    return [i.to_dict() for i in detector.detect(content, file_path)]
```

#### Verifying Environment Variable is Persistent

**PowerShell:**
```powershell
# Close PowerShell completely, then reopen
# Check if variable survived:
echo $env:QA_ENGINE_PATH

# If empty, the permanent setup didn't work
# Check your profile:
Get-Content $PROFILE | Select-String "QA_ENGINE"
```

**CMD:**
```cmd
REM Close CMD completely, then reopen
echo %QA_ENGINE_PATH%

REM If empty, use setx or System Properties
```

**WSL:**
```bash
# Close terminal completely, then reopen
echo $QA_ENGINE_PATH

# If empty, check your profile:
cat ~/.bashrc | grep QA_ENGINE
```

---

### Summary: Which Option Should You Choose?

| Option | Best For | Setup Difficulty | Maintenance |
|--------|----------|-----------------|-------------|
| **1. Local UV Project** | Development | Easy | Must be in folder |
| **2. Global UV Install** | Regular use | Medium | Reinstall on changes |
| **3. Path Injection** | Quick testing | Easy | Update each tool |
| **4. UV Venv Activation** | Complex deps | Hard | Most reliable |
| **5. Environment Var** | Team/multi-PC | Medium | One-time setup |

**My Recommendation:**
- **For development:** Option 1 (Local UV Project with `uv sync`)
- **For regular use:** Option 2 with editable install (`uv pip install -e`)
- **For sharing with team:** Option 5 (Environment Variables)

---

## 10. Complete Skills Reference Table

### QA Skills (Quality Assurance)

| Skill Name | Level | Mission | Has Python Tool? |
|------------|-------|---------|------------------|
| **qa-super** | L0 | Master orchestrator - coordinates all QA families | Yes |
| **qa-BiDi** | L1 | Bidirectional text family orchestrator | No (delegates) |
| **qa-BiDi-detect** | L2 | Detect RTL/LTR text direction issues | Yes |
| **qa-BiDi-detect-tikz** | L2 | Detect TikZ diagrams without english wrapper | Yes |
| **qa-BiDi-fix-text** | L2 | Fix text direction issues | Yes |
| **qa-BiDi-fix-numbers** | L2 | Wrap numbers with \en{} | Yes |
| **qa-BiDi-fix-tikz** | L2 | Add english wrapper to TikZ | Yes |
| **qa-code** | L1 | Code blocks family orchestrator | No (delegates) |
| **qa-code-detect** | L2 | Detect code block issues | Yes |
| **qa-code-fix-background** | L2 | Fix pythonbox overflow | Yes |
| **qa-code-fix-encoding** | L2 | Fix character encoding | Yes |
| **qa-table** | L1 | Table layout family orchestrator | No (delegates) |
| **qa-table-detect** | L2 | Detect table RTL issues | Yes |
| **qa-table-fix-columns** | L2 | Fix column order for RTL | Yes |
| **qa-typeset** | L1 | LaTeX compilation warnings | No (delegates) |
| **qa-typeset-detect** | L2 | Parse .log file for warnings | Yes |
| **qa-typeset-fix-hbox** | L2 | Fix overfull/underfull hbox | Yes |
| **qa-img** | L1 | Image and figure issues | No (delegates) |
| **qa-img-detect** | L2 | Find missing images | Yes |
| **qa-bib** | L1 | Bibliography issues | No (delegates) |
| **qa-bib-detect** | L2 | Find citation problems | Yes |
| **qa-infra** | L1 | Project structure | No (delegates) |
| **qa-cls-version-detect** | L2 | Check CLS version | Yes |
| **qa-cls-version-fix** | L2 | Update CLS file | Yes |

### BC Skills (Book Creator)

| Skill Name | Level | Mission | Has Python Tool? |
|------------|-------|---------|------------------|
| **bc-architect** | Worker | Chief architect - narrative flow, final review | No (creative) |
| **bc-content** | Worker | Content specialist - Harari-style writing | No (creative) |
| **bc-math** | Worker | Mathematical formulas and proofs | No (creative) |
| **bc-code** | Worker | Code examples and explanations | Yes (validator) |
| **bc-drawing** | Worker | TikZ diagrams and figures | Yes (validator) |
| **bc-academic-source** | Worker | Citations and bibliography | Yes (validator) |
| **bc-hebrew** | Worker | Hebrew language editor | No (creative) |
| **bc-source-research** | Worker | Find and collect sources | No (research) |

### Understanding the Levels

```
QA HIERARCHY:                      BC HIERARCHY:

   L0: qa-super                    Orchestrator: bc-architect
        │                               │
        ├── L1: qa-BiDi                 ├── bc-content
        │    ├── L2: qa-BiDi-detect     ├── bc-math
        │    ├── L2: qa-BiDi-fix-text   ├── bc-code
        │    └── L2: qa-BiDi-fix-tikz   ├── bc-drawing
        │                               ├── bc-academic-source
        ├── L1: qa-code                 ├── bc-hebrew
        │    ├── L2: qa-code-detect     └── bc-source-research
        │    └── L2: qa-code-fix-*
        │
        ├── L1: qa-table
        │    └── L2: qa-table-*
        │
        └── [more families...]
```

---

## 11. Troubleshooting

### Common Error: ModuleNotFoundError

```
Error: ModuleNotFoundError: No module named 'qa_engine'
```

**Solutions:**
1. Activate the UV virtual environment (Option 1)
2. Install the package globally with UV (Option 2)
3. Add path injection to tool.py (Option 3)
4. Set the environment variable (Option 5)

### Common Error: UV Not Found

```
Error: 'uv' is not recognized as an internal or external command
```

**Solution - Install UV:**

**PowerShell:**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**WSL/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Common Error: Virtual Environment Not Found

```
Error: The virtual environment .venv does not exist
```

**Solution:**
```powershell
cd C:\25D\GeneralLearning\skill-python-base
uv venv
.\.venv\Scripts\Activate.ps1
uv sync
```

### Common Error: Permission Denied (PowerShell)

```
Error: .ps1 cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Common Error: uv.lock Not Found

```
Error: No `uv.lock` found
```

**Solution:**
```powershell
# Create lock file from pyproject.toml
uv lock

# Then sync
uv sync
```

### Checking Your Setup

Run this diagnostic script:

```python
# Save as: check_setup.py

import sys
import os
import shutil

print("=" * 60)
print("SKILL-PYTHON-BASE SETUP DIAGNOSTIC")
print("=" * 60)

# Check UV installation
uv_path = shutil.which("uv")
print(f"\n1. UV Installation: {uv_path or 'NOT FOUND'}")
if not uv_path:
    print("   Install UV: irm https://astral.sh/uv/install.ps1 | iex")

# Check Python version
print(f"\n2. Python Version: {sys.version}")
if sys.version_info < (3, 10):
    print("   WARNING: Python 3.10+ recommended")

# Check environment variable
qa_path = os.environ.get("QA_ENGINE_PATH")
print(f"\n3. QA_ENGINE_PATH: {qa_path or 'NOT SET'}")

# Check if qa_engine is importable
print("\n4. qa_engine Import Test:")
try:
    import qa_engine
    print(f"   SUCCESS - Version: {qa_engine.__version__}")
    print(f"   Location: {qa_engine.__file__}")
except ImportError as e:
    print(f"   FAILED: {e}")

# Check virtual environment
venv = os.environ.get("VIRTUAL_ENV")
print(f"\n5. Virtual Environment: {venv or 'NOT ACTIVE'}")

print("\n" + "=" * 60)
```

Run it:
```powershell
python check_setup.py
```

---

## Appendix: Quick Reference Card

### UV Commands

| Task | Command |
|------|---------|
| Install UV | `irm https://astral.sh/uv/install.ps1 \| iex` |
| Create venv | `uv venv` |
| Sync dependencies | `uv sync` |
| Install package | `uv pip install package` |
| Install editable | `uv pip install -e .` |
| Build wheel | `uv build` |
| Show package | `uv pip show package` |
| List packages | `uv pip list` |
| Lock dependencies | `uv lock` |

### PowerShell Commands

```powershell
# Full setup from scratch
cd C:\25D\GeneralLearning\skill-python-base
uv venv
.\.venv\Scripts\Activate.ps1
uv sync

# Install package globally (editable)
uv pip install -e C:\25D\GeneralLearning\skill-python-base

# Set environment variable (permanent)
Add-Content $PROFILE '$env:QA_ENGINE_PATH = "C:\25D\GeneralLearning\skill-python-base\src"'

# Verify installation
uv pip show qa_engine
python -c "from qa_engine import api; print('OK')"
```

### CMD Commands

```cmd
REM Full setup
cd C:\25D\GeneralLearning\skill-python-base
uv venv
.venv\Scripts\activate.bat
uv sync

REM Install package globally
uv pip install -e C:\25D\GeneralLearning\skill-python-base

REM Set environment variable (permanent)
setx QA_ENGINE_PATH "C:\25D\GeneralLearning\skill-python-base\src"
```

### WSL Commands

```bash
# Full setup
cd ~/projects/skill-python-base
uv venv
source .venv/bin/activate
uv sync

# Install package globally (editable)
uv pip install -e ~/projects/skill-python-base

# Set environment variable (permanent)
echo 'export QA_ENGINE_PATH=~/projects/skill-python-base/src' >> ~/.bashrc
source ~/.bashrc
```

---

*End of Document*
