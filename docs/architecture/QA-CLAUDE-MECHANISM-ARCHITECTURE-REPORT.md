# QA Claude Mechanism Architecture Research Report

## Executive Summary

This report presents a comprehensive analysis of the existing Claude CLI QA skills system for Hebrew-English LaTeX documents. Based on deep research of 50+ skill files, we identify critical improvements needed to make the QA mechanism more **efficient, faster, reliable, token-conscious**, and **deterministic**.

**Key Findings:**
- Current system relies heavily on LLM reasoning for tasks that could be deterministic Python code
- Lack of centralized orchestration metrics and progress tracking
- No standardized test framework for skill validation
- Missing batch processing for large documents
- No mutex/semaphore mechanisms for concurrent agent coordination

**Recommended Architecture:**
- Hybrid skill/Python tool model
- Centralized QA orchestration engine with Python backend
- Standardized test framework with unit tests for each skill
- `insert_qa_skill` meta-skill for automated skill creation and integration

---

## Table of Contents

1. [Current Architecture Analysis](#1-current-architecture-analysis)
2. [Complete Skill Hierarchy](#2-complete-skill-hierarchy)
3. [Skill Capabilities Analysis](#3-skill-capabilities-analysis)
4. [Skill vs Python Code Evaluation](#4-skill-vs-python-code-evaluation)
5. [Recommended Architecture](#5-recommended-architecture)
6. [insert_qa_skill Mechanism](#6-insert_qa_skill-mechanism)
7. [Python Testing Framework](#7-python-testing-framework)
8. [Protocols and Procedures](#8-protocols-and-procedures)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Appendices](#10-appendices)

---

## 1. Current Architecture Analysis

### 1.1 Hierarchical Structure

```
Level 0: Super Orchestrator
├── qa-super (Master coordinator)
├── qa-mechanism-improver (Meta-skill for improvements)
└── Coordination files:
    ├── QA-CLAUDE.md (architecture rules)
    └── QA-TASKS.md (status tracking)

Level 1: Family Orchestrators (6 families)
├── qa-BiDi (RTL/LTR text direction)
├── qa-table (Table formatting)
├── qa-code (Code blocks)
├── qa-img (Images/figures)
├── qa-typeset (LaTeX compilation warnings)
└── qa-infra (Project infrastructure)

Level 2: Detection & Fix Skills (40+ skills)
├── *-detect skills (problem detection)
├── *-fix-* skills (problem correction)
└── *-validate skills (verification)
```

### 1.2 Current Strengths

| Strength | Description |
|----------|-------------|
| Modular design | Clear separation between detection and fix skills |
| Hierarchical coordination | L0 → L1 → L2 delegation pattern |
| Version tracking | Each skill has version history |
| Documentation | Comprehensive markdown documentation per skill |

### 1.3 Current Weaknesses

| Weakness | Impact | Severity |
|----------|--------|----------|
| LLM-dependent detection | High token consumption, inconsistent results | CRITICAL |
| No batch processing | Cannot handle large documents efficiently | HIGH |
| No test framework | No way to verify skills work correctly | HIGH |
| Manual integration | Adding new skills requires manual updates | MEDIUM |
| No progress metrics | Cannot measure QA progress objectively | MEDIUM |
| No parallel coordination | Agents may conflict on shared resources | MEDIUM |

---

## 2. Complete Skill Hierarchy

### 2.1 Level 0 - Super Orchestrators

| Skill | Version | Purpose | Calls | Called By |
|-------|---------|---------|-------|-----------|
| qa-super | 1.5.0 | Master QA coordinator | All L1 families | /full-pdf-qa, user |
| qa-orchestrator | 2.0.0 | DEPRECATED wrapper | qa-super | Legacy calls |
| qa-mechanism-improver | 1.0.0 | Investigate and fix QA failures | L2 skills | /fix-qa-mechanism |

### 2.2 Level 1 - Family Orchestrators

| Skill | Version | Domain | Children | Detection Priority |
|-------|---------|--------|----------|-------------------|
| qa-BiDi | 2.5.0 | RTL/LTR text | 10 skills | ALWAYS for Hebrew |
| qa-table | 2.1.0 | Table layouts | 8 skills | If tables present |
| qa-code | 2.2.0 | Code blocks | 6 skills | If code present |
| qa-img | 3.0.0 | Images/figures | 4 skills | If figures present |
| qa-typeset | 1.3.0 | LaTeX warnings | 10 skills | ALWAYS after compile |
| qa-infra | 2.3.0 | Project structure | 8 skills | On request |
| qa-bib | 1.0.0 | Bibliography | 2 skills | If citations present |

### 2.3 Level 2 - Detection Skills (Complete List)

#### qa-BiDi Family
| Skill | Version | Purpose | Detection Rules |
|-------|---------|---------|-----------------|
| qa-BiDi-detect | 2.8.0 | General BiDi issues | 15 rules |
| qa-heb-math-detect | 1.0.0 | Hebrew in math mode | 1 rule |
| qa-BiDi-detect-tikz | 1.0.0 | TikZ without english wrapper | 1 rule |
| qa-cls-toc-detect | 1.0.0 | CLS/TOC BiDi issues | 1 rule |

#### qa-table Family
| Skill | Version | Purpose | Detection Rules |
|-------|---------|---------|-----------------|
| qa-table-detect | 1.0.0 | Table layout issues | 3 rules |
| qa-table-fancy-detect | 1.0.0 | Plain/unstyled tables | 1 rule |
| qa-table-overflow-detect | 1.0.0 | Wide tables without resizebox | 1 rule |

#### qa-code Family
| Skill | Version | Purpose | Detection Rules |
|-------|---------|---------|-----------------|
| qa-code-detect | 1.3.0 | Code block issues | 6 phases |
| qa-code-background-detect | 1.1.0 | pythonbox without english wrapper | 1 rule |

#### qa-img Family
| Skill | Version | Purpose | Detection Rules |
|-------|---------|---------|-----------------|
| qa-img-detect | 1.0.0 | Missing images | 2 rules |

#### qa-typeset Family
| Skill | Version | Purpose | Detection Rules |
|-------|---------|---------|-----------------|
| qa-typeset-detect | 1.5.0 | LaTeX log warnings | 10+ patterns |
| qa-mdframed-detect | 1.0.0 | mdframed bad breaks | 1 rule |
| qa-section-orphan-detect | 1.0.0 | Orphan sections | 1 rule |

#### qa-infra Family
| Skill | Version | Purpose | Detection Rules |
|-------|---------|---------|-----------------|
| qa-infra-scan | 1.0.0 | Project structure analysis | N/A |
| qa-cls-version-detect | 1.0.0 | CLS version check | 3 rules |
| qa-infra-subfiles-detect | 1.0.0 | Missing subfiles preamble | 3 rules |

#### qa-bib Family
| Skill | Version | Purpose | Detection Rules |
|-------|---------|---------|-----------------|
| qa-bib-detect | 1.0.0 | Citation/bibliography issues | 5 rules |

### 2.4 Level 2 - Fix Skills (Complete List)

#### qa-BiDi Family Fixes
| Skill | Version | Purpose | Fix Patterns |
|-------|---------|---------|--------------|
| qa-BiDi-fix-text | 1.5.0 | Text direction correction | 10 patterns |
| qa-BiDi-fix-numbers | 1.2.0 | Number LTR rendering | 6 patterns |
| qa-BiDi-fix-tcolorbox | 1.0.0 | Box rendering BiDi-safe | 1 pattern |
| qa-BiDi-fix-sections | 1.0.0 | Section numbering | 1 pattern |
| qa-heb-math-fix | 1.0.0 | Hebrew in math mode | 1 pattern |
| qa-BiDi-fix-tikz | 1.0.0 | TikZ english wrapper | 1 pattern |

#### qa-table Family Fixes
| Skill | Version | Purpose | Fix Patterns |
|-------|---------|---------|--------------|
| qa-table-fix-columns | 1.0.0 | Column order correction | 1 pattern |
| qa-table-fix-captions | 1.0.0 | Caption alignment | 1 pattern |
| qa-table-fix-alignment | 1.0.0 | Cell alignment | 1 pattern |
| qa-table-fancy-fix | 1.0.0 | Convert to fancy styled | 1 pattern |
| qa-table-overflow-fix | 1.0.0 | Add resizebox wrapper | 1 pattern |

#### qa-code Family Fixes
| Skill | Version | Purpose | Fix Patterns |
|-------|---------|---------|--------------|
| qa-code-fix-background | 2.0.0 | Add english wrapper | 1 pattern |
| qa-code-fix-encoding | 1.0.0 | Character encoding | 3 patterns |
| qa-code-fix-direction | 1.0.0 | Text direction | 1 pattern |
| qa-code-fix-emoji | 1.0.0 | Remove/replace emoji | 1 pattern |

#### qa-img Family Fixes
| Skill | Version | Purpose | Fix Patterns |
|-------|---------|---------|--------------|
| qa-img-fix-paths | 1.0.0 | Image path correction | 1 pattern |
| qa-img-fix-missing | 1.0.0 | Create missing images | N/A |
| qa-img-validate | 1.0.0 | Verify image rendering | N/A |

#### qa-typeset Family Fixes
| Skill | Version | Purpose | Fix Patterns |
|-------|---------|---------|--------------|
| qa-typeset-fix-hbox | 1.0.0 | Overfull/Underfull hbox | 3 patterns |
| qa-typeset-fix-vbox | 1.0.0 | Overfull/Underfull vbox | 2 patterns |
| qa-typeset-fix-float | 1.0.0 | Float too large | 1 pattern |
| qa-typeset-fix-tikz | 1.0.0 | TikZ overflow | 1 pattern |
| qa-typeset-fix-bib-standalone | 1.0.0 | Standalone biblatex | 1 pattern |
| qa-mdframed-fix | 1.0.0 | mdframed page breaks | 2 patterns |
| qa-section-orphan-fix | 1.0.0 | Orphan sections | 2 patterns |

#### qa-infra Family Fixes
| Skill | Version | Purpose | Fix Patterns |
|-------|---------|---------|--------------|
| qa-infra-backup | 1.0.0 | Create project backup | N/A |
| qa-infra-reorganize | 1.0.0 | Move files to correct dirs | N/A |
| qa-infra-validate | 1.0.0 | Verify structure | N/A |
| qa-cls-version-fix | 1.0.0 | Upgrade CLS version | 4 steps |
| qa-infra-subfiles-fix | 1.0.0 | Add subfiles preamble | 1 pattern |

#### qa-bib Family Fixes
| Skill | Version | Purpose | Fix Patterns |
|-------|---------|---------|--------------|
| qa-bib-fix-missing | 1.0.0 | Add missing bib entries | 3 patterns |

---

## 3. Skill Capabilities Analysis

### 3.1 qa-BiDi-detect Capabilities (15 Rules)

| Rule # | Capability | Description | Can Be Python? |
|--------|------------|-------------|----------------|
| 1 | Cover Page Metadata | Detect unwrapped Hebrew/English in preamble | YES |
| 2 | Table Cell Hebrew | Detect Hebrew in tabular without wrapper | YES |
| 3 | Section Numbering | Detect sections numbered from 0 | YES |
| 4 | Reversed Text | Detect final letters at word start | YES |
| 5 | Header/Footer Hebrew | Detect Hebrew in fancyhdr without RTL | YES |
| 6 | Numbers Without LTR | Detect unwrapped numbers in Hebrew | YES |
| 7 | English Without LTR | Detect unwrapped English in Hebrew | YES |
| 8 | tcolorbox BiDi-Safe | Detect tcolorbox without wrapper pattern | YES |
| 9 | Section Titles | Detect English in section titles | YES |
| 10 | Uppercase Acronyms | Detect unwrapped acronyms | YES |
| 11 | Decimal Numbers | Detect unwrapped decimals in preamble | YES |
| 12 | Chapter Labels | Detect \label after \hebrewchapter | YES |
| 13 | fbox/parbox Mixed | Detect mixed content without wrapper | YES |
| 14 | Standalone Counter | Detect missing chapter counter | YES |
| 15 | Hebrew in English | Detect Hebrew inside English wrapper | YES |

**Conclusion: ALL 15 rules can be implemented as Python regex-based detection.**

### 3.2 qa-code-detect Capabilities (6 Phases)

| Phase | Capability | Description | Can Be Python? |
|-------|------------|-------------|----------------|
| 1 | Code Block Discovery | Find all code blocks in PDF | PARTIAL (PDF parsing) |
| 2 | Background Overflow | Detect missing english wrapper | YES |
| 3 | Character Encoding | Detect non-ASCII characters | YES |
| 4 | Language Direction | Detect Hebrew in code | YES |
| 5 | Hebrew Title | Detect Hebrew without \hebtitle | YES |
| 6 | F-String Braces | Detect f-strings in pythonbox | YES |

### 3.3 qa-typeset-detect Capabilities

| Pattern | Capability | Description | Can Be Python? |
|---------|------------|-------------|----------------|
| Overfull hbox | Parse log for overflow | Regex on .log file | YES |
| Underfull hbox | Parse log for badness | Regex on .log file | YES |
| Overfull vbox | Parse log for page overflow | Regex on .log file | YES |
| Underfull vbox | Parse log for page badness | Regex on .log file | YES |
| Undefined refs | Parse log for missing refs | Regex on .log file | YES |
| Undefined citations | Parse log for missing cites | Regex on .log file | YES |
| Float too large | Parse log for float warnings | Regex on .log file | YES |
| TikZ overflow | Source analysis for TikZ | Regex on .tex files | YES |
| Known issues | Filter known harmless errors | Whitelist matching | YES |

---

## 4. Skill vs Python Code Evaluation

### 4.1 Decision Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                 SKILL vs PYTHON DECISION TREE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Can the operation be fully specified by input/output?          │
│  ├─ YES → Is it deterministic (same input = same output)?       │
│  │        ├─ YES → Is it regex/pattern based?                   │
│  │        │        ├─ YES → PYTHON TOOL (pure function)         │
│  │        │        └─ NO → PYTHON TOOL (algorithm)              │
│  │        └─ NO → HYBRID (skill decides, Python executes)       │
│  └─ NO → Does it require judgment or explanation?               │
│          ├─ YES → SKILL (procedural knowledge)                  │
│          └─ NO → HYBRID (skill orchestrates Python tools)       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Complete Evaluation Matrix

#### Detection Skills → Python Conversion

| Current Skill | Keep as Skill | Convert to Python | Split (Hybrid) |
|---------------|---------------|-------------------|----------------|
| qa-BiDi-detect | Orchestration only | All 15 rules | YES |
| qa-heb-math-detect | - | Entire skill | - |
| qa-BiDi-detect-tikz | - | Entire skill | - |
| qa-code-detect | Orchestration only | Phases 2-6 | YES |
| qa-code-background-detect | - | Entire skill | - |
| qa-table-detect | Orchestration only | All rules | YES |
| qa-table-fancy-detect | - | Entire skill | - |
| qa-table-overflow-detect | - | Entire skill | - |
| qa-img-detect | Orchestration only | Path/file checks | YES |
| qa-typeset-detect | Orchestration only | All log parsing | YES |
| qa-mdframed-detect | - | Entire skill | - |
| qa-cls-version-detect | - | Entire skill | - |
| qa-infra-subfiles-detect | - | Entire skill | - |
| qa-bib-detect | - | Entire skill | - |

#### Fix Skills → Python Conversion

| Current Skill | Keep as Skill | Convert to Python | Split (Hybrid) |
|---------------|---------------|-------------------|----------------|
| qa-BiDi-fix-text | Pattern selection | All replacements | YES |
| qa-BiDi-fix-numbers | - | Entire skill | - |
| qa-BiDi-fix-tcolorbox | Pattern docs | Replacement logic | YES |
| qa-code-fix-background | - | Entire skill | - |
| qa-table-fix-* | - | All table fixes | - |
| qa-typeset-fix-* | Judgment on severity | Text replacements | YES |

### 4.3 Token Savings Projection

| Operation Type | Current (LLM) | With Python | Savings |
|----------------|---------------|-------------|---------|
| Regex detection (per file) | ~500 tokens | 0 tokens | 100% |
| Pattern replacement | ~300 tokens | 0 tokens | 100% |
| Log parsing | ~1000 tokens | 0 tokens | 100% |
| Orchestration | ~200 tokens | ~200 tokens | 0% |
| Judgment decisions | ~400 tokens | ~400 tokens | 0% |

**Estimated total savings: 60-70% token reduction**

---

## 5. Recommended Architecture

### 5.1 New Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        QA ORCHESTRATION ENGINE                           │
│                     (Python Backend + Skill Frontend)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     qa_setup.json (Configuration)                 │   │
│  │  {                                                                │   │
│  │    "enabled_families": ["BiDi", "code", "typeset"],              │   │
│  │    "execution_order": ["cls-version", "BiDi", "code", "typeset"],│   │
│  │    "parallel_families": true,                                     │   │
│  │    "batch_size": 50,                                              │   │
│  │    "chunk_lines": 1000,                                           │   │
│  │    "log_level": "INFO",                                           │   │
│  │    "test_mode": false                                             │   │
│  │  }                                                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────┐   │
│  │   QA Controller    │  │   Progress Monitor │  │  Report Gen     │   │
│  │   (Python)         │  │   (Python)         │  │  (Python)       │   │
│  │                    │  │                    │  │                 │   │
│  │ - Load config      │  │ - Track progress   │  │ - Aggregate     │   │
│  │ - Dispatch jobs    │  │ - Heartbeat/alive  │  │ - Format output │   │
│  │ - Manage queue     │  │ - Watchdog         │  │ - Save reports  │   │
│  │ - Handle locks     │  │ - Log events       │  │                 │   │
│  └─────────┬──────────┘  └─────────┬──────────┘  └────────┬────────┘   │
│            │                       │                       │            │
│  ┌─────────┴───────────────────────┴───────────────────────┴─────────┐  │
│  │                      SHARED STATE MANAGER                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │ Mutex/Lock  │  │ Semaphore   │  │ Status DB   │                │  │
│  │  │ Manager     │  │ Pool        │  │ (SQLite)    │                │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
          ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
          │Python Tools │  │Python Tools │  │Python Tools │
          │(Detection)  │  │(Fixing)     │  │(Validation) │
          └─────────────┘  └─────────────┘  └─────────────┘
                    │               │               │
                    ▼               ▼               ▼
          ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
          │ Claude Skill│  │ Claude Skill│  │ Claude Skill│
          │ (Judgment)  │  │ (Complex)   │  │ (Report)    │
          └─────────────┘  └─────────────┘  └─────────────┘
```

### 5.2 Document Size Measurement

```python
# qa_engine/document_analyzer.py

class DocumentAnalyzer:
    """Measure document size and determine processing strategy."""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.metrics = {}

    def analyze(self) -> dict:
        """Analyze document and return metrics."""
        return {
            "total_lines": self._count_lines(),
            "total_files": self._count_files(),
            "total_chars": self._count_chars(),
            "estimated_tokens": self._estimate_tokens(),
            "recommended_strategy": self._recommend_strategy()
        }

    def _recommend_strategy(self) -> str:
        """Recommend processing strategy based on size."""
        lines = self.metrics.get("total_lines", 0)

        if lines < 500:
            return "single_pass"  # Process entire document at once
        elif lines < 2000:
            return "file_by_file"  # Process each file separately
        elif lines < 10000:
            return "chunked"  # Process in chunks of 1000 lines
        else:
            return "parallel_chunked"  # Parallel processing with chunks
```

### 5.3 Batch Processing Engine

```python
# qa_engine/batch_processor.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore
import queue

class BatchProcessor:
    """Process large documents in batches with coordination."""

    def __init__(self, config: dict):
        self.batch_size = config.get("batch_size", 50)
        self.chunk_lines = config.get("chunk_lines", 1000)
        self.max_workers = config.get("max_workers", 4)

        # Synchronization primitives
        self.file_locks = {}
        self.global_lock = Lock()
        self.worker_semaphore = Semaphore(self.max_workers)

        # Progress tracking
        self.progress_queue = queue.Queue()
        self.results = {}

    def process_project(self, project_path: str, detectors: list) -> dict:
        """Process entire project with batch coordination."""
        files = self._discover_files(project_path)
        chunks = self._create_chunks(files)

        results = {"issues": [], "stats": {}}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for chunk_id, chunk in enumerate(chunks):
                with self.worker_semaphore:
                    future = executor.submit(
                        self._process_chunk,
                        chunk_id,
                        chunk,
                        detectors
                    )
                    futures[future] = chunk_id

            for future in as_completed(futures):
                chunk_id = futures[future]
                try:
                    chunk_result = future.result()
                    results["issues"].extend(chunk_result["issues"])
                    self._update_progress(chunk_id, "DONE")
                except Exception as e:
                    self._update_progress(chunk_id, "ERROR", str(e))

        return results

    def _process_chunk(self, chunk_id: int, chunk: list, detectors: list) -> dict:
        """Process a single chunk through all detectors."""
        issues = []

        for file_path, start_line, end_line in chunk:
            # Acquire file lock
            file_lock = self._get_file_lock(file_path)
            with file_lock:
                content = self._read_chunk(file_path, start_line, end_line)

                for detector in detectors:
                    detector_issues = detector.detect(content, file_path, start_line)
                    issues.extend(detector_issues)

        return {"issues": issues, "chunk_id": chunk_id}

    def _get_file_lock(self, file_path: str) -> Lock:
        """Get or create lock for file."""
        with self.global_lock:
            if file_path not in self.file_locks:
                self.file_locks[file_path] = Lock()
            return self.file_locks[file_path]
```

### 5.4 Synchronization and Communication

```python
# qa_engine/coordination.py

import sqlite3
import json
from datetime import datetime
from threading import Lock
import os

class QACoordinator:
    """Coordinate multiple QA agents/processes."""

    DB_PATH = ".qa_coordination.db"

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.db_path = os.path.join(project_path, self.DB_PATH)
        self._init_db()
        self._lock = Lock()

    def _init_db(self):
        """Initialize SQLite database for coordination."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS qa_status (
                    id INTEGER PRIMARY KEY,
                    skill_name TEXT UNIQUE,
                    status TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    issues_count INTEGER,
                    verdict TEXT,
                    agent_id TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS qa_locks (
                    resource TEXT PRIMARY KEY,
                    locked_by TEXT,
                    locked_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS qa_heartbeat (
                    agent_id TEXT PRIMARY KEY,
                    last_heartbeat TEXT,
                    current_task TEXT
                )
            """)

    def acquire_resource(self, resource: str, agent_id: str, timeout: int = 30) -> bool:
        """Acquire exclusive lock on a resource."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Check if locked
                cursor = conn.execute(
                    "SELECT locked_by, locked_at FROM qa_locks WHERE resource = ?",
                    (resource,)
                )
                row = cursor.fetchone()

                if row:
                    # Check if lock is stale (older than timeout)
                    locked_at = datetime.fromisoformat(row[1])
                    if (datetime.now() - locked_at).seconds < timeout:
                        return False  # Still locked

                # Acquire or update lock
                conn.execute("""
                    INSERT OR REPLACE INTO qa_locks (resource, locked_by, locked_at)
                    VALUES (?, ?, ?)
                """, (resource, agent_id, datetime.now().isoformat()))
                return True

    def release_resource(self, resource: str, agent_id: str):
        """Release lock on a resource."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM qa_locks WHERE resource = ? AND locked_by = ?",
                    (resource, agent_id)
                )

    def update_heartbeat(self, agent_id: str, current_task: str):
        """Update agent heartbeat for watchdog monitoring."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO qa_heartbeat (agent_id, last_heartbeat, current_task)
                VALUES (?, ?, ?)
            """, (agent_id, datetime.now().isoformat(), current_task))

    def check_stale_agents(self, timeout: int = 60) -> list:
        """Find agents that haven't sent heartbeat recently."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT agent_id, last_heartbeat, current_task FROM qa_heartbeat"
            )
            stale = []
            for row in cursor.fetchall():
                last_beat = datetime.fromisoformat(row[1])
                if (datetime.now() - last_beat).seconds > timeout:
                    stale.append({
                        "agent_id": row[0],
                        "last_heartbeat": row[1],
                        "task": row[2]
                    })
            return stale
```

### 5.5 Logging and Monitoring

```python
# qa_engine/logging_system.py

import logging
import json
from datetime import datetime
from pathlib import Path

class QALogger:
    """Centralized logging for QA operations."""

    def __init__(self, project_path: str, log_level: str = "INFO"):
        self.project_path = Path(project_path)
        self.log_dir = self.project_path / "qa-logs"
        self.log_dir.mkdir(exist_ok=True)

        # Setup file handler
        log_file = self.log_dir / f"qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        self.logger = logging.getLogger("qa_system")
        self.logger.setLevel(getattr(logging, log_level))

        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(agent)s] %(message)s'
        ))
        self.logger.addHandler(handler)

    def log_event(self, agent: str, event_type: str, data: dict):
        """Log a QA event with structured data."""
        extra = {"agent": agent}
        message = json.dumps({
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            **data
        })
        self.logger.info(message, extra=extra)

    def log_progress(self, agent: str, skill: str, progress: float, status: str):
        """Log progress update."""
        self.log_event(agent, "PROGRESS", {
            "skill": skill,
            "progress": progress,
            "status": status
        })


class WatchdogMonitor:
    """Monitor agent health and restart if needed."""

    def __init__(self, coordinator: 'QACoordinator', check_interval: int = 30):
        self.coordinator = coordinator
        self.check_interval = check_interval
        self._running = False

    def start(self):
        """Start watchdog monitoring in background thread."""
        import threading
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop watchdog monitoring."""
        self._running = False

    def _monitor_loop(self):
        """Main monitoring loop."""
        import time
        while self._running:
            stale = self.coordinator.check_stale_agents()
            for agent in stale:
                self._handle_stale_agent(agent)
            time.sleep(self.check_interval)

    def _handle_stale_agent(self, agent: dict):
        """Handle a stale agent (log warning, potentially restart)."""
        logging.warning(f"Stale agent detected: {agent['agent_id']}, task: {agent['task']}")
```

---

## 6. insert_qa_skill Mechanism

### 6.1 Overview

The `insert_qa_skill` is a meta-skill that automates the creation and integration of new QA skills. It has two operating modes:

1. **Create New Skill Mode**: Define a completely new QA skill from requirements
2. **Split Existing Skill Mode**: Take an existing skill and split it into skill + Python code

### 6.2 insert_qa_skill Skill Definition

```yaml
# .claude/skills/insert_qa_skill/skill.md
---
name: insert_qa_skill
description: Creates and integrates new QA skills with optional Python tool generation
version: 1.0.0
author: QA Team
tags: [qa, meta-skill, skill-creation, python-tool, integration]
tools: [Read, Write, Edit, Grep, Glob, Bash, Task]
---
```

### 6.3 Full insert_qa_skill Implementation

```markdown
# insert_qa_skill - QA Skill Creation and Integration Meta-Skill

## Overview

This meta-skill automates the process of creating new QA skills and/or Python tools
and integrating them into the QA orchestration system.

## Operating Modes

### Mode 1: Create New Skill
```
invoke: insert_qa_skill --mode=create
arguments:
  --name: skill name (e.g., qa-new-detector)
  --family: parent family (e.g., BiDi, code, table)
  --level: skill level (1 or 2)
  --type: detection | fix | validation
  --description: brief description
  --rules: comma-separated list of detection rules (if detector)
  --patterns: comma-separated list of fix patterns (if fixer)
  --python: true | false (generate Python tool)
```

### Mode 2: Split Existing Skill
```
invoke: insert_qa_skill --mode=split
arguments:
  --skill: existing skill name to split
  --extract: capabilities to extract to Python (comma-separated)
```

## Workflow: Create New Skill

### Step 1: Validate Input
```
1. Check skill name follows convention: qa-{family}-{type}-{specific}
2. Verify parent family exists
3. Ensure no naming conflicts
```

### Step 2: Generate Skill File
```
Create: .claude/skills/{skill-name}/skill.md

Content template:
---
name: {skill-name}
description: {description} (Level {level} skill)
version: 1.0.0
author: QA Team
tags: [qa, {family}, {type}, level-{level}]
---

# {Skill Title} (Level {level})

## Agent Identity
- **Name:** {Display Name}
- **Role:** {Role Description}
- **Level:** {level} (Skill)
- **Parent:** qa-{family} (Level 1)

## Coordination

### Reports To
- qa-{family} (Level 1 orchestrator)

### Input
- {Input description}

### Output
- {Output description}

## Detection Rules / Fix Patterns
{Generated from --rules or --patterns}

## Version History
- **v1.0.0** ({date}): Initial creation
```

### Step 3: Generate Python Tool (if --python=true)
```
Create: .claude/skills/{skill-name}/tool.py

Content template:
"""
Python tool for {skill-name}
Auto-generated by insert_qa_skill
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Issue:
    rule: str
    file: str
    line: int
    content: str
    severity: str
    fix: Optional[str] = None

class {SkillClass}:
    """Python implementation of {skill-name}."""

    def __init__(self):
        self.rules = self._compile_rules()

    def _compile_rules(self) -> Dict[str, re.Pattern]:
        """Compile detection regex patterns."""
        return {
            {Generated regex patterns from rules}
        }

    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        """Run detection on content."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            for rule_name, pattern in self.rules.items():
                if pattern.search(line):
                    issues.append(Issue(
                        rule=rule_name,
                        file=file_path,
                        line=i + offset + 1,
                        content=line.strip(),
                        severity=self._get_severity(rule_name)
                    ))

        return issues

    def _get_severity(self, rule: str) -> str:
        """Get severity for rule."""
        # Implement rule-specific severity
        return "WARNING"

# Singleton instance for tool usage
detector = {SkillClass}()

def run_detection(file_path: str) -> List[Dict]:
    """Entry point for tool invocation."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = detector.detect(content, file_path)
    return [vars(issue) for issue in issues]
```

### Step 4: Generate Test File
```
Create: .claude/skills/{skill-name}/test_tool.py

Content:
"""Unit tests for {skill-name}"""

import unittest
from tool import {SkillClass}, run_detection

class Test{SkillClass}(unittest.TestCase):

    def setUp(self):
        self.detector = {SkillClass}()

    {Generated test cases from rules}

    def test_no_false_positives(self):
        """Test that valid content doesn't trigger."""
        valid_content = {valid examples}
        issues = self.detector.detect(valid_content, "test.tex")
        self.assertEqual(len(issues), 0)

    def test_detection_accuracy(self):
        """Test that issues are correctly detected."""
        bad_content = {bad examples}
        issues = self.detector.detect(bad_content, "test.tex")
        self.assertGreater(len(issues), 0)

if __name__ == '__main__':
    unittest.main()
```

### Step 5: Update Parent Orchestrator
```
Edit: .claude/skills/qa-{family}/skill.md

Add to Skill Family table:
| `{skill-name}` | {description} | {priority} |

Add to workflow diagram:
{Update ASCII diagram to include new skill}

Update version:
- **v{new}** ({date}): Added {skill-name} for {purpose}
```

### Step 6: Update QA-CLAUDE.md
```
Edit: .claude/skills/qa-orchestration/QA-CLAUDE.md

Add skill to Level 2 list under appropriate family.
Update version history.
```

### Step 7: Run Tests
```
bash: cd .claude/skills/{skill-name} && python -m pytest test_tool.py -v
```

### Step 8: Generate Integration Report
```
Output:
## insert_qa_skill Report

### Created Files
- .claude/skills/{skill-name}/skill.md
- .claude/skills/{skill-name}/tool.py (if python=true)
- .claude/skills/{skill-name}/test_tool.py (if python=true)

### Updated Files
- .claude/skills/qa-{family}/skill.md
- .claude/skills/qa-orchestration/QA-CLAUDE.md

### Integration Steps Completed
- [x] Skill file created
- [x] Python tool generated (if requested)
- [x] Tests generated
- [x] Parent orchestrator updated
- [x] QA-CLAUDE.md updated
- [x] Tests passed

### Usage
```
Skill: {skill-name}
```

## Workflow: Split Existing Skill

### Step 1: Analyze Existing Skill
```
1. Read existing skill file
2. Identify capabilities marked for extraction
3. Analyze which can be Python (deterministic, regex-based)
```

### Step 2: Extract Python Capabilities
```
For each capability in --extract:
1. Generate Python function implementing the capability
2. Replace skill section with tool invocation reference
```

### Step 3: Refactor Skill
```
1. Update skill to reference Python tool
2. Remove extracted logic
3. Keep orchestration and judgment logic
```

### Step 4: Update Tests
```
1. Generate unit tests for Python tool
2. Update skill integration tests
```

## Examples

### Example 1: Create New Detector
```
/insert_qa_skill --mode=create \
  --name=qa-BiDi-detect-footnotes \
  --family=BiDi \
  --level=2 \
  --type=detection \
  --description="Detect footnotes with Hebrew BiDi issues" \
  --rules="footnote-hebrew-unwrapped,footnote-number-reversed" \
  --python=true
```

### Example 2: Split Existing Skill
```
/insert_qa_skill --mode=split \
  --skill=qa-BiDi-detect \
  --extract="rule-6-numbers,rule-7-english,rule-10-acronyms"
```

## Integration Checklist

When a new skill is created, verify:

- [ ] Skill file follows naming convention
- [ ] Skill has proper frontmatter
- [ ] Skill has version history
- [ ] Python tool (if any) has unit tests
- [ ] Parent orchestrator references new skill
- [ ] QA-CLAUDE.md lists new skill
- [ ] Tests pass
```

### 6.4 insert_qa_skill Usage Examples

#### Create New Detection Skill with Python Backend

```bash
# Invoke the skill
Skill: insert_qa_skill

Arguments:
--mode=create
--name=qa-BiDi-detect-footnotes
--family=BiDi
--level=2
--type=detection
--description=Detect footnotes with Hebrew BiDi issues
--rules=footnote-hebrew-unwrapped:Footnote with Hebrew not in RTL wrapper,footnote-number-reversed:Footnote number displays reversed
--python=true
```

#### Split Existing Skill

```bash
# Analyze qa-BiDi-detect and extract rules 6, 7, 10 to Python
Skill: insert_qa_skill

Arguments:
--mode=split
--skill=qa-BiDi-detect
--extract=rule-6-numbers,rule-7-english,rule-10-acronyms
```

---

## 7. Python Testing Framework

### 7.1 Test Structure

```
.claude/skills/
├── qa-BiDi-detect/
│   ├── skill.md
│   ├── tool.py           # Python detection logic
│   ├── test_tool.py      # Unit tests
│   └── fixtures/         # Test fixtures
│       ├── valid_document.tex
│       └── invalid_document.tex
├── qa-code-detect/
│   ├── skill.md
│   ├── tool.py
│   ├── test_tool.py
│   └── fixtures/
└── qa-test-runner/       # Test orchestration
    ├── run_all_tests.py
    ├── test_orchestration.py
    └── conftest.py
```

### 7.2 Base Test Class

```python
# .claude/skills/qa-test-runner/base_test.py

import unittest
import os
from pathlib import Path
from abc import ABC, abstractmethod

class QASkillTestBase(ABC, unittest.TestCase):
    """Base class for all QA skill tests."""

    @property
    @abstractmethod
    def skill_name(self) -> str:
        """Return the skill name being tested."""
        pass

    @property
    def fixtures_path(self) -> Path:
        """Return path to test fixtures."""
        return Path(__file__).parent.parent / self.skill_name / "fixtures"

    def load_fixture(self, name: str) -> str:
        """Load a test fixture file."""
        fixture_file = self.fixtures_path / name
        with open(fixture_file, 'r', encoding='utf-8') as f:
            return f.read()

    def assertIssueFound(self, issues: list, rule: str, msg: str = None):
        """Assert that a specific rule was triggered."""
        rules_found = [i.get('rule') or i.rule for i in issues]
        self.assertIn(rule, rules_found, msg or f"Expected rule '{rule}' to be triggered")

    def assertNoIssue(self, issues: list, rule: str, msg: str = None):
        """Assert that a specific rule was NOT triggered."""
        rules_found = [i.get('rule') or i.rule for i in issues]
        self.assertNotIn(rule, rules_found, msg or f"Did not expect rule '{rule}' to be triggered")

    def assertIssueCount(self, issues: list, expected: int, msg: str = None):
        """Assert the number of issues found."""
        self.assertEqual(len(issues), expected, msg)
```

### 7.3 Example Test Implementation

```python
# .claude/skills/qa-BiDi-detect/test_tool.py

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "qa-test-runner"))

from base_test import QASkillTestBase
from tool import BiDiDetector

class TestBiDiDetector(QASkillTestBase):
    """Tests for qa-BiDi-detect Python tool."""

    @property
    def skill_name(self) -> str:
        return "qa-BiDi-detect"

    def setUp(self):
        self.detector = BiDiDetector()

    # Rule 6: Numbers in RTL context
    def test_rule6_detects_unwrapped_numbers(self):
        """Rule 6: Should detect numbers without \\en{} wrapper."""
        content = r"גרסה 0.5"
        issues = self.detector.detect(content, "test.tex")
        self.assertIssueFound(issues, "number-not-ltr")

    def test_rule6_allows_wrapped_numbers(self):
        """Rule 6: Should not trigger for wrapped numbers."""
        content = r"גרסה \en{0.5}"
        issues = self.detector.detect(content, "test.tex")
        self.assertNoIssue(issues, "number-not-ltr")

    def test_rule6_detects_escaped_percent(self):
        """Rule 6: Should detect 50\\% pattern."""
        content = r"הנחה של 50\% קלט"
        issues = self.detector.detect(content, "test.tex")
        self.assertIssueFound(issues, "number-not-ltr")

    # Rule 7: English in RTL context
    def test_rule7_detects_unwrapped_english(self):
        """Rule 7: Should detect English without \\en{} wrapper."""
        content = r"\textbf{sklearn} -- לשימוש"
        issues = self.detector.detect(content, "test.tex")
        self.assertIssueFound(issues, "english-text-not-ltr")

    def test_rule7_allows_wrapped_english(self):
        """Rule 7: Should not trigger for wrapped English."""
        content = r"\textbf{\en{sklearn}} -- לשימוש"
        issues = self.detector.detect(content, "test.tex")
        self.assertNoIssue(issues, "english-text-not-ltr")

    # Rule 10: Acronyms
    def test_rule10_detects_unwrapped_acronyms(self):
        """Rule 10: Should detect uppercase acronyms."""
        content = r"פרוטוקול MCP לליגת סוכנים"
        issues = self.detector.detect(content, "test.tex")
        self.assertIssueFound(issues, "acronym-not-ltr")

    # Rule 15: Hebrew inside English wrapper
    def test_rule15_detects_hebrew_in_english(self):
        """Rule 15: Should detect Hebrew inside \\textenglish{}."""
        content = r"\textenglish{Input (קלט)}"
        issues = self.detector.detect(content, "test.tex")
        self.assertIssueFound(issues, "hebrew-in-english-wrapper")

    # Integration test with fixture
    def test_fixture_invalid_document(self):
        """Should find issues in invalid fixture."""
        content = self.load_fixture("invalid_document.tex")
        issues = self.detector.detect(content, "invalid_document.tex")
        self.assertGreater(len(issues), 0)

    def test_fixture_valid_document(self):
        """Should not find issues in valid fixture."""
        content = self.load_fixture("valid_document.tex")
        issues = self.detector.detect(content, "valid_document.tex")
        self.assertIssueCount(issues, 0)


if __name__ == '__main__':
    unittest.main()
```

### 7.4 Test Fixtures

```latex
% .claude/skills/qa-BiDi-detect/fixtures/invalid_document.tex
% This file contains intentional BiDi issues for testing

\documentclass{hebrew-academic-template}
\begin{document}

% Rule 6 violation: unwrapped numbers
גרסה 0.5

% Rule 7 violation: unwrapped English
\textbf{sklearn} -- לשימוש

% Rule 10 violation: unwrapped acronym
פרוטוקול MCP לליגת סוכנים

% Rule 15 violation: Hebrew inside English
\textenglish{Input (קלט)}

\end{document}
```

```latex
% .claude/skills/qa-BiDi-detect/fixtures/valid_document.tex
% This file has correct BiDi usage for testing

\documentclass{hebrew-academic-template}
\begin{document}

% Rule 6 correct: wrapped numbers
גרסה \en{0.5}

% Rule 7 correct: wrapped English
\textbf{\en{sklearn}} -- לשימוש

% Rule 10 correct: wrapped acronym
פרוטוקול \en{MCP} לליגת סוכנים

% Rule 15 correct: Hebrew outside English
\textenglish{Input} (קלט)

\end{document}
```

### 7.5 Test Runner

```python
# .claude/skills/qa-test-runner/run_all_tests.py

import unittest
import sys
from pathlib import Path
import json
from datetime import datetime

def discover_and_run_tests() -> dict:
    """Discover and run all QA skill tests."""

    skills_dir = Path(__file__).parent.parent
    results = {
        "timestamp": datetime.now().isoformat(),
        "skills_tested": [],
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "details": []
    }

    # Find all test files
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith('qa-') and skill_dir.name != 'qa-test-runner':
            test_file = skill_dir / "test_tool.py"
            if test_file.exists():
                results["skills_tested"].append(skill_dir.name)

                # Run tests for this skill
                loader = unittest.TestLoader()
                suite = loader.discover(str(skill_dir), pattern="test_*.py")

                # Capture results
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)

                # Aggregate
                results["total_tests"] += result.testsRun
                results["passed"] += result.testsRun - len(result.failures) - len(result.errors)
                results["failed"] += len(result.failures)
                results["errors"] += len(result.errors)

                results["details"].append({
                    "skill": skill_dir.name,
                    "tests_run": result.testsRun,
                    "failures": [str(f) for f in result.failures],
                    "errors": [str(e) for e in result.errors]
                })

    return results


def run_orchestration_tests() -> dict:
    """Test the full orchestration pipeline."""

    results = {"timestamp": datetime.now().isoformat(), "tests": []}

    # Test 1: Skill discovery
    from qa_engine.skill_discovery import discover_skills
    skills = discover_skills()
    results["tests"].append({
        "name": "skill_discovery",
        "passed": len(skills) > 0,
        "details": f"Found {len(skills)} skills"
    })

    # Test 2: Orchestration flow
    # ... more tests

    return results


if __name__ == '__main__':
    print("=" * 60)
    print("QA SKILLS TEST SUITE")
    print("=" * 60)

    results = discover_and_run_tests()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Skills tested: {len(results['skills_tested'])}")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Errors: {results['errors']}")

    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 and results['errors'] == 0 else 1)
```

### 7.6 Orchestration Tests

```python
# .claude/skills/qa-test-runner/test_orchestration.py

import unittest
from pathlib import Path
import tempfile
import shutil

class TestQAOrchestration(unittest.TestCase):
    """Test the full QA orchestration system."""

    def setUp(self):
        """Create a temporary test project."""
        self.test_dir = tempfile.mkdtemp()
        self._create_test_project()

    def tearDown(self):
        """Clean up test project."""
        shutil.rmtree(self.test_dir)

    def _create_test_project(self):
        """Create a minimal LaTeX project for testing."""
        master_dir = Path(self.test_dir) / "master"
        master_dir.mkdir()

        # Create minimal .tex file with known issues
        main_tex = master_dir / "main.tex"
        main_tex.write_text(r"""
\documentclass{hebrew-academic-template}
\begin{document}
גרסה 0.5
\end{document}
""", encoding='utf-8')

    def test_full_qa_pipeline(self):
        """Test complete QA pipeline execution."""
        from qa_engine.controller import QAController

        controller = QAController(self.test_dir)
        results = controller.run_full_qa()

        # Verify results structure
        self.assertIn("families", results)
        self.assertIn("total_issues", results)
        self.assertIn("verdict", results)

    def test_parallel_execution(self):
        """Test that families can run in parallel."""
        from qa_engine.controller import QAController

        controller = QAController(self.test_dir, parallel=True)
        results = controller.run_full_qa()

        # All families should have completed
        for family in ["BiDi", "code", "typeset"]:
            self.assertIn(family, results["families"])

    def test_batch_processing(self):
        """Test batch processing for large documents."""
        from qa_engine.batch_processor import BatchProcessor

        processor = BatchProcessor({"batch_size": 10, "chunk_lines": 100})
        results = processor.process_project(self.test_dir, [])

        self.assertIn("issues", results)


if __name__ == '__main__':
    unittest.main()
```

---

## 8. Protocols and Procedures

### 8.1 Protocol: Adding a New QA Skill

```
┌─────────────────────────────────────────────────────────────────┐
│           PROTOCOL: ADDING A NEW QA SKILL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STEP 1: REQUIREMENTS GATHERING                                  │
│  ─────────────────────────────────                               │
│  □ Define problem/bug this skill will detect/fix                 │
│  □ Identify parent family (BiDi, code, table, etc.)              │
│  □ Determine skill level (usually L2)                            │
│  □ Decide skill type (detection, fix, validation)                │
│  □ List specific rules/patterns                                  │
│                                                                  │
│  STEP 2: USE insert_qa_skill                                     │
│  ──────────────────────────────                                  │
│  □ Invoke: Skill: insert_qa_skill                                │
│  □ Provide arguments:                                            │
│    --mode=create                                                 │
│    --name={skill-name}                                           │
│    --family={parent-family}                                      │
│    --level=2                                                     │
│    --type={detection|fix|validation}                             │
│    --description={brief description}                             │
│    --rules={comma-separated rules}                               │
│    --python=true (if deterministic)                              │
│                                                                  │
│  STEP 3: REVIEW GENERATED FILES                                  │
│  ─────────────────────────────────                               │
│  □ Review skill.md for accuracy                                  │
│  □ Review tool.py for correct regex patterns                     │
│  □ Review test_tool.py for comprehensive coverage                │
│                                                                  │
│  STEP 4: ADD TEST FIXTURES                                       │
│  ────────────────────────────                                    │
│  □ Create valid_document.tex (no issues)                         │
│  □ Create invalid_document.tex (has issues)                      │
│  □ Add edge case fixtures as needed                              │
│                                                                  │
│  STEP 5: RUN TESTS                                               │
│  ─────────────────                                               │
│  □ Run: python test_tool.py                                      │
│  □ All tests must pass                                           │
│  □ Run full test suite: python run_all_tests.py                  │
│                                                                  │
│  STEP 6: VERIFY INTEGRATION                                      │
│  ──────────────────────────                                      │
│  □ Check parent orchestrator includes new skill                  │
│  □ Check QA-CLAUDE.md lists new skill                            │
│  □ Test with real document                                       │
│                                                                  │
│  STEP 7: DOCUMENTATION                                           │
│  ─────────────────────────                                       │
│  □ Update skill version history                                  │
│  □ Document any special usage notes                              │
│  □ Add to QA-TASKS.md if tracking needed                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Protocol: Adding Python Code to Existing Skill

```
┌─────────────────────────────────────────────────────────────────┐
│       PROTOCOL: ADDING PYTHON CODE TO EXISTING SKILL             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STEP 1: IDENTIFY CONVERTIBLE CAPABILITIES                       │
│  ─────────────────────────────────────────                       │
│  □ Read existing skill.md completely                             │
│  □ List all detection rules or fix patterns                      │
│  □ Evaluate each using decision framework:                       │
│    - Is it deterministic? (same input = same output)             │
│    - Can it be implemented as regex/algorithm?                   │
│    - Does it require LLM judgment?                               │
│  □ Mark capabilities suitable for Python extraction              │
│                                                                  │
│  STEP 2: USE insert_qa_skill SPLIT MODE                          │
│  ───────────────────────────────────────                         │
│  □ Invoke: Skill: insert_qa_skill                                │
│  □ Provide arguments:                                            │
│    --mode=split                                                  │
│    --skill={existing-skill-name}                                 │
│    --extract={comma-separated capability names}                  │
│                                                                  │
│  STEP 3: REVIEW GENERATED PYTHON                                 │
│  ───────────────────────────────                                 │
│  □ Verify regex patterns are correct                             │
│  □ Verify edge cases are handled                                 │
│  □ Ensure error handling is appropriate                          │
│                                                                  │
│  STEP 4: UPDATE SKILL TO USE PYTHON                              │
│  ──────────────────────────────────                              │
│  □ Add reference to Python tool in skill.md                      │
│  □ Update detection/fix process to call Python                   │
│  □ Keep orchestration logic in skill                             │
│  □ Remove extracted logic from skill (avoid duplication)         │
│                                                                  │
│  STEP 5: CREATE/UPDATE TESTS                                     │
│  ───────────────────────────                                     │
│  □ Create unit tests for each Python function                    │
│  □ Test with existing fixtures                                   │
│  □ Add new fixtures for edge cases                               │
│                                                                  │
│  STEP 6: VERIFY NO REGRESSION                                    │
│  ─────────────────────────────                                   │
│  □ Run full test suite                                           │
│  □ Test with real document that previously worked                │
│  □ Verify all issues still detected                              │
│                                                                  │
│  STEP 7: UPDATE VERSION                                          │
│  ─────────────────────                                           │
│  □ Increment skill version (minor bump)                          │
│  □ Add to version history:                                       │
│    "Python tool added for {capability}"                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 Protocol: Adding Test to Existing Skill

```
┌─────────────────────────────────────────────────────────────────┐
│           PROTOCOL: ADDING TEST TO EXISTING SKILL                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STEP 1: IDENTIFY TEST GAP                                       │
│  ─────────────────────────                                       │
│  □ Review existing test_tool.py                                  │
│  □ Identify untested capabilities                                │
│  □ Identify edge cases without tests                             │
│  □ Check for regression scenarios                                │
│                                                                  │
│  STEP 2: CREATE TEST FIXTURE                                     │
│  ───────────────────────────                                     │
│  □ Create minimal .tex file demonstrating the scenario           │
│  □ Save in fixtures/ directory                                   │
│  □ Name descriptively: test_{scenario}.tex                       │
│                                                                  │
│  STEP 3: WRITE TEST METHOD                                       │
│  ─────────────────────────                                       │
│  □ Follow naming convention: test_{rule}_{scenario}              │
│  □ Add docstring explaining what's being tested                  │
│  □ Use base class assertions:                                    │
│    - assertIssueFound(issues, rule)                              │
│    - assertNoIssue(issues, rule)                                 │
│    - assertIssueCount(issues, expected)                          │
│                                                                  │
│  STEP 4: RUN TEST                                                │
│  ─────────────                                                   │
│  □ Run single test: python -m pytest test_tool.py -k test_name   │
│  □ Verify test passes with expected behavior                     │
│  □ Run full suite to ensure no regressions                       │
│                                                                  │
│  STEP 5: DOCUMENT                                                │
│  ────────────                                                    │
│  □ Add test to test listing in skill.md (if applicable)          │
│  □ Note any special test setup requirements                      │
│                                                                  │
│  TEST METHOD TEMPLATE:                                           │
│  ─────────────────────                                           │
│  def test_rule{N}_{scenario}(self):                              │
│      """Rule {N}: {Description of what's tested}."""             │
│      content = r"{latex content}"  # or self.load_fixture(...)   │
│      issues = self.detector.detect(content, "test.tex")          │
│      self.assert{Assertion}(issues, "{expected}")                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.4 qa_setup.json Configuration Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "QA Setup Configuration",
  "description": "Configuration for QA orchestration system",
  "type": "object",
  "properties": {
    "enabled_families": {
      "type": "array",
      "description": "List of L1 families to enable",
      "items": {
        "type": "string",
        "enum": ["BiDi", "table", "code", "img", "typeset", "infra", "bib"]
      },
      "default": ["BiDi", "code", "typeset"]
    },
    "execution_order": {
      "type": "array",
      "description": "Order in which families execute (blocking families first)",
      "items": {"type": "string"},
      "default": ["cls-version", "BiDi", "code", "table", "img", "typeset"]
    },
    "parallel_families": {
      "type": "boolean",
      "description": "Run non-blocking families in parallel",
      "default": true
    },
    "blocking_checks": {
      "type": "array",
      "description": "Checks that must pass before continuing",
      "items": {"type": "string"},
      "default": ["cls-version"]
    },
    "batch_processing": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": true},
        "batch_size": {"type": "integer", "default": 50},
        "chunk_lines": {"type": "integer", "default": 1000},
        "max_workers": {"type": "integer", "default": 4}
      }
    },
    "logging": {
      "type": "object",
      "properties": {
        "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"], "default": "INFO"},
        "file_enabled": {"type": "boolean", "default": true},
        "console_enabled": {"type": "boolean", "default": true}
      }
    },
    "watchdog": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": true},
        "heartbeat_interval": {"type": "integer", "default": 30},
        "stale_threshold": {"type": "integer", "default": 60}
      }
    },
    "reporting": {
      "type": "object",
      "properties": {
        "format": {"type": "string", "enum": ["markdown", "json", "html"], "default": "markdown"},
        "include_details": {"type": "boolean", "default": true},
        "include_timestamps": {"type": "boolean", "default": true}
      }
    },
    "skill_overrides": {
      "type": "object",
      "description": "Per-skill configuration overrides",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "enabled": {"type": "boolean"},
          "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
          "skip_rules": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

### 8.5 Example qa_setup.json

```json
{
  "enabled_families": ["BiDi", "code", "typeset", "table"],
  "execution_order": ["cls-version", "BiDi", "code", "table", "typeset"],
  "parallel_families": true,
  "blocking_checks": ["cls-version"],
  "batch_processing": {
    "enabled": true,
    "batch_size": 50,
    "chunk_lines": 1000,
    "max_workers": 4
  },
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "console_enabled": true
  },
  "watchdog": {
    "enabled": true,
    "heartbeat_interval": 30,
    "stale_threshold": 60
  },
  "reporting": {
    "format": "markdown",
    "include_details": true,
    "include_timestamps": true
  },
  "skill_overrides": {
    "qa-BiDi-detect": {
      "enabled": true,
      "priority": "high",
      "skip_rules": []
    },
    "qa-typeset-detect": {
      "enabled": true,
      "priority": "medium",
      "skip_rules": ["known_issues"]
    }
  }
}
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation (Immediate)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Create qa_engine Python package | CRITICAL | 2 days | None |
| Implement DocumentAnalyzer | HIGH | 1 day | qa_engine |
| Implement QACoordinator | HIGH | 2 days | qa_engine |
| Create qa_setup.json schema | HIGH | 1 day | None |
| Create base test framework | HIGH | 1 day | None |

### Phase 2: Python Tool Migration

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Convert qa-BiDi-detect rules to Python | HIGH | 3 days | Phase 1 |
| Convert qa-code-detect phases to Python | HIGH | 2 days | Phase 1 |
| Convert qa-typeset-detect to Python | MEDIUM | 2 days | Phase 1 |
| Create unit tests for all Python tools | HIGH | 2 days | Tool migration |

### Phase 3: Orchestration Engine

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Implement BatchProcessor | HIGH | 2 days | Phase 1 |
| Implement WatchdogMonitor | MEDIUM | 1 day | Phase 1 |
| Implement QALogger | MEDIUM | 1 day | Phase 1 |
| Create QA Controller | HIGH | 2 days | All Phase 3 |

### Phase 4: insert_qa_skill

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Create insert_qa_skill skill.md | HIGH | 2 days | Phase 2 |
| Implement create mode | HIGH | 2 days | skill.md |
| Implement split mode | HIGH | 2 days | skill.md |
| Create skill templates | MEDIUM | 1 day | modes |

### Phase 5: Testing & Validation

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Create test fixtures for all skills | HIGH | 3 days | Phase 2 |
| Implement test runner | HIGH | 1 day | fixtures |
| Run full validation on real projects | CRITICAL | 2 days | All phases |
| Performance benchmarking | MEDIUM | 1 day | Validation |

---

## 10. Appendices

### Appendix A: Complete File Structure

```
.claude/
├── skills/
│   ├── qa-orchestration/
│   │   ├── QA-CLAUDE.md
│   │   ├── QA-TASKS.md
│   │   └── qa_setup.json
│   │
│   ├── qa-super/
│   │   └── skill.md
│   │
│   ├── qa-BiDi/
│   │   └── skill.md
│   ├── qa-BiDi-detect/
│   │   ├── skill.md
│   │   ├── tool.py
│   │   ├── test_tool.py
│   │   └── fixtures/
│   ├── qa-BiDi-fix-text/
│   │   ├── skill.md
│   │   └── tool.py
│   │ ... (other BiDi skills)
│   │
│   ├── qa-code/
│   │   └── skill.md
│   ├── qa-code-detect/
│   │   ├── skill.md
│   │   ├── tool.py
│   │   └── test_tool.py
│   │ ... (other code skills)
│   │
│   ├── qa-table/
│   ├── qa-img/
│   ├── qa-typeset/
│   ├── qa-infra/
│   ├── qa-bib/
│   │
│   ├── insert_qa_skill/
│   │   ├── skill.md
│   │   └── templates/
│   │
│   └── qa-test-runner/
│       ├── run_all_tests.py
│       ├── base_test.py
│       ├── test_orchestration.py
│       └── conftest.py
│
├── qa_engine/                    # NEW: Python backend
│   ├── __init__.py
│   ├── controller.py
│   ├── document_analyzer.py
│   ├── batch_processor.py
│   ├── coordination.py
│   ├── logging_system.py
│   └── skill_discovery.py
│
└── commands/
    ├── full-pdf-qa.md
    └── fix-qa-mechanism.md
```

### Appendix B: Python Tool Interface Specification

```python
"""
Standard interface for QA Python tools.
All Python tools must implement these interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum

class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

@dataclass
class Issue:
    """Standard issue representation."""
    rule: str
    file: str
    line: int
    content: str
    severity: Severity
    fix: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class DetectorInterface(ABC):
    """Interface for detection tools."""

    @abstractmethod
    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        """
        Detect issues in content.

        Args:
            content: The text content to analyze
            file_path: Path to the source file (for reporting)
            offset: Line number offset (for chunked processing)

        Returns:
            List of Issue objects
        """
        pass

    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        pass

class FixerInterface(ABC):
    """Interface for fix tools."""

    @abstractmethod
    def fix(self, content: str, issues: List[Issue]) -> str:
        """
        Apply fixes to content.

        Args:
            content: The original content
            issues: List of issues to fix

        Returns:
            Fixed content
        """
        pass

    @abstractmethod
    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        pass
```

### Appendix C: Skill Template

```markdown
---
name: qa-{family}-{type}-{specific}
description: {Description} (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, {family}, {type}, level-2]
---

# {Title} (Level 2)

## Agent Identity
- **Name:** {Display Name}
- **Role:** {Role}
- **Level:** 2 (Skill)
- **Parent:** qa-{family} (Level 1)

## Coordination

### Reports To
- qa-{family} (Level 1 orchestrator)

### Input
- LaTeX source files from parent
- Issues list from detection (if fix skill)

### Output
- Detection report / Fix report

## Purpose
{Detailed purpose description}

## Detection Rules / Fix Patterns

### Rule/Pattern 1: {Name}
**Problem:**
```latex
% BAD:
{bad example}

% GOOD:
{good example}
```

**Detection/Fix:**
{Description}

## Python Tool Reference
This skill uses the Python tool at `tool.py` for:
- {capability 1}
- {capability 2}

## Version History
- **v1.0.0** ({date}): Initial creation

---

**Parent:** qa-{family} (Level 1)
**Coordination:** qa-orchestration/QA-CLAUDE.md
```

---

## Conclusion

This research report provides a comprehensive analysis of the existing QA Claude mechanism and presents a detailed architecture for improvement. The key recommendations are:

1. **Adopt hybrid skill/Python model** - Keep skills for orchestration and judgment; use Python for deterministic operations
2. **Implement batch processing** - Handle large documents efficiently with chunking
3. **Add coordination primitives** - Mutex, semaphores, and shared state for multi-agent scenarios
4. **Create insert_qa_skill** - Automate skill creation and integration
5. **Build test framework** - Unit tests for all Python tools with fixtures
6. **Use qa_setup.json** - Centralized configuration for enabling/ordering skills

The estimated token savings from Python migration is 60-70%, with improved reliability through deterministic execution.

---

*Report generated: 2025-12-15*
*Author: Claude Code QA Research*
*Version: 1.0.0*
