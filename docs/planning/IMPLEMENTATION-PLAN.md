# Implementation Plan - QA Skill Python Base System

**Document Version:** 1.0.0
**Date:** 2025-12-15
**Status:** Ready for Review
**Reference:** PRD-QA-SKILL-PYTHON-BASE.md v1.1.0

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Phase Breakdown](#2-phase-breakdown)
3. [Parallel Execution Map](#3-parallel-execution-map)
4. [Detailed Task List](#4-detailed-task-list)
5. [Testing Strategy](#5-testing-strategy)
6. [Deployment Strategy](#6-deployment-strategy)
7. [Risk Management](#7-risk-management)
8. [Verification Checkpoints](#8-verification-checkpoints)

---

## 1. Architecture Overview

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QA SKILL PYTHON BASE SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    ORCHESTRATION LAYER                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │    │
│  │  │ qa-super    │  │  QA         │  │ qa_setup    │                  │    │
│  │  │ (skill.md)  │←→│ Controller  │←→│ .json       │                  │    │
│  │  │ L0 Skill    │  │ (Python)    │  │ (Config)    │                  │    │
│  │  └─────────────┘  └──────┬──────┘  └─────────────┘                  │    │
│  └──────────────────────────┼──────────────────────────────────────────┘    │
│                             │                                                │
│  ┌──────────────────────────┼──────────────────────────────────────────┐    │
│  │                    FAMILY LAYER (L1)                                 │    │
│  │         ┌────────────────┼────────────────┐                          │    │
│  │         ▼                ▼                ▼                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │    │
│  │  │ qa-BiDi     │  │ qa-code     │  │ qa-typeset  │  ... (families)  │    │
│  │  │ (skill.md)  │  │ (skill.md)  │  │ (skill.md)  │                  │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │    │
│  └─────────┼────────────────┼────────────────┼─────────────────────────┘    │
│            │                │                │                               │
│  ┌─────────┼────────────────┼────────────────┼─────────────────────────┐    │
│  │         │         TOOLS LAYER (L2)        │                          │    │
│  │         ▼                ▼                ▼                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │    │
│  │  │ BiDi        │  │ Code        │  │ Typeset     │                  │    │
│  │  │ Detector    │  │ Detector    │  │ Detector    │                  │    │
│  │  │ (tool.py)   │  │ (tool.py)   │  │ (tool.py)   │                  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │    │
│  │  │ BiDi        │  │ Code        │  │ Table       │                  │    │
│  │  │ Fixer       │  │ Fixer       │  │ Detector    │                  │    │
│  │  │ (tool.py)   │  │ (tool.py)   │  │ (tool.py)   │                  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    INFRASTRUCTURE LAYER                              │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐   │    │
│  │  │ Document    │  │ Batch       │  │ Coordinator │  │ Logger    │   │    │
│  │  │ Analyzer    │  │ Processor   │  │ (SQLite)    │  │           │   │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘   │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │    │
│  │  │ Skill       │  │ Interfaces  │  │ Watchdog    │                  │    │
│  │  │ Discovery   │  │ (ABC)       │  │ Monitor     │                  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    META-SKILL LAYER                                  │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐│    │
│  │  │ insert_qa_skill                                                 ││    │
│  │  │ ├── skill.md (orchestration)                                    ││    │
│  │  │ ├── templates/ (skill_template.md, detector_template.py, ...)   ││    │
│  │  │ └── tool.py (generation logic)                                  ││    │
│  │  └─────────────────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    TEST FRAMEWORK                                    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐   │    │
│  │  │ base_test   │  │ fixtures/   │  │ test_*.py   │  │ conftest  │   │    │
│  │  │ .py         │  │ (per skill) │  │ (per skill) │  │ .py       │   │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Command                                                                │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────┐                                                            │
│  │ qa_setup    │───────────────────────────────────────────┐                │
│  │ .json       │                                            │                │
│  └──────┬──────┘                                            │                │
│         │                                                   │                │
│         ▼                                                   ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  ┌───────────┐       │
│  │ QA          │───▶│ Document    │───▶│ Processing  │  │ Logging   │       │
│  │ Controller  │    │ Analyzer    │    │ Strategy    │  │ System    │       │
│  └──────┬──────┘    └─────────────┘    └──────┬──────┘  └───────────┘       │
│         │                                     │              ▲               │
│         ▼                                     ▼              │               │
│  ┌─────────────┐                       ┌─────────────┐      │               │
│  │ Skill       │───────────────────────│ Batch       │──────┘               │
│  │ Discovery   │                       │ Processor   │                      │
│  └──────┬──────┘                       └──────┬──────┘                      │
│         │                                     │                              │
│         ▼                                     ▼                              │
│  ┌─────────────┐                       ┌─────────────┐                      │
│  │ L1 Family   │◀─────────────────────▶│ Coordinator │                      │
│  │ Orchestrator│                       │ (SQLite)    │                      │
│  └──────┬──────┘                       └─────────────┘                      │
│         │                                     ▲                              │
│         │ [PARALLEL]                          │                              │
│         ▼                                     │                              │
│  ┌─────────────┐                              │                              │
│  │ L2 Detector │──────────────────────────────┤                              │
│  │ (Python)    │                              │                              │
│  └──────┬──────┘                              │                              │
│         │                                     │                              │
│         │ List[Issue]                         │                              │
│         ▼                                     │                              │
│  ┌─────────────┐                              │                              │
│  │ L2 Fixer    │──────────────────────────────┘                              │
│  │ (Python)    │                                                             │
│  └──────┬──────┘                                                             │
│         │                                                                    │
│         │ Fixed Content                                                      │
│         ▼                                                                    │
│  ┌─────────────┐    ┌─────────────┐                                         │
│  │ Result      │───▶│ Report      │                                         │
│  │ Aggregation │    │ Generation  │                                         │
│  └─────────────┘    └─────────────┘                                         │
│                            │                                                 │
│                            ▼                                                 │
│                     QA-REPORT.md                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Integration Points

| Component | Integrates With | Communication |
|-----------|----------------|---------------|
| QA Controller | qa-super skill | Python invocation from skill |
| QA Controller | qa_setup.json | JSON configuration file |
| QA Controller | Coordinator | SQLite database |
| L1 Orchestrators | L2 Python Tools | Python module import |
| L2 Detectors | L2 Fixers | List[Issue] data structure |
| All Components | Logger | Structured log events |
| Batch Processor | Coordinator | Lock acquisition |

---

## 2. Phase Breakdown

### Phase 1: Foundation (P0 - Critical)

**Objective:** Establish core infrastructure and interfaces

```
PHASE 1 COMPONENTS
├── [P0] qa_engine/__init__.py
├── [P0] qa_engine/interfaces.py          # DetectorInterface, FixerInterface, Issue
├── [P0] qa_engine/document_analyzer.py   # Document size analysis
├── [P0] qa_engine/coordination.py        # SQLite locks, heartbeats
├── [P0] qa_engine/config_loader.py       # qa_setup.json loader
├── [P0] qa_engine/logging_system.py      # Structured logging
└── [P0] qa_setup.json                    # Default configuration

PARALLEL OPPORTUNITIES:
- interfaces.py, document_analyzer.py, coordination.py can be developed in PARALLEL
- config_loader.py depends on qa_setup.json schema (SEQUENTIAL)
- logging_system.py can be developed in PARALLEL with others
```

**Exit Criteria:**
- [ ] Interfaces defined and importable
- [ ] Document analyzer returns correct metrics for test documents
- [ ] Coordinator creates database, manages locks/heartbeats
- [ ] Config loader validates and loads configuration
- [ ] Logger produces structured output

---

### Phase 2: Python Tool Migration (P0 - Critical)

**Objective:** Migrate all detection logic to deterministic Python tools

```
PHASE 2 COMPONENTS
├── DETECTORS (all PARALLEL):
│   ├── [P0] qa-BiDi-detect/tool.py       # 15 BiDi rules
│   ├── [P0] qa-code-detect/tool.py       # 6 code phases
│   ├── [P1] qa-typeset-detect/tool.py    # Log parsing
│   └── [P1] qa-table-detect/tool.py      # Table layout
│
├── FIXERS (PARALLEL, after detectors):
│   ├── [P1] qa-BiDi-fix-text/tool.py
│   ├── [P1] qa-BiDi-fix-numbers/tool.py
│   ├── [P1] qa-code-fix-background/tool.py
│   └── [P1] qa-code-fix-encoding/tool.py
│
└── TEST FILES (PARALLEL with tools):
    ├── qa-BiDi-detect/test_tool.py
    ├── qa-BiDi-detect/fixtures/
    ├── qa-code-detect/test_tool.py
    └── qa-code-detect/fixtures/

PARALLEL OPPORTUNITIES:
- ALL detectors can be developed in PARALLEL
- ALL fixers can be developed in PARALLEL (after their detector)
- Test files can be developed in PARALLEL with tools
```

**Exit Criteria:**
- [ ] BiDiDetector implements all 15 rules with tests
- [ ] CodeDetector implements all 6 phases with tests
- [ ] TypesetDetector parses log patterns with tests
- [ ] TableDetector detects layout issues with tests
- [ ] All fixers apply corrections correctly
- [ ] 80%+ test coverage achieved

---

### Phase 3: Orchestration Engine (P0 - Critical)

**Objective:** Build batch processing and main controller

```
PHASE 3 COMPONENTS
├── [P0] qa_engine/batch_processor.py     # Chunked parallel processing
├── [P0] qa_engine/controller.py          # Main orchestration (depends on P1, P2)
├── [P1] qa_engine/skill_discovery.py     # Skill registry building
├── [P1] qa_engine/watchdog.py            # Agent monitoring
└── [P0] qa_engine/report_generator.py    # Report output

DEPENDENCIES:
- batch_processor.py depends on: interfaces.py, coordination.py
- controller.py depends on: ALL Phase 1, batch_processor.py, skill_discovery.py
- skill_discovery.py depends on: interfaces.py

PARALLEL OPPORTUNITIES:
- batch_processor.py and skill_discovery.py can be PARALLEL
- watchdog.py and report_generator.py can be PARALLEL
- controller.py MUST be SEQUENTIAL (depends on others)
```

**Exit Criteria:**
- [ ] Batch processor handles 50,000+ line documents
- [ ] Controller orchestrates full QA pipeline
- [ ] Skill discovery builds complete registry
- [ ] Watchdog detects stale agents
- [ ] Reports generated in markdown/JSON

---

### Phase 4: insert_qa_skill Meta-Skill (P1 - High)

**Objective:** Automate skill creation and Python extraction

```
PHASE 4 COMPONENTS
├── [P1] insert_qa_skill/skill.md         # Meta-skill definition
├── [P1] insert_qa_skill/tool.py          # Generation logic
├── [P1] insert_qa_skill/templates/
│   ├── skill_template.md
│   ├── detector_template.py
│   ├── fixer_template.py
│   ├── test_template.py
│   └── fixture_templates/
└── [P1] insert_qa_skill/test_tool.py     # Tests

SEQUENTIAL:
- Templates must be created BEFORE tool.py
- tool.py depends on templates and interfaces
```

**Exit Criteria:**
- [ ] Create mode generates valid skill structure
- [ ] Split mode extracts Python tool correctly
- [ ] Generated skills pass validation
- [ ] Generated tests pass
- [ ] Integration updates parent orchestrator

---

### Phase 5: Skill Migration and Validation (P1 - High)

**Objective:** Rewrite existing skills to standard format and validate

```
PHASE 5 COMPONENTS
├── SKILL REWRITES (PARALLEL):
│   ├── [P1] qa-super/skill.md            # Rewrite to standard
│   ├── [P1] qa-BiDi/skill.md             # Rewrite to standard
│   ├── [P1] qa-code/skill.md             # Rewrite to standard
│   ├── [P1] qa-typeset/skill.md          # Rewrite to standard
│   └── [P1] qa-table/skill.md            # Rewrite to standard
│
├── INTEGRATION:
│   ├── [P1] qa-orchestration/QA-CLAUDE.md # Update architecture doc
│   └── [P1] commands/full-pdf-qa.md       # Update command
│
└── VALIDATION:
    ├── [P0] Test with real Hebrew-English documents
    ├── [P0] Token usage measurement
    └── [P0] Performance benchmarks

PARALLEL OPPORTUNITIES:
- ALL skill rewrites can be done in PARALLEL
- Validation MUST be SEQUENTIAL (after rewrites)
```

**Exit Criteria:**
- [ ] All skills follow Claude CLI standard format
- [ ] All skills have proper detector/fixer separation
- [ ] Real project QA runs successfully
- [ ] 60%+ token reduction verified
- [ ] Documentation complete

---

### Phase 6: Global Deployment (P0 - Critical)

**Objective:** Deploy to global Claude CLI skills location

```
PHASE 6 STEPS (SEQUENTIAL):
1. [P0] Create backup of existing global skills
2. [P0] Run full test suite locally
3. [P0] Generate deployment report
4. [P0] Get user approval
5. [P0] Copy skills to global location
6. [P0] Copy qa_engine to global location
7. [P0] Run validation tests on global installation
8. [P0] Update QA-CLAUDE.md in global location
```

**Exit Criteria:**
- [ ] User has explicitly approved deployment
- [ ] Backup created successfully
- [ ] All files copied to global location
- [ ] Global installation passes tests
- [ ] Rollback procedure documented and tested

---

## 3. Parallel Execution Map

### 3.1 Phase 1 Parallel Map

```
PHASE 1 - FOUNDATION
══════════════════════════════════════════════════════════════════════════════

Time →  T1          T2          T3          T4          T5
        │           │           │           │           │
        ├───────────┴───────────┴───────────┴───────────┤
        │                                               │
        │  [PARALLEL BLOCK A]                          │
        │  ┌─────────────────────────────────────────┐  │
        │  │ interfaces.py                           │  │
        │  │ (DetectorInterface, FixerInterface,     │  │
        │  │  Issue, Severity)                       │  │
        │  └─────────────────────────────────────────┘  │
        │  ┌─────────────────────────────────────────┐  │
        │  │ document_analyzer.py                    │  │
        │  │ (analyze_project, count_lines,          │  │
        │  │  estimate_tokens, recommend_strategy)   │  │
        │  └─────────────────────────────────────────┘  │
        │  ┌─────────────────────────────────────────┐  │
        │  │ coordination.py                         │  │
        │  │ (QACoordinator, acquire/release,        │  │
        │  │  heartbeat, SQLite schema)              │  │
        │  └─────────────────────────────────────────┘  │
        │  ┌─────────────────────────────────────────┐  │
        │  │ logging_system.py                       │  │
        │  │ (QALogger, structured events,           │  │
        │  │  file/console handlers)                 │  │
        │  └─────────────────────────────────────────┘  │
        │                                               │
        └───────────────────────────────────────────────┘
                            │
                            ▼ [SYNC POINT]
        ┌───────────────────────────────────────────────┐
        │  [SEQUENTIAL BLOCK B]                         │
        │  ┌─────────────────────────────────────────┐  │
        │  │ qa_setup.json (schema definition)       │  │
        │  └─────────────────────────────────────────┘  │
        │                     │                         │
        │                     ▼                         │
        │  ┌─────────────────────────────────────────┐  │
        │  │ config_loader.py                        │  │
        │  │ (depends on schema, uses interfaces)    │  │
        │  └─────────────────────────────────────────┘  │
        │                     │                         │
        │                     ▼                         │
        │  ┌─────────────────────────────────────────┐  │
        │  │ Unit tests for Phase 1                  │  │
        │  └─────────────────────────────────────────┘  │
        └───────────────────────────────────────────────┘
                            │
                            ▼
                    PHASE 1 COMPLETE
```

### 3.2 Phase 2 Parallel Map

```
PHASE 2 - PYTHON TOOLS
══════════════════════════════════════════════════════════════════════════════

        ┌───────────────────────────────────────────────────────────────────┐
        │                    [PARALLEL BLOCK A - DETECTORS]                  │
        │                                                                    │
        │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
        │  │ BiDiDetector     │  │ CodeDetector     │  │ TypesetDetector  │ │
        │  │ (tool.py)        │  │ (tool.py)        │  │ (tool.py)        │ │
        │  │ ├── Rule 1-5     │  │ ├── Phase 2      │  │ ├── hbox/vbox    │ │
        │  │ ├── Rule 6-10    │  │ ├── Phase 3      │  │ ├── undefined    │ │
        │  │ └── Rule 11-15   │  │ ├── Phase 4      │  │ ├── float        │ │
        │  │                  │  │ ├── Phase 5      │  │ └── tikz         │ │
        │  │ test_tool.py     │  │ └── Phase 6      │  │                  │ │
        │  │ fixtures/        │  │                  │  │ test_tool.py     │ │
        │  └──────────────────┘  │ test_tool.py     │  │ fixtures/        │ │
        │                        │ fixtures/        │  └──────────────────┘ │
        │  ┌──────────────────┐  └──────────────────┘                       │
        │  │ TableDetector    │                                              │
        │  │ (tool.py)        │                                              │
        │  │ test_tool.py     │                                              │
        │  │ fixtures/        │                                              │
        │  └──────────────────┘                                              │
        │                                                                    │
        └───────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ [SYNC POINT - Detectors complete]
        ┌───────────────────────────────────────────────────────────────────┐
        │                    [PARALLEL BLOCK B - FIXERS]                     │
        │                                                                    │
        │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
        │  │ BiDi-fix-text    │  │ BiDi-fix-numbers │  │ Code-fix-bg      │ │
        │  │ (tool.py)        │  │ (tool.py)        │  │ (tool.py)        │ │
        │  │ test_tool.py     │  │ test_tool.py     │  │ test_tool.py     │ │
        │  │ fixtures/        │  │ fixtures/        │  │ fixtures/        │ │
        │  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
        │                                                                    │
        │  ┌──────────────────┐  ┌──────────────────┐                       │
        │  │ Code-fix-encode  │  │ Table-fix-align  │                       │
        │  │ (tool.py)        │  │ (tool.py)        │                       │
        │  │ test_tool.py     │  │ test_tool.py     │                       │
        │  │ fixtures/        │  │ fixtures/        │                       │
        │  └──────────────────┘  └──────────────────┘                       │
        │                                                                    │
        └───────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
                                PHASE 2 COMPLETE
```

### 3.3 Phase 3-6 Parallel Map

```
PHASE 3 - ORCHESTRATION
══════════════════════════════════════════════════════════════════════════════

        ┌───────────────────────────────────────────────────────────────────┐
        │                    [PARALLEL BLOCK]                                │
        │                                                                    │
        │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
        │  │ batch_processor  │  │ skill_discovery  │  │ watchdog.py      │ │
        │  │ .py              │  │ .py              │  │                  │ │
        │  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
        │  ┌──────────────────┐                                              │
        │  │ report_generator │                                              │
        │  │ .py              │                                              │
        │  └──────────────────┘                                              │
        └───────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ [SYNC - All components ready]
        ┌───────────────────────────────────────────────────────────────────┐
        │  [SEQUENTIAL]                                                      │
        │  ┌──────────────────────────────────────────────────────────────┐ │
        │  │ controller.py (integrates all components)                    │ │
        │  └──────────────────────────────────────────────────────────────┘ │
        └───────────────────────────────────────────────────────────────────┘

PHASE 4 - INSERT_QA_SKILL
══════════════════════════════════════════════════════════════════════════════

        ┌───────────────────────────────────────────────────────────────────┐
        │  [SEQUENTIAL]                                                      │
        │  templates/ → tool.py → skill.md → tests                          │
        └───────────────────────────────────────────────────────────────────┘

PHASE 5 - SKILL MIGRATION
══════════════════════════════════════════════════════════════════════════════

        ┌───────────────────────────────────────────────────────────────────┐
        │                    [PARALLEL BLOCK - REWRITES]                     │
        │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │
        │  │ qa-super   │ │ qa-BiDi    │ │ qa-code    │ │ qa-typeset │      │
        │  │ skill.md   │ │ skill.md   │ │ skill.md   │ │ skill.md   │      │
        │  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │
        └───────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ [SYNC]
        ┌───────────────────────────────────────────────────────────────────┐
        │  [SEQUENTIAL - VALIDATION]                                         │
        │  Real document testing → Performance benchmarks → Token metrics    │
        └───────────────────────────────────────────────────────────────────┘

PHASE 6 - DEPLOYMENT
══════════════════════════════════════════════════════════════════════════════

        ┌───────────────────────────────────────────────────────────────────┐
        │  [STRICTLY SEQUENTIAL]                                             │
        │  Backup → Test → Approval → Copy → Validate → Document             │
        └───────────────────────────────────────────────────────────────────┘
```

---

## 4. Detailed Task List

### 4.1 Phase 1 Tasks

| ID | Task | Priority | Dependencies | Parallel | Est. Effort |
|----|------|----------|--------------|----------|-------------|
| **P1-001** | Create project directory structure | P0 | None | - | Small |
| **P1-002** | Create qa_engine/__init__.py | P0 | P1-001 | Yes | Small |
| **P1-003** | Implement interfaces.py (Issue, Severity, DetectorInterface, FixerInterface) | P0 | P1-001 | Yes | Medium |
| **P1-004** | Implement document_analyzer.py | P0 | P1-001 | Yes | Medium |
| **P1-005** | Implement coordination.py (SQLite, locks, heartbeats) | P0 | P1-001 | Yes | Medium |
| **P1-006** | Implement logging_system.py | P0 | P1-001 | Yes | Medium |
| **P1-007** | Define qa_setup.json schema | P0 | P1-003 | No | Small |
| **P1-008** | Implement config_loader.py | P0 | P1-007 | No | Medium |
| **P1-009** | Write unit tests for interfaces | P0 | P1-003 | Yes | Small |
| **P1-010** | Write unit tests for document_analyzer | P0 | P1-004 | Yes | Small |
| **P1-011** | Write unit tests for coordination | P0 | P1-005 | Yes | Small |
| **P1-012** | Write unit tests for config_loader | P0 | P1-008 | No | Small |
| **P1-013** | Create test fixtures for Phase 1 | P0 | P1-001 | Yes | Small |
| **P1-014** | Phase 1 integration test | P0 | P1-009 to P1-012 | No | Small |

**Parallel Groups:**
- Group A (parallel): P1-002, P1-003, P1-004, P1-005, P1-006
- Group B (sequential after A): P1-007 → P1-008
- Group C (parallel with Group B): P1-009, P1-010, P1-011, P1-013
- Group D (sequential after all): P1-012 → P1-014

---

### 4.2 Phase 2 Tasks

| ID | Task | Priority | Dependencies | Parallel | Est. Effort |
|----|------|----------|--------------|----------|-------------|
| **P2-001** | Create qa-BiDi-detect/tool.py structure | P0 | P1-003 | Yes | Small |
| **P2-002** | Implement BiDi rules 1-5 (cover, table, section, reversed, header) | P0 | P2-001 | Yes | Large |
| **P2-003** | Implement BiDi rules 6-10 (numbers, english, tcolorbox, titles, acronyms) | P0 | P2-001 | Yes | Large |
| **P2-004** | Implement BiDi rules 11-15 (decimal, chapter, fbox, standalone, hebrew-in-english) | P0 | P2-001 | Yes | Large |
| **P2-005** | Create BiDi test fixtures (valid/invalid documents) | P0 | P2-001 | Yes | Medium |
| **P2-006** | Write BiDi detector tests | P0 | P2-002, P2-003, P2-004 | No | Medium |
| **P2-007** | Create qa-code-detect/tool.py structure | P0 | P1-003 | Yes | Small |
| **P2-008** | Implement Code phases 2-3 (background, encoding) | P0 | P2-007 | Yes | Medium |
| **P2-009** | Implement Code phases 4-6 (direction, title, f-string) | P0 | P2-007 | Yes | Medium |
| **P2-010** | Create Code test fixtures | P0 | P2-007 | Yes | Medium |
| **P2-011** | Write Code detector tests | P0 | P2-008, P2-009 | No | Medium |
| **P2-012** | Create qa-typeset-detect/tool.py | P1 | P1-003 | Yes | Medium |
| **P2-013** | Implement log parsing (hbox, vbox, undefined, float) | P1 | P2-012 | No | Medium |
| **P2-014** | Create Typeset test fixtures | P1 | P2-012 | Yes | Small |
| **P2-015** | Write Typeset detector tests | P1 | P2-013 | No | Small |
| **P2-016** | Create qa-table-detect/tool.py | P1 | P1-003 | Yes | Medium |
| **P2-017** | Implement table detection rules | P1 | P2-016 | No | Medium |
| **P2-018** | Write Table detector tests | P1 | P2-017 | No | Small |
| **P2-019** | Create qa-BiDi-fix-text/tool.py | P1 | P2-006 | Yes | Medium |
| **P2-020** | Create qa-BiDi-fix-numbers/tool.py | P1 | P2-006 | Yes | Medium |
| **P2-021** | Write BiDi fixer tests | P1 | P2-019, P2-020 | No | Small |
| **P2-022** | Create qa-code-fix-background/tool.py | P1 | P2-011 | Yes | Medium |
| **P2-023** | Create qa-code-fix-encoding/tool.py | P1 | P2-011 | Yes | Medium |
| **P2-024** | Write Code fixer tests | P1 | P2-022, P2-023 | No | Small |
| **P2-025** | Phase 2 integration tests | P0 | All P2 tasks | No | Medium |

**Parallel Groups:**
- Group A (parallel): P2-001, P2-007, P2-012, P2-016 (structure setup)
- Group B (parallel, after A): P2-002, P2-003, P2-004, P2-008, P2-009, P2-013, P2-017
- Group C (parallel, with B): P2-005, P2-010, P2-014 (fixtures)
- Group D (sequential, after B): P2-006, P2-011, P2-015, P2-018 (detector tests)
- Group E (parallel, after D): P2-019, P2-020, P2-022, P2-023 (fixers)
- Group F (sequential, after E): P2-021, P2-024 (fixer tests)
- Group G (final): P2-025 (integration)

---

### 4.3 Phase 3 Tasks

| ID | Task | Priority | Dependencies | Parallel | Est. Effort |
|----|------|----------|--------------|----------|-------------|
| **P3-001** | Create batch_processor.py structure | P0 | P1-003, P1-005 | Yes | Small |
| **P3-002** | Implement smart chunking (environment boundaries) | P0 | P3-001 | No | Medium |
| **P3-003** | Implement parallel chunk processing | P0 | P3-002 | No | Medium |
| **P3-004** | Implement result merging | P0 | P3-003 | No | Medium |
| **P3-005** | Write batch processor tests | P0 | P3-004 | No | Medium |
| **P3-006** | Create skill_discovery.py | P1 | P1-003 | Yes | Medium |
| **P3-007** | Implement skill scanning and parsing | P1 | P3-006 | No | Medium |
| **P3-008** | Implement hierarchy building | P1 | P3-007 | No | Small |
| **P3-009** | Write skill discovery tests | P1 | P3-008 | No | Small |
| **P3-010** | Create watchdog.py | P1 | P1-005 | Yes | Medium |
| **P3-011** | Implement monitoring loop | P1 | P3-010 | No | Medium |
| **P3-012** | Write watchdog tests | P1 | P3-011 | No | Small |
| **P3-013** | Create report_generator.py | P1 | P1-003 | Yes | Medium |
| **P3-014** | Implement markdown report | P1 | P3-013 | No | Medium |
| **P3-015** | Implement JSON report | P1 | P3-013 | No | Small |
| **P3-016** | Write report generator tests | P1 | P3-014, P3-015 | No | Small |
| **P3-017** | Create controller.py structure | P0 | All Phase 1, P3-005, P3-008 | No | Small |
| **P3-018** | Implement run_full_qa() | P0 | P3-017 | No | Large |
| **P3-019** | Implement run_family() | P0 | P3-017 | No | Medium |
| **P3-020** | Implement run_skill() | P0 | P3-017 | No | Medium |
| **P3-021** | Write controller tests | P0 | P3-018, P3-019, P3-020 | No | Medium |
| **P3-022** | Phase 3 integration tests | P0 | All P3 tasks | No | Medium |

**Parallel Groups:**
- Group A (parallel): P3-001, P3-006, P3-010, P3-013 (structure)
- Group B (sequential from A): P3-002→P3-003→P3-004→P3-005
- Group C (sequential from A): P3-007→P3-008→P3-009
- Group D (sequential from A): P3-011→P3-012
- Group E (sequential from A): P3-014→P3-015→P3-016
- Group F (after B, C): P3-017→P3-018→P3-019→P3-020→P3-021
- Group G (final): P3-022

---

### 4.4 Phase 4 Tasks

| ID | Task | Priority | Dependencies | Parallel | Est. Effort |
|----|------|----------|--------------|----------|-------------|
| **P4-001** | Create insert_qa_skill directory | P1 | Phase 3 | - | Small |
| **P4-002** | Create skill_template.md | P1 | P4-001 | Yes | Medium |
| **P4-003** | Create detector_template.py | P1 | P4-001 | Yes | Medium |
| **P4-004** | Create fixer_template.py | P1 | P4-001 | Yes | Medium |
| **P4-005** | Create test_template.py | P1 | P4-001 | Yes | Medium |
| **P4-006** | Create fixture templates | P1 | P4-001 | Yes | Small |
| **P4-007** | Implement tool.py for CREATE mode | P1 | P4-002 to P4-006 | No | Large |
| **P4-008** | Implement tool.py for SPLIT mode | P1 | P4-007 | No | Medium |
| **P4-009** | Implement parent orchestrator update | P1 | P4-007 | No | Medium |
| **P4-010** | Implement QA-CLAUDE.md update | P1 | P4-007 | No | Small |
| **P4-011** | Create skill.md for insert_qa_skill | P1 | P4-007 to P4-010 | No | Medium |
| **P4-012** | Write insert_qa_skill tests | P1 | P4-011 | No | Medium |
| **P4-013** | Integration test: create new skill | P1 | P4-012 | No | Medium |
| **P4-014** | Integration test: split existing skill | P1 | P4-012 | No | Medium |

**Parallel Groups:**
- Group A (parallel): P4-002, P4-003, P4-004, P4-005, P4-006 (templates)
- Group B (sequential after A): P4-007→P4-008→P4-009→P4-010→P4-011
- Group C (sequential after B): P4-012→P4-013, P4-014

---

### 4.5 Phase 5 Tasks

| ID | Task | Priority | Dependencies | Parallel | Est. Effort |
|----|------|----------|--------------|----------|-------------|
| **P5-001** | Rewrite qa-super/skill.md to standard | P1 | Phase 4 | Yes | Medium |
| **P5-002** | Rewrite qa-BiDi/skill.md to standard | P1 | Phase 4 | Yes | Medium |
| **P5-003** | Rewrite qa-code/skill.md to standard | P1 | Phase 4 | Yes | Medium |
| **P5-004** | Rewrite qa-typeset/skill.md to standard | P1 | Phase 4 | Yes | Medium |
| **P5-005** | Rewrite qa-table/skill.md to standard | P1 | Phase 4 | Yes | Medium |
| **P5-006** | Rewrite qa-infra/skill.md to standard | P1 | Phase 4 | Yes | Medium |
| **P5-007** | Rewrite qa-bib/skill.md to standard | P1 | Phase 4 | Yes | Small |
| **P5-008** | Rewrite qa-img/skill.md to standard | P1 | Phase 4 | Yes | Small |
| **P5-009** | Update qa-BiDi-detect/skill.md with tool reference | P1 | P2-006 | Yes | Small |
| **P5-010** | Update qa-code-detect/skill.md with tool reference | P1 | P2-011 | Yes | Small |
| **P5-011** | Update all L2 skills with tool references | P1 | Phase 2 | Yes | Medium |
| **P5-012** | Update QA-CLAUDE.md architecture | P1 | P5-001 to P5-011 | No | Medium |
| **P5-013** | Update full-pdf-qa.md command | P1 | P5-012 | No | Small |
| **P5-014** | Create test with real Hebrew-English document | P0 | P5-013 | No | Medium |
| **P5-015** | Measure token usage (before vs after) | P0 | P5-014 | No | Small |
| **P5-016** | Performance benchmark | P0 | P5-014 | Yes | Small |
| **P5-017** | Create deployment readiness report | P0 | P5-015, P5-016 | No | Medium |

**Parallel Groups:**
- Group A (parallel): P5-001 to P5-011 (skill rewrites)
- Group B (sequential after A): P5-012→P5-013
- Group C (sequential after B): P5-014→P5-015
- Group D (parallel with C): P5-016
- Group E (after C, D): P5-017

---

### 4.6 Phase 6 Tasks

| ID | Task | Priority | Dependencies | Parallel | Est. Effort |
|----|------|----------|--------------|----------|-------------|
| **P6-001** | Create backup script | P0 | Phase 5 | - | Small |
| **P6-002** | Execute backup of global skills | P0 | P6-001 | No | Small |
| **P6-003** | Run full local test suite | P0 | P6-002 | No | Medium |
| **P6-004** | Generate deployment report | P0 | P6-003 | No | Small |
| **P6-005** | Present to user for approval | P0 | P6-004 | No | - |
| **P6-006** | Copy skills to global location | P0 | P6-005 (approval) | No | Small |
| **P6-007** | Copy qa_engine to global location | P0 | P6-006 | No | Small |
| **P6-008** | Run validation tests on global | P0 | P6-007 | No | Medium |
| **P6-009** | Update global QA-CLAUDE.md | P0 | P6-008 | No | Small |
| **P6-010** | Document rollback procedure | P0 | P6-009 | No | Small |
| **P6-011** | Final validation with real project | P0 | P6-010 | No | Medium |

**Note:** Phase 6 is STRICTLY SEQUENTIAL - no parallel execution allowed.

---

## 5. Testing Strategy

### 5.1 Test Hierarchy

```
TEST STRUCTURE
══════════════════════════════════════════════════════════════════════════════

qa-test-framework/
├── conftest.py                    # Shared pytest fixtures
├── base_test.py                   # QASkillTestBase class
│
├── unit/                          # Unit tests (run in parallel)
│   ├── test_interfaces.py
│   ├── test_document_analyzer.py
│   ├── test_coordination.py
│   ├── test_config_loader.py
│   ├── test_logging_system.py
│   ├── test_batch_processor.py
│   └── test_controller.py
│
├── skill_tests/                   # Skill-specific tests (run in parallel)
│   ├── test_bidi_detector.py
│   ├── test_bidi_fixer.py
│   ├── test_code_detector.py
│   ├── test_code_fixer.py
│   ├── test_typeset_detector.py
│   └── test_table_detector.py
│
├── integration/                   # Integration tests (sequential)
│   ├── test_full_pipeline.py
│   ├── test_batch_processing.py
│   ├── test_parallel_families.py
│   └── test_insert_qa_skill.py
│
└── fixtures/                      # Shared test fixtures
    ├── valid_hebrew_doc.tex
    ├── invalid_bidi_doc.tex
    ├── large_document.tex
    └── sample.log
```

### 5.2 Test Coverage Requirements

| Component | Min Coverage | Notes |
|-----------|--------------|-------|
| qa_engine/*.py | 90% | All Python modules |
| */tool.py | 90% | All Python tools |
| Integration tests | N/A | All critical paths covered |

### 5.3 Test Execution Strategy

```bash
# Run all unit tests in parallel
pytest unit/ -n auto

# Run skill tests in parallel
pytest skill_tests/ -n auto

# Run integration tests sequentially
pytest integration/ -v

# Generate coverage report
pytest --cov=qa_engine --cov-report=html
```

### 5.4 Test Fixtures Requirements

Each detector/fixer tool MUST have:

```
fixtures/
├── valid_document.tex      # No issues expected
├── invalid_document.tex    # Known issues
├── edge_case_1.tex         # Edge cases
└── expected_output.json    # Expected detection results
```

### 5.5 Base Test Class

```python
# qa-test-framework/base_test.py

class QASkillTestBase:
    """Base class for all skill tests."""

    @classmethod
    def load_fixture(cls, name: str) -> str:
        """Load fixture file content."""
        pass

    def assertIssueFound(self, issues: list, rule: str):
        """Assert that a specific rule was triggered."""
        pass

    def assertNoIssue(self, issues: list, rule: str):
        """Assert that a specific rule was NOT triggered."""
        pass

    def assertIssueCount(self, issues: list, expected: int):
        """Assert exact number of issues found."""
        pass

    def assertFixApplied(self, original: str, fixed: str, pattern: str):
        """Assert that a fix was correctly applied."""
        pass
```

---

## 6. Deployment Strategy

### 6.1 Development Environment Setup

```
LOCAL PROJECT STRUCTURE:
C:\25D\Richman\skill-python-base\
├── .claude/
│   └── skills/                    # Local skill development
│       ├── qa-super/
│       ├── qa-BiDi/
│       ├── qa-BiDi-detect/
│       │   ├── skill.md
│       │   ├── tool.py
│       │   ├── test_tool.py
│       │   └── fixtures/
│       └── ...
├── qa_engine/                     # Python backend
│   ├── __init__.py
│   ├── interfaces.py
│   ├── controller.py
│   └── ...
├── tests/                         # Test framework
├── docs/                          # Documentation
├── qa_setup.json                  # Default config
└── pytest.ini                     # Test configuration
```

### 6.2 Deployment Paths

| Type | Source | Destination |
|------|--------|-------------|
| Skills | `skill-python-base/.claude/skills/qa-*` | `C:\Users\gal-t\.claude\skills\qa-*` |
| Engine | `skill-python-base/qa_engine/` | `C:\Users\gal-t\.claude\qa_engine\` |
| Config | `skill-python-base/qa_setup.json` | `C:\Users\gal-t\.claude\qa_setup.json` |

### 6.3 Deployment Checklist

Before deployment:
- [ ] All unit tests pass (100%)
- [ ] All integration tests pass
- [ ] Test coverage >= 90%
- [ ] Token reduction verified (60%+)
- [ ] Detection consistency verified (100%)
- [ ] Performance benchmarks acceptable
- [ ] Documentation complete
- [ ] User has reviewed all changes
- [ ] User has EXPLICITLY approved deployment

Deployment steps:
- [ ] Create timestamped backup of existing global skills
- [ ] Copy all qa-* skill directories to global
- [ ] Copy qa_engine directory to global
- [ ] Update global QA-CLAUDE.md
- [ ] Run validation tests on global installation
- [ ] Test with real project
- [ ] Document rollback procedure

### 6.4 Rollback Procedure

```powershell
# If issues discovered after deployment:

# 1. Remove new skills
Remove-Item -Recurse "C:\Users\gal-t\.claude\skills\qa-*"

# 2. Restore from backup
Copy-Item -Recurse "C:\Users\gal-t\.claude\skills-backup-YYYYMMDD\qa-*" "C:\Users\gal-t\.claude\skills\"

# 3. Remove qa_engine
Remove-Item -Recurse "C:\Users\gal-t\.claude\qa_engine"

# 4. Verify rollback
claude /full-pdf-qa "path/to/test/project"
```

---

## 7. Risk Management

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation | Contingency |
|------|-------------|--------|------------|-------------|
| Regex patterns miss edge cases | Medium | High | Comprehensive test fixtures | Add pattern on discovery |
| Batch boundary cuts environment | Medium | Medium | Smart chunking logic | Manual chunk size config |
| SQLite locking issues | Low | Medium | WAL mode, connection pool | File-based fallback |
| Python import errors | Medium | High | Graceful degradation | Skill-only fallback |
| Performance regression | Low | Medium | Benchmarks in CI | Optimization pass |

### 7.2 Project Risks

| Risk | Probability | Impact | Mitigation | Contingency |
|------|-------------|--------|------------|-------------|
| Scope creep | High | Medium | Strict PRD adherence | Phase trimming |
| Integration complexity | Medium | High | Incremental phases | Simplify interface |
| Test coverage gaps | Medium | High | TDD approach | Post-hoc testing |
| Documentation lag | High | Low | Doc-as-code | Post-release docs |

### 7.3 Risk Response Plan

```
RISK ESCALATION PATH:
────────────────────────────────────────────────────────────────────────

1. Detected: Log issue, continue if non-blocking
2. Blocking: Pause work, assess impact
3. Critical: Rollback to last known good state
4. Unrecoverable: Escalate to user for decision

MONITORING:
- Test failures: Immediate investigation
- Performance degradation: Benchmark comparison
- Token increase: Compare with baseline
```

---

## 8. Verification Checkpoints

### 8.1 Phase Gate Criteria

| Phase | Gate | Criteria |
|-------|------|----------|
| 1 | Foundation Complete | All interfaces defined, coordination works, config loads |
| 2 | Tools Ready | All detectors implemented, 80%+ coverage, fixers work |
| 3 | Engine Ready | Controller orchestrates full pipeline, batch works |
| 4 | Meta-skill Ready | insert_qa_skill creates valid skills |
| 5 | Validation Complete | Real project QA, 60%+ token reduction |
| 6 | Deployment Complete | Global installation verified, rollback documented |

### 8.2 Quality Gates

Each phase must pass:
- [ ] All unit tests pass
- [ ] Code review complete
- [ ] Documentation updated
- [ ] Integration verified
- [ ] No P0 bugs open

### 8.3 Final Acceptance Checklist

- [ ] FR-101 to FR-105 (Core Engine) implemented
- [ ] FR-201 to FR-204 (Coordination) implemented
- [ ] FR-301 to FR-303 (Logging) implemented
- [ ] FR-401 to FR-404 (Detection Tools) implemented
- [ ] FR-501 to FR-502 (Fix Tools) implemented
- [ ] FR-601 to FR-603 (Skill Management) implemented
- [ ] FR-701 to FR-704 (Testing) implemented
- [ ] FR-801 to FR-802 (Configuration) implemented
- [ ] FR-901 to FR-902 (Reporting) implemented
- [ ] NFR-101 to NFR-104 (Performance) met
- [ ] NFR-201 to NFR-204 (Reliability) met
- [ ] NFR-301 to NFR-303 (Usability) met
- [ ] NFR-401 to NFR-404 (Maintainability) met
- [ ] NFR-501 to NFR-503 (Security) met
- [ ] Detector/Fixer separation enforced
- [ ] All skills follow Claude CLI standards
- [ ] Python files <150 lines
- [ ] 90%+ test coverage
- [ ] 60%+ token reduction verified
- [ ] User approval obtained

---

## Appendix A: Task Priority Legend

| Priority | Description | Must Complete |
|----------|-------------|---------------|
| P0 | Critical - Blocking | Before next phase |
| P1 | High - Important | Before deployment |
| P2 | Medium - Nice to have | After deployment OK |

## Appendix B: Effort Estimation Legend

| Effort | Description | Approximate |
|--------|-------------|-------------|
| Small | Simple task | 1-2 hours |
| Medium | Moderate complexity | 3-4 hours |
| Large | Complex task | 5-8 hours |

---

*End of Implementation Plan*
