# Product Requirements Document (PRD)
# QA Skill Python Base System

**Document Version:** 1.1.0
**Date:** 2025-12-15
**Author:** Claude Code Architecture Team
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [Goals and Objectives](#3-goals-and-objectives)
4. [Target Users](#4-target-users)
5. [**MANDATORY: Planning Requirements**](#5-mandatory-planning-requirements)
6. [**Development Workflow**](#6-development-workflow)
7. [**Claude CLI Skill Standards**](#7-claude-cli-skill-standards)
8. [**Skill Resources and Tools**](#8-skill-resources-and-tools)
9. [Functional Requirements](#9-functional-requirements)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Technical Architecture](#11-technical-architecture)
12. [User Stories](#12-user-stories)
13. [API Specifications](#13-api-specifications)
14. [Data Models](#14-data-models)
15. [Configuration Schema](#15-configuration-schema)
16. [Success Metrics](#16-success-metrics)
17. [Dependencies](#17-dependencies)
18. [Constraints and Assumptions](#18-constraints-and-assumptions)
19. [Risks and Mitigations](#19-risks-and-mitigations)
20. [Implementation Phases](#20-implementation-phases)
21. [Acceptance Criteria](#21-acceptance-criteria)
22. [Appendices](#22-appendices)

---

## 1. Executive Summary

### 1.1 Problem Statement

The current Claude CLI QA skills system for Hebrew-English LaTeX documents suffers from:

- **High token consumption**: LLM performs regex-based detection that could be deterministic Python
- **Inconsistent results**: Same input may produce different outputs across runs
- **No batch processing**: Large documents (10,000+ lines) cannot be processed efficiently
- **No coordination**: Multiple agents cannot safely work on the same project
- **No test framework**: No way to verify skills work correctly
- **Manual integration**: Adding new skills requires updating multiple files manually

### 1.2 Proposed Solution

Build a **hybrid skill/Python tool system** that:

- Delegates deterministic operations (regex detection, pattern replacement) to Python
- Keeps orchestration and judgment logic in Claude skills
- Provides batch processing for large documents
- Implements coordination primitives (mutex, semaphores) for multi-agent scenarios
- Includes comprehensive test framework
- Offers `insert_qa_skill` meta-skill for automated skill creation

### 1.3 Expected Outcomes

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Token usage per QA run | ~50,000 | ~15,000 | 70% reduction |
| Detection consistency | ~85% | 100% | Deterministic |
| Large document support | No | Yes | New capability |
| Test coverage | 0% | 90%+ | New capability |
| Skill creation time | ~2 hours | ~10 min | 12x faster |

---

## 2. Product Vision

### 2.1 Vision Statement

> Create a **fast, reliable, token-efficient QA orchestration system** for LaTeX documents that combines the flexibility of Claude CLI skills with the precision of Python tools, enabling consistent quality assurance at scale.

### 2.2 Product Principles

1. **Determinism First**: Prefer Python for any operation that can be fully specified
2. **Token Efficiency**: Minimize LLM calls for repetitive operations
3. **Composability**: Skills and tools should be independently testable and combinable
4. **Configuration over Code**: Behavior should be configurable via `qa_setup.json`
5. **Fail Safe**: System should handle errors gracefully and never corrupt documents

### 2.3 Out of Scope

- GUI interface (CLI only)
- Support for non-LaTeX documents
- Real-time collaborative editing
- Cloud deployment (local execution only)

---

## 3. Goals and Objectives

### 3.1 Primary Goals

| ID | Goal | Success Criteria |
|----|------|------------------|
| G1 | Reduce token consumption | 60-70% reduction in tokens per QA run |
| G2 | Achieve deterministic detection | 100% consistent results for same input |
| G3 | Support large documents | Process 50,000+ line documents |
| G4 | Enable automated testing | 90%+ test coverage for Python tools |
| G5 | Automate skill creation | `insert_qa_skill` creates complete skill in <5 commands |

### 3.2 Secondary Goals

| ID | Goal | Success Criteria |
|----|------|------------------|
| G6 | Improve debugging | Structured logs with timestamps and agent IDs |
| G7 | Enable parallel execution | L1 families run concurrently |
| G8 | Provide progress monitoring | Real-time progress tracking via shared state |
| G9 | Support graceful degradation | Continue on non-critical failures |

### 3.3 Non-Goals

- Replacing all skills with Python (judgment still needs LLM)
- Supporting languages other than Hebrew-English
- Building a web service

---

## 4. Target Users

### 4.1 Primary Users

#### User Persona 1: LaTeX Document Author
- **Role**: Creates Hebrew-English academic documents
- **Need**: Automatic detection and fixing of BiDi, code, table issues
- **Skill Level**: Intermediate LaTeX, beginner CLI
- **Usage Frequency**: Weekly

#### User Persona 2: QA Skill Developer
- **Role**: Creates and maintains QA skills
- **Need**: Easy skill creation, testing, and integration
- **Skill Level**: Advanced Python, intermediate CLI
- **Usage Frequency**: Monthly

#### User Persona 3: System Administrator
- **Role**: Manages QA configuration across projects
- **Need**: Centralized configuration, monitoring, logging
- **Skill Level**: Advanced CLI, intermediate Python
- **Usage Frequency**: As needed

### 4.2 User Environments

| Environment | OS | Python | Claude CLI |
|-------------|-----|--------|------------|
| Primary | Windows 10/11 | 3.10+ | Latest |
| Secondary | macOS | 3.10+ | Latest |
| Tertiary | Linux (Ubuntu) | 3.10+ | Latest |

---

## 5. MANDATORY: Planning Requirements

### 5.1 Full Implementation Plan Required

**CRITICAL:** Before any implementation begins, the developer MUST create:

1. **Complete Implementation Plan** - A detailed plan document covering:
   - Architecture decisions and rationale
   - Component breakdown with dependencies
   - Integration strategy
   - Testing strategy
   - Deployment strategy

2. **Detailed Todo List** - A comprehensive task list with:
   - All tasks broken down to actionable items (max 2-hour tasks)
   - Clear dependencies between tasks
   - Priority assignments (P0, P1, P2)
   - Parallel execution opportunities identified
   - Acceptance criteria for each task

### 5.2 Plan Document Structure

The implementation plan MUST follow this structure:

```markdown
# Implementation Plan - QA Skill Python Base

## 1. Architecture Overview
   - System components
   - Data flow diagrams
   - Integration points

## 2. Phase Breakdown
   - Phase 1: [Tasks, Dependencies, Parallel Opportunities]
   - Phase 2: [Tasks, Dependencies, Parallel Opportunities]
   - ...

## 3. Parallel Execution Map
   - Which tasks can run simultaneously
   - Resource conflicts to avoid
   - Synchronization points

## 4. Testing Strategy
   - Unit test plan
   - Integration test plan
   - Validation checkpoints

## 5. Deployment Strategy
   - Local development workflow
   - Global skill replacement procedure
   - Rollback plan
```

### 5.3 Todo List Requirements

The todo list MUST:

- [ ] Include ALL tasks from this PRD
- [ ] Mark tasks that can be executed in PARALLEL
- [ ] Identify BLOCKING tasks that must complete before others
- [ ] Include test tasks for each component
- [ ] Include documentation tasks
- [ ] Include validation/review checkpoints

### 5.4 Parallel Execution Design Principle

**MANDATORY:** The design MUST maximize parallel execution wherever possible.

#### Parallel Execution Guidelines:

| Scenario | Parallel Approach |
|----------|-------------------|
| L1 Family Orchestrators | Run ALL families in parallel (qa-BiDi, qa-code, qa-table, etc.) |
| L2 Detection Skills | Run all detectors within a family in parallel |
| Python Tool Development | Develop independent tools in parallel |
| Test Execution | Run test suites in parallel |
| File Processing | Process independent files in parallel |
| Chunk Processing | Process document chunks in parallel |

#### Identify Parallel Opportunities:

```
PARALLEL EXECUTION MAP:

Phase 1 (Foundation):
├── [PARALLEL] document_analyzer.py
├── [PARALLEL] coordination.py
├── [PARALLEL] interfaces.py
└── [SEQUENTIAL - depends on above] controller.py

Phase 2 (Python Tools):
├── [PARALLEL] BiDiDetector
├── [PARALLEL] CodeDetector
├── [PARALLEL] TypesetDetector
└── [PARALLEL] TableDetector

Phase 3 (Testing):
├── [PARALLEL] test_bidi.py
├── [PARALLEL] test_code.py
├── [PARALLEL] test_typeset.py
└── [SEQUENTIAL - after all tests] integration_test.py
```

### 5.5 Planning Deliverables Checklist

Before implementation begins, verify:

- [ ] Implementation plan document created
- [ ] All PRD sections covered in plan
- [ ] Parallel execution opportunities identified
- [ ] Todo list created with all tasks
- [ ] Dependencies mapped
- [ ] Blocking tasks identified
- [ ] Testing checkpoints defined
- [ ] User approval obtained for plan

---

## 6. Development Workflow

### 6.1 Local Development Environment

**ALL development MUST occur in the local project folder:**

```
C:\25D\Richman\skill-python-base\
├── .claude/
│   └── skills/           # LOCAL skill development
│       ├── qa-super/
│       ├── qa-BiDi/
│       ├── qa-BiDi-detect/
│       │   ├── skill.md
│       │   ├── tool.py
│       │   └── test_tool.py
│       └── ...
├── qa_engine/            # Python backend
├── tests/                # Integration tests
└── docs/                 # Documentation
```

### 6.2 Development vs Production Paths

| Environment | Path | Purpose |
|-------------|------|---------|
| **LOCAL (Development)** | `C:\25D\Richman\skill-python-base\.claude\skills\` | All development, testing, iteration |
| **GLOBAL (Production)** | `C:\Users\gal-t\.claude\skills\` | Final deployed skills |

### 6.3 Development Workflow Stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STAGE 1: LOCAL DEVELOPMENT                                              │
│  ─────────────────────────────                                          │
│  Location: skill-python-base/.claude/skills/                            │
│                                                                          │
│  1. Create/modify skill.md files                                        │
│  2. Develop Python tools (tool.py)                                      │
│  3. Write unit tests (test_tool.py)                                     │
│  4. Create test fixtures                                                │
│  5. Run local tests                                                     │
│                                                                          │
│                         ▼                                                │
│                                                                          │
│  STAGE 2: LOCAL TESTING                                                  │
│  ──────────────────────                                                 │
│  Location: skill-python-base/                                           │
│                                                                          │
│  1. Run ALL unit tests: python -m pytest                                │
│  2. Run integration tests                                               │
│  3. Test with sample LaTeX documents                                    │
│  4. Verify token reduction metrics                                      │
│  5. All tests MUST pass                                                 │
│                                                                          │
│                         ▼                                                │
│                                                                          │
│  STAGE 3: USER APPROVAL                                                  │
│  ──────────────────────                                                 │
│                                                                          │
│  1. Generate test report                                                │
│  2. Document changes made                                               │
│  3. Present to user for review                                          │
│  4. User explicitly approves deployment                                 │
│                                                                          │
│                         ▼                                                │
│                                                                          │
│  STAGE 4: GLOBAL DEPLOYMENT                                              │
│  ─────────────────────────                                              │
│  Target: C:\Users\gal-t\.claude\skills\                                 │
│                                                                          │
│  1. Backup existing global skills                                       │
│  2. Copy LOCAL skills to GLOBAL location                                │
│  3. Verify global skills work                                           │
│  4. Run validation tests                                                │
│  5. Update QA-CLAUDE.md                                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Deployment Prerequisites

**Before deploying to global Claude CLI skills:**

- [ ] ALL unit tests pass (100%)
- [ ] ALL integration tests pass
- [ ] Token reduction verified (60%+ reduction)
- [ ] Detection accuracy verified (100% consistency)
- [ ] Documentation complete
- [ ] User has reviewed changes
- [ ] User has EXPLICITLY approved deployment
- [ ] Backup of existing global skills created

### 6.5 Global Skill Replacement Procedure

```bash
# Step 1: Backup existing global skills
cp -r "C:\Users\gal-t\.claude\skills\qa-*" "C:\Users\gal-t\.claude\skills-backup-YYYYMMDD\"

# Step 2: Copy new skills to global
cp -r "C:\25D\Richman\skill-python-base\.claude\skills\qa-*" "C:\Users\gal-t\.claude\skills\"

# Step 3: Copy Python engine
cp -r "C:\25D\Richman\skill-python-base\qa_engine" "C:\Users\gal-t\.claude\"

# Step 4: Verify installation
cd "C:\Users\gal-t\.claude\skills"
python -m pytest qa-*/test_*.py

# Step 5: Test with real project
/full-pdf-qa "path/to/test/project"
```

### 6.6 Rollback Procedure

If issues are discovered after deployment:

```bash
# Restore from backup
rm -rf "C:\Users\gal-t\.claude\skills\qa-*"
cp -r "C:\Users\gal-t\.claude\skills-backup-YYYYMMDD\qa-*" "C:\Users\gal-t\.claude\skills\"
```

---

## 7. Claude CLI Skill Standards

### 7.1 Professional Skill Writing Requirements

**MANDATORY:** All skills MUST be written following Claude CLI professional standards.

When creating NEW skills or REWRITING existing skills, follow these requirements:

### 7.2 Skill File Structure Standard

```markdown
---
name: qa-{family}-{type}-{specific}
description: {Clear, concise description} (Level {N} skill)
version: X.Y.Z
author: QA Team
tags: [qa, {family}, {type}, level-{N}, {relevant-tags}]
tools: [Read, Write, Edit, Grep, Glob, Bash]  # If applicable
---

# {Skill Title} (Level {N})

## Agent Identity
- **Name:** {Display Name}
- **Role:** {Role Description}
- **Level:** {N} (Skill/Orchestrator)
- **Parent:** {Parent skill} (Level {N-1})

## Coordination

### Reports To
- {Parent orchestrator}

### Manages (for orchestrators)
- {Child skills list}

### Reads
- {Input sources}

### Writes
- {Output destinations}

## Mission Statement
{Clear statement of skill's purpose}

## {Main Content Sections}
{Detection Rules / Fix Patterns / Workflow / etc.}

## Input/Output Format

### Input
{Structured input specification}

### Output
{JSON or structured output format}

## Version History
- **vX.Y.Z** (YYYY-MM-DD): {Change description}

---

**Parent:** {parent-skill}
**Children:** {child-skills} (if any)
**Coordination:** qa-orchestration/QA-CLAUDE.md
```

### 7.3 Naming Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| Skill folder | `qa-{family}-{type}-{specific}` | `qa-BiDi-detect-footnotes` |
| Skill file | `skill.md` | `skill.md` |
| Python tool | `tool.py` | `tool.py` |
| Test file | `test_tool.py` | `test_tool.py` |
| Fixtures folder | `fixtures/` | `fixtures/` |

### 7.4 Skill Quality Checklist

Before a skill is considered complete:

- [ ] Follows standard file structure
- [ ] Has complete YAML frontmatter
- [ ] Has Agent Identity section
- [ ] Has Coordination section
- [ ] Has Mission Statement
- [ ] Has Input/Output format specification
- [ ] Has Version History
- [ ] Has proper naming convention
- [ ] All tags are relevant and lowercase
- [ ] Description is clear and includes level
- [ ] Parent/Children relationships documented

### 7.5 Version Numbering Standard

Use Semantic Versioning (SemVer):

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking change | MAJOR | 1.0.0 → 2.0.0 |
| New feature | MINOR | 1.0.0 → 1.1.0 |
| Bug fix | PATCH | 1.0.0 → 1.0.1 |
| QA Mechanism Fix | MINOR | 1.0.0 → 1.1.0 |

### 7.6 Documentation Standards

Every skill MUST include:

1. **Clear examples** - BAD vs GOOD code examples
2. **Regex patterns** - If detection uses regex, document the patterns
3. **Error handling** - How errors are handled
4. **Integration notes** - How skill integrates with others

### 7.7 MANDATORY: Clear Separation Between Detectors and Fixers

**CRITICAL ARCHITECTURAL REQUIREMENT:** There MUST be a clear and strict separation between Detection skills and Fix skills.

#### Separation Principles

```
┌─────────────────────────────────────────────────────────────────────────┐
│           DETECTOR / FIXER SEPARATION ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DETECTORS (qa-*-detect)              FIXERS (qa-*-fix-*)               │
│  ─────────────────────────            ─────────────────────             │
│                                                                          │
│  Purpose:                             Purpose:                           │
│  - Find issues                        - Resolve issues                   │
│  - Report locations                   - Apply corrections                │
│  - Categorize problems                - Verify fixes                     │
│                                                                          │
│  MUST NOT:                            MUST NOT:                          │
│  - Modify any files                   - Perform detection                │
│  - Apply any fixes                    - Search for new issues            │
│  - Change document state              - Report unfixed issues            │
│                                                                          │
│  Output:                              Input:                             │
│  - List[Issue]                        - List[Issue] from detector        │
│  - Issue locations                    - File content                     │
│  - Issue severity                                                        │
│                                       Output:                            │
│                                       - Fixed content                    │
│                                       - Fix report                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Detector Requirements

| Requirement | Description |
|-------------|-------------|
| **Single Responsibility** | ONLY detect issues, never fix them |
| **Stateless** | No side effects, no file modifications |
| **Deterministic** | Same input always produces same output |
| **Complete Output** | Return ALL detected issues in structured format |
| **No Fix Logic** | NEVER contain fix patterns or replacement code |

#### Fixer Requirements

| Requirement | Description |
|-------------|-------------|
| **Single Responsibility** | ONLY fix issues provided by detector |
| **Issue-Driven** | Operate ONLY on issues passed from detector |
| **No Detection** | NEVER search for issues independently |
| **Targeted Changes** | Only modify what's needed to fix the issue |
| **Verification Ready** | Output should be verifiable by re-running detector |

#### Workflow Enforcement

```
CORRECT WORKFLOW:
─────────────────
1. Detector runs → Produces List[Issue]
2. Issues passed to Fixer
3. Fixer applies fixes → Produces fixed content
4. Detector runs again → Verifies no issues remain

INCORRECT (FORBIDDEN):
──────────────────────
❌ Detector that also fixes issues
❌ Fixer that searches for issues
❌ Combined detect-and-fix skill
❌ Fixer that operates without issue list input
```

#### Naming Convention Enforcement

| Skill Type | Naming Pattern | Example |
|------------|----------------|---------|
| Detector | `qa-{family}-detect` or `qa-{family}-detect-{specific}` | `qa-BiDi-detect`, `qa-BiDi-detect-tikz` |
| Fixer | `qa-{family}-fix-{specific}` | `qa-BiDi-fix-text`, `qa-BiDi-fix-numbers` |

#### Interface Separation

```python
# DETECTOR INTERFACE - Read-only, returns issues
class DetectorInterface(ABC):
    @abstractmethod
    def detect(self, content: str, file_path: str) -> List[Issue]:
        """Detect issues. MUST NOT modify content."""
        pass

# FIXER INTERFACE - Takes issues, returns fixed content
class FixerInterface(ABC):
    @abstractmethod
    def fix(self, content: str, issues: List[Issue]) -> str:
        """Fix issues. MUST NOT detect new issues."""
        pass
```

#### Verification Checklist

Before any skill is accepted:

**For Detectors:**
- [ ] Skill name contains `-detect`
- [ ] No file write operations
- [ ] No fix patterns in code
- [ ] Returns List[Issue] only
- [ ] Can run multiple times with same result

**For Fixers:**
- [ ] Skill name contains `-fix-`
- [ ] Takes List[Issue] as input
- [ ] No detection logic in code
- [ ] Only modifies content related to input issues
- [ ] Can be verified by re-running detector

---

## 8. Skill Resources and Tools

### 8.1 Skill Resources Support

**MANDATORY:** Skills MUST support adding resources for enhanced functionality.

#### Resource Types:

| Resource Type | Location | Purpose |
|---------------|----------|---------|
| Python Tools | `tool.py` | Deterministic detection/fix logic |
| Test Files | `test_tool.py` | Unit tests for Python tools |
| Fixtures | `fixtures/` | Test data files |
| Templates | `templates/` | Code generation templates |
| Configuration | `config.json` | Skill-specific configuration |
| Documentation | `README.md` | Extended documentation |

### 8.2 Resource Directory Structure

```
qa-{skill-name}/
├── skill.md              # REQUIRED: Skill definition
├── tool.py               # RECOMMENDED: Python tool
├── test_tool.py          # RECOMMENDED: Unit tests
├── fixtures/             # RECOMMENDED: Test fixtures
│   ├── valid_document.tex
│   └── invalid_document.tex
├── templates/            # OPTIONAL: Code templates
├── config.json           # OPTIONAL: Skill config
└── README.md             # OPTIONAL: Extended docs
```

### 8.3 Python Tool Recommendations

**When to Add Python Tools:**

| Scenario | Recommendation |
|----------|----------------|
| Regex-based detection | **MUST** add Python tool |
| Pattern replacement | **MUST** add Python tool |
| File parsing (log, tex) | **MUST** add Python tool |
| Complex orchestration | KEEP in skill |
| Judgment/decisions | KEEP in skill |
| User interaction | KEEP in skill |

### 8.4 Tool Integration Pattern

```markdown
## Skill Definition (skill.md)

### Python Tool Reference

This skill uses Python tools for deterministic operations:

| Tool Function | Purpose | Input | Output |
|---------------|---------|-------|--------|
| `detect()` | Run detection rules | content, file_path | List[Issue] |
| `fix()` | Apply fixes | content, issues | fixed_content |

### Tool Invocation

```python
from tool import detector

# Run detection
issues = detector.detect(content, file_path)

# Apply fixes (if fix skill)
fixed = fixer.fix(content, issues)
```
```

### 8.5 Resource Addition Checklist

When adding resources to a skill:

- [ ] Create resource in appropriate subdirectory
- [ ] Update skill.md to reference the resource
- [ ] Add tests for new resource
- [ ] Document resource purpose and usage
- [ ] Verify resource follows naming conventions
- [ ] Update version history in skill.md

### 8.6 Recommended Resources for Each Skill Type

#### Detection Skills (qa-*-detect)
```
RECOMMENDED RESOURCES:
├── tool.py           # Detection logic (Python)
├── test_tool.py      # Unit tests
└── fixtures/         # Test documents
    ├── valid_*.tex   # Documents without issues
    └── invalid_*.tex # Documents with known issues
```

#### Fix Skills (qa-*-fix-*)
```
RECOMMENDED RESOURCES:
├── tool.py           # Fix logic (Python)
├── test_tool.py      # Unit tests
└── fixtures/
    ├── before_*.tex  # Documents before fix
    └── after_*.tex   # Expected result after fix
```

#### Orchestrator Skills (qa-{family})
```
RECOMMENDED RESOURCES:
├── config.json       # Family-specific configuration
└── README.md         # Extended documentation
```

---

## 9. Functional Requirements

### 9.1 Core Engine (FR-100 Series)

#### FR-101: Document Analysis
**Priority:** P0 (Critical)
**Description:** System shall analyze LaTeX documents to determine size and processing strategy.

**Acceptance Criteria:**
- AC1: Count total lines across all .tex files
- AC2: Count total files in project
- AC3: Estimate token count
- AC4: Recommend processing strategy (single_pass, file_by_file, chunked, parallel_chunked)

**Input:** Project path
**Output:** Analysis metrics dict

---

#### FR-102: Batch Processing
**Priority:** P0 (Critical)
**Description:** System shall process large documents in batches to stay within context limits.

**Acceptance Criteria:**
- AC1: Split documents into chunks of configurable size (default 1000 lines)
- AC2: Process chunks in parallel (configurable workers, default 4)
- AC3: Merge results from all chunks
- AC4: Handle chunk boundaries (no split mid-environment)

**Configuration:**
```json
{
  "batch_processing": {
    "enabled": true,
    "batch_size": 50,
    "chunk_lines": 1000,
    "max_workers": 4
  }
}
```

---

#### FR-103: Skill Discovery
**Priority:** P0 (Critical)
**Description:** System shall automatically discover all available QA skills.

**Acceptance Criteria:**
- AC1: Scan `.claude/skills/qa-*` directories
- AC2: Parse skill.md frontmatter for metadata
- AC3: Build skill hierarchy (L0, L1, L2)
- AC4: Identify Python tools (tool.py) for each skill

**Output:** Skill registry dict with hierarchy

---

#### FR-104: Orchestration Controller
**Priority:** P0 (Critical)
**Description:** System shall orchestrate QA execution according to configuration.

**Acceptance Criteria:**
- AC1: Load configuration from `qa_setup.json`
- AC2: Execute blocking checks first (e.g., cls-version)
- AC3: Launch enabled families in configured order
- AC4: Support parallel family execution
- AC5: Aggregate results from all families

---

#### FR-105: Python Tool Invocation
**Priority:** P0 (Critical)
**Description:** System shall invoke Python detection/fix tools instead of LLM for deterministic operations.

**Acceptance Criteria:**
- AC1: Load Python tool from skill directory
- AC2: Pass content and metadata to tool
- AC3: Receive structured Issue list
- AC4: Handle tool errors gracefully

---

### 9.2 Coordination (FR-200 Series)

#### FR-201: Resource Locking
**Priority:** P1 (High)
**Description:** System shall provide mutex-style locks for shared resources.

**Acceptance Criteria:**
- AC1: Acquire exclusive lock on resource (file, skill, etc.)
- AC2: Release lock when done
- AC3: Detect stale locks (timeout-based)
- AC4: Support lock timeout parameter

**API:**
```python
coordinator.acquire_resource(resource: str, agent_id: str, timeout: int) -> bool
coordinator.release_resource(resource: str, agent_id: str) -> None
```

---

#### FR-202: Heartbeat Monitoring
**Priority:** P1 (High)
**Description:** System shall track agent health via heartbeat mechanism.

**Acceptance Criteria:**
- AC1: Agents send heartbeat with current task
- AC2: System detects stale agents (no heartbeat > threshold)
- AC3: Report stale agents for recovery

**API:**
```python
coordinator.update_heartbeat(agent_id: str, current_task: str) -> None
coordinator.check_stale_agents(timeout: int) -> List[dict]
```

---

#### FR-203: Shared Status Database
**Priority:** P1 (High)
**Description:** System shall maintain shared state in SQLite database.

**Tables:**
- `qa_status`: Skill execution status
- `qa_locks`: Resource locks
- `qa_heartbeat`: Agent heartbeats

**Location:** `{project}/.qa_coordination.db`

---

#### FR-204: Progress Tracking
**Priority:** P2 (Medium)
**Description:** System shall track and report QA progress.

**Acceptance Criteria:**
- AC1: Track skill start/complete times
- AC2: Track issues found per skill
- AC3: Calculate overall progress percentage
- AC4: Expose progress via API

---

### 9.3 Logging (FR-300 Series)

#### FR-301: Structured Logging
**Priority:** P1 (High)
**Description:** System shall log all QA events in structured format.

**Log Format:**
```
{timestamp} - {level} - [{agent}] {json_payload}
```

**Log Levels:** DEBUG, INFO, WARNING, ERROR

**Log Location:** `{project}/qa-logs/qa_{timestamp}.log`

---

#### FR-302: Event Types
**Priority:** P1 (High)
**Description:** System shall log the following event types:

| Event | Payload |
|-------|---------|
| SKILL_START | skill, agent_id |
| SKILL_COMPLETE | skill, issues_count, verdict |
| SKILL_ERROR | skill, error_message |
| PROGRESS | skill, progress_pct, status |
| LOCK_ACQUIRE | resource, agent_id |
| LOCK_RELEASE | resource, agent_id |
| HEARTBEAT | agent_id, task |
| WATCHDOG_ALERT | agent_id, last_seen |

---

#### FR-303: Watchdog Monitor
**Priority:** P2 (Medium)
**Description:** System shall monitor agent health and alert on issues.

**Acceptance Criteria:**
- AC1: Run monitoring loop in background thread
- AC2: Check for stale agents every N seconds (configurable)
- AC3: Log warning for stale agents
- AC4: Optionally trigger recovery action

---

### 9.4 Detection Tools (FR-400 Series)

#### FR-401: BiDi Detection Tool
**Priority:** P0 (Critical)
**Description:** Python tool implementing all 15 BiDi detection rules.

**Rules to Implement:**
| Rule | Name | Regex-Based |
|------|------|-------------|
| 1 | Cover Page Metadata | Yes |
| 2 | Table Cell Hebrew | Yes |
| 3 | Section Numbering | Yes |
| 4 | Reversed Text | Yes |
| 5 | Header/Footer Hebrew | Yes |
| 6 | Numbers Without LTR | Yes |
| 7 | English Without LTR | Yes |
| 8 | tcolorbox BiDi-Safe | Yes |
| 9 | Section Titles | Yes |
| 10 | Uppercase Acronyms | Yes |
| 11 | Decimal Numbers | Yes |
| 12 | Chapter Labels | Yes |
| 13 | fbox/parbox Mixed | Yes |
| 14 | Standalone Counter | Yes |
| 15 | Hebrew in English | Yes |

**Interface:**
```python
class BiDiDetector(DetectorInterface):
    def detect(content: str, file_path: str, offset: int = 0) -> List[Issue]
```

---

#### FR-402: Code Detection Tool
**Priority:** P0 (Critical)
**Description:** Python tool for code block detection.

**Phases to Implement:**
| Phase | Name | Regex-Based |
|-------|------|-------------|
| 2 | Background Overflow | Yes |
| 3 | Character Encoding | Yes |
| 4 | Language Direction | Yes |
| 5 | Hebrew Title | Yes |
| 6 | F-String Braces | Yes |

---

#### FR-403: Typeset Detection Tool
**Priority:** P1 (High)
**Description:** Python tool for LaTeX log parsing.

**Patterns to Detect:**
- Overfull/Underfull hbox
- Overfull/Underfull vbox
- Undefined references
- Undefined citations
- Float too large
- TikZ overflow risk

---

#### FR-404: Table Detection Tool
**Priority:** P1 (High)
**Description:** Python tool for table layout detection.

---

### 9.5 Fix Tools (FR-500 Series)

#### FR-501: BiDi Fix Tool
**Priority:** P1 (High)
**Description:** Python tool for BiDi text corrections.

**Fix Patterns:**
| Pattern | Find | Replace |
|---------|------|---------|
| Number wrap | `(\d+([.,]\d+)*)` in Hebrew | `\en{$1}` |
| English wrap | `([a-zA-Z]{2,})` in Hebrew | `\en{$1}` |
| Acronym wrap | `([A-Z]{2,5})` in Hebrew | `\en{$1}` |

---

#### FR-502: Code Fix Tool
**Priority:** P1 (High)
**Description:** Python tool for code block corrections.

---

### 9.6 Skill Management (FR-600 Series)

#### FR-601: insert_qa_skill - Create Mode
**Priority:** P0 (Critical)
**Description:** Create new QA skill from requirements.

**Inputs:**
- `--name`: Skill name
- `--family`: Parent family
- `--level`: Skill level (1 or 2)
- `--type`: detection | fix | validation
- `--description`: Brief description
- `--rules`: Comma-separated detection rules
- `--patterns`: Comma-separated fix patterns
- `--python`: true | false

**Outputs:**
- `skill.md`: Skill definition file
- `tool.py`: Python tool (if `--python=true`)
- `test_tool.py`: Unit tests
- Updated parent orchestrator
- Updated QA-CLAUDE.md

---

#### FR-602: insert_qa_skill - Split Mode
**Priority:** P1 (High)
**Description:** Extract Python code from existing skill.

**Inputs:**
- `--skill`: Existing skill name
- `--extract`: Capabilities to extract (comma-separated)

**Outputs:**
- `tool.py`: New Python tool
- Updated `skill.md` with tool reference
- `test_tool.py`: Unit tests

---

#### FR-603: Skill Validation
**Priority:** P1 (High)
**Description:** Validate skill structure and integration.

**Checks:**
- Skill file exists and has valid frontmatter
- Parent orchestrator references skill
- Python tool (if exists) implements interface
- Tests exist and pass

---

### 9.7 Testing (FR-700 Series)

#### FR-701: Base Test Class
**Priority:** P0 (Critical)
**Description:** Provide base class for all skill tests.

**Methods:**
```python
class QASkillTestBase:
    def load_fixture(name: str) -> str
    def assertIssueFound(issues: list, rule: str)
    def assertNoIssue(issues: list, rule: str)
    def assertIssueCount(issues: list, expected: int)
```

---

#### FR-702: Test Fixtures
**Priority:** P0 (Critical)
**Description:** Each skill shall have test fixtures.

**Required Fixtures:**
- `valid_document.tex`: Document with no issues
- `invalid_document.tex`: Document with known issues
- Additional edge case fixtures as needed

---

#### FR-703: Test Runner
**Priority:** P1 (High)
**Description:** Run all skill tests and report results.

**Features:**
- Discover all test files
- Run tests in parallel
- Generate JSON report
- Exit with appropriate code

---

#### FR-704: Orchestration Tests
**Priority:** P1 (High)
**Description:** Test full QA pipeline.

**Test Cases:**
- Full pipeline execution
- Parallel family execution
- Batch processing
- Error handling

---

### 9.8 Configuration (FR-800 Series)

#### FR-801: qa_setup.json
**Priority:** P0 (Critical)
**Description:** Central configuration file for QA system.

**Schema:** See Section 11

---

#### FR-802: Configuration Loading
**Priority:** P0 (Critical)
**Description:** Load and validate configuration.

**Acceptance Criteria:**
- AC1: Load from project root or default location
- AC2: Validate against JSON schema
- AC3: Apply defaults for missing values
- AC4: Support environment variable overrides

---

### 9.9 Reporting (FR-900 Series)

#### FR-901: Execution Report
**Priority:** P1 (High)
**Description:** Generate report after QA run.

**Formats:** Markdown, JSON, HTML

**Content:**
- Execution summary (time, families, issues)
- Per-family results
- Issue details
- Recommendations

---

#### FR-902: Progress Report
**Priority:** P2 (Medium)
**Description:** Generate real-time progress report.

---

## 10. Non-Functional Requirements

### 10.1 Performance (NFR-100)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-101 | Token usage reduction | 60-70% vs current |
| NFR-102 | Processing speed | 1000 lines/second (Python tools) |
| NFR-103 | Memory usage | <500MB for 50,000 line document |
| NFR-104 | Startup time | <2 seconds |

### 10.2 Reliability (NFR-200)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-201 | Detection consistency | 100% for Python tools |
| NFR-202 | Error recovery | Continue on non-critical errors |
| NFR-203 | Data integrity | Never corrupt source files |
| NFR-204 | Uptime | N/A (not a service) |

### 10.3 Usability (NFR-300)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-301 | Skill creation time | <10 minutes with insert_qa_skill |
| NFR-302 | Error messages | Clear, actionable messages |
| NFR-303 | Documentation | README + API docs for all components |

### 10.4 Maintainability (NFR-400)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-401 | Test coverage | 90%+ for Python tools |
| NFR-402 | Code style | PEP 8 compliant |
| NFR-403 | Documentation | Docstrings for all public functions |
| NFR-404 | Module size | <150 lines per Python file |

### 10.5 Security (NFR-500)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-501 | File access | Only within project directory |
| NFR-502 | No external calls | Python tools work offline |
| NFR-503 | Input validation | Sanitize all file paths |

---

## 11. Technical Architecture

### 11.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                 │
│                    (Claude CLI / /full-pdf-qa command)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          QA ORCHESTRATION LAYER                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   qa-super      │  │ qa_setup.json   │  │  QA Controller  │         │
│  │   (Skill)       │  │ (Configuration) │  │  (Python)       │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           └────────────────────┴────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FAMILY ORCHESTRATORS (L1)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ qa-BiDi  │ │ qa-code  │ │ qa-table │ │qa-typeset│ │ qa-infra │      │
│  │ (Skill)  │ │ (Skill)  │ │ (Skill)  │ │ (Skill)  │ │ (Skill)  │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
└───────┼────────────┼────────────┼────────────┼────────────┼─────────────┘
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          PYTHON TOOLS LAYER (L2)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │BiDiDetector  │ │CodeDetector  │ │TableDetector │ │TypesetDetect │   │
│  │   (Python)   │ │   (Python)   │ │   (Python)   │ │   (Python)   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                    │
│  │  BiDiFixer   │ │  CodeFixer   │ │  TableFixer  │                    │
│  │   (Python)   │ │   (Python)   │ │   (Python)   │                    │
│  └──────────────┘ └──────────────┘ └──────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE LAYER                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   Batch     │ │ Coordinator │ │   Logger    │ │  Watchdog   │       │
│  │ Processor   │ │  (SQLite)   │ │             │ │  Monitor    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            FILE SYSTEM                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ .tex files  │ │ .log files  │ │ .db (state) │ │  qa-logs/   │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Directory Structure

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
│   │       ├── valid_document.tex
│   │       └── invalid_document.tex
│   │
│   ├── [other skill families...]
│   │
│   ├── insert_qa_skill/
│   │   ├── skill.md
│   │   └── templates/
│   │       ├── skill_template.md
│   │       ├── detector_template.py
│   │       ├── fixer_template.py
│   │       └── test_template.py
│   │
│   └── qa-test-runner/
│       ├── run_all_tests.py
│       ├── base_test.py
│       ├── test_orchestration.py
│       └── conftest.py
│
├── qa_engine/
│   ├── __init__.py
│   ├── controller.py
│   ├── document_analyzer.py
│   ├── batch_processor.py
│   ├── coordination.py
│   ├── logging_system.py
│   ├── skill_discovery.py
│   └── interfaces.py
│
└── commands/
    ├── full-pdf-qa.md
    └── fix-qa-mechanism.md
```

### 11.3 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.10+ |
| Database | SQLite | 3.x |
| CLI Framework | Claude CLI | Latest |
| Testing | pytest | 7.x+ |
| Logging | Python logging | stdlib |
| Concurrency | concurrent.futures | stdlib |

---

## 12. User Stories

### 12.1 Document Author Stories

#### US-101: Run QA on Document
**As a** document author
**I want to** run QA on my LaTeX document
**So that** I can find and fix BiDi, code, and formatting issues

**Acceptance Criteria:**
- Given I have a LaTeX project
- When I run `/full-pdf-qa {project_path}`
- Then all enabled QA families execute
- And I receive a report with all issues found

---

#### US-102: Configure QA Checks
**As a** document author
**I want to** enable/disable specific QA families
**So that** I only run checks relevant to my document

**Acceptance Criteria:**
- Given I have a `qa_setup.json` file
- When I set `enabled_families` to specific families
- Then only those families run during QA

---

#### US-103: Process Large Document
**As a** document author
**I want to** run QA on a large document (10,000+ lines)
**So that** I can find issues without context limit errors

**Acceptance Criteria:**
- Given I have a large LaTeX project
- When I run QA
- Then the system automatically chunks the document
- And processes chunks in parallel
- And merges results into single report

---

### 12.2 Skill Developer Stories

#### US-201: Create New Detection Skill
**As a** skill developer
**I want to** create a new detection skill
**So that** I can add new QA capabilities

**Acceptance Criteria:**
- Given I invoke `insert_qa_skill --mode=create`
- When I provide skill name, family, and rules
- Then skill.md is created
- And tool.py is generated (if python=true)
- And test_tool.py is generated
- And parent orchestrator is updated

---

#### US-202: Add Python Tool to Existing Skill
**As a** skill developer
**I want to** extract Python code from an existing skill
**So that** I can improve performance and consistency

**Acceptance Criteria:**
- Given I invoke `insert_qa_skill --mode=split`
- When I specify skill and capabilities to extract
- Then tool.py is created with extracted logic
- And skill.md is updated to reference tool
- And tests are generated

---

#### US-203: Run Skill Tests
**As a** skill developer
**I want to** run tests for all skills
**So that** I can verify they work correctly

**Acceptance Criteria:**
- Given I run `python run_all_tests.py`
- When tests execute
- Then I see pass/fail for each skill
- And a JSON report is generated

---

### 12.3 Administrator Stories

#### US-301: Monitor QA Progress
**As an** administrator
**I want to** monitor QA progress in real-time
**So that** I can identify issues early

**Acceptance Criteria:**
- Given QA is running
- When I check the coordination database
- Then I see current status of all skills
- And agent heartbeats

---

#### US-302: Configure Logging
**As an** administrator
**I want to** configure logging level and output
**So that** I can debug issues when needed

**Acceptance Criteria:**
- Given I set logging config in qa_setup.json
- When QA runs
- Then logs are written at specified level
- To specified outputs (file/console)

---

## 13. API Specifications

### 13.1 Python Tool Interface

```python
# qa_engine/interfaces.py

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
        """Detect issues in content."""
        pass

    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        pass

class FixerInterface(ABC):
    """Interface for fix tools."""

    @abstractmethod
    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes to content."""
        pass

    @abstractmethod
    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return dict of pattern_name -> {find, replace, description}."""
        pass
```

### 13.2 Coordinator Interface

```python
# qa_engine/coordination.py

class QACoordinator:
    """Interface for agent coordination."""

    def __init__(self, project_path: str):
        """Initialize coordinator with project path."""
        pass

    def acquire_resource(self, resource: str, agent_id: str, timeout: int = 30) -> bool:
        """Acquire exclusive lock on resource. Returns True if acquired."""
        pass

    def release_resource(self, resource: str, agent_id: str) -> None:
        """Release lock on resource."""
        pass

    def update_heartbeat(self, agent_id: str, current_task: str) -> None:
        """Update agent heartbeat."""
        pass

    def check_stale_agents(self, timeout: int = 60) -> List[Dict]:
        """Find agents without recent heartbeat."""
        pass

    def update_skill_status(self, skill: str, status: str, issues: int, verdict: str) -> None:
        """Update skill execution status."""
        pass

    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all skills."""
        pass
```

### 13.3 Controller Interface

```python
# qa_engine/controller.py

class QAController:
    """Main QA orchestration controller."""

    def __init__(self, project_path: str, config_path: str = None):
        """Initialize with project and optional config path."""
        pass

    def run_full_qa(self) -> Dict:
        """Run complete QA pipeline. Returns results dict."""
        pass

    def run_family(self, family: str) -> Dict:
        """Run single family. Returns family results."""
        pass

    def run_skill(self, skill: str, content: str, file_path: str) -> List[Issue]:
        """Run single skill on content. Returns issues."""
        pass

    def get_progress(self) -> Dict:
        """Get current progress."""
        pass
```

---

## 14. Data Models

### 14.1 Issue Model

```python
@dataclass
class Issue:
    rule: str           # Rule identifier (e.g., "number-not-ltr")
    file: str           # Source file path
    line: int           # Line number (1-indexed)
    content: str        # Offending content
    severity: Severity  # INFO, WARNING, CRITICAL
    fix: str = None     # Suggested fix
    context: dict = None  # Additional context
```

### 14.2 Skill Metadata Model

```python
@dataclass
class SkillMetadata:
    name: str           # Skill name
    description: str    # Brief description
    version: str        # Semantic version
    level: int          # 0, 1, or 2
    family: str         # Parent family (for L2)
    type: str           # detection, fix, validation
    tags: List[str]     # Search tags
    has_python_tool: bool  # Whether tool.py exists
```

### 14.3 QA Status Model

```python
@dataclass
class QAStatus:
    skill_name: str     # Skill identifier
    status: str         # PENDING, RUNNING, DONE, ERROR
    started_at: datetime
    completed_at: datetime
    issues_count: int
    verdict: str        # PASS, WARNING, FAIL
    agent_id: str       # Agent that executed
```

### 14.4 Database Schema

```sql
-- qa_status table
CREATE TABLE qa_status (
    id INTEGER PRIMARY KEY,
    skill_name TEXT UNIQUE,
    status TEXT,
    started_at TEXT,
    completed_at TEXT,
    issues_count INTEGER,
    verdict TEXT,
    agent_id TEXT
);

-- qa_locks table
CREATE TABLE qa_locks (
    resource TEXT PRIMARY KEY,
    locked_by TEXT,
    locked_at TEXT
);

-- qa_heartbeat table
CREATE TABLE qa_heartbeat (
    agent_id TEXT PRIMARY KEY,
    last_heartbeat TEXT,
    current_task TEXT
);
```

---

## 15. Configuration Schema

### 15.1 qa_setup.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "QA Setup Configuration",
  "type": "object",
  "properties": {
    "enabled_families": {
      "type": "array",
      "items": {"type": "string"},
      "default": ["BiDi", "code", "typeset"]
    },
    "execution_order": {
      "type": "array",
      "items": {"type": "string"},
      "default": ["cls-version", "BiDi", "code", "table", "typeset"]
    },
    "parallel_families": {
      "type": "boolean",
      "default": true
    },
    "blocking_checks": {
      "type": "array",
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
        "level": {"type": "string", "default": "INFO"},
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
        "format": {"type": "string", "default": "markdown"},
        "include_details": {"type": "boolean", "default": true}
      }
    },
    "skill_overrides": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "enabled": {"type": "boolean"},
          "priority": {"type": "string"},
          "skip_rules": {"type": "array"}
        }
      }
    }
  }
}
```

---

## 16. Success Metrics

### 16.1 Key Performance Indicators (KPIs)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Token usage per QA run | 50,000 | 15,000 | Count from API |
| Detection consistency | 85% | 100% | Same input = same output |
| Test coverage | 0% | 90% | pytest-cov |
| Skill creation time | 2 hours | 10 min | Manual timing |
| Large doc support | 0 lines | 50,000+ | Test with real docs |
| False positive rate | Unknown | <5% | Manual review |
| False negative rate | Unknown | <1% | Known issue testing |

### 16.2 Acceptance Thresholds

| Phase | Metric | Threshold |
|-------|--------|-----------|
| Phase 1 | Core engine functional | All FR-100 pass |
| Phase 2 | Token reduction | 50%+ reduction |
| Phase 3 | Test coverage | 80%+ |
| Phase 4 | insert_qa_skill works | Creates valid skill |
| Phase 5 | Full validation | Real project QA successful |

---

## 17. Dependencies

### 17.1 External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| Claude CLI | Latest | Skill execution |
| pytest | 7.x+ | Testing |
| SQLite | 3.x | State storage |

### 17.2 Internal Dependencies

| Component | Depends On |
|-----------|------------|
| QA Controller | Document Analyzer, Batch Processor, Coordinator |
| Batch Processor | Coordinator, Logger |
| Python Tools | Interfaces |
| Test Runner | All Python Tools |
| insert_qa_skill | Templates, QA-CLAUDE.md |

### 17.3 Skill Dependencies

| Skill Level | Depends On |
|-------------|------------|
| L2 Detection | Parent L1 orchestrator |
| L2 Fix | L2 Detection results |
| L1 Orchestrator | L0 qa-super |
| L0 qa-super | qa_setup.json |

---

## 18. Constraints and Assumptions

### 14.1 Constraints

| ID | Constraint | Impact |
|----|------------|--------|
| C1 | Must run locally (no cloud) | Cannot use cloud services |
| C2 | Windows primary platform | Some Unix tools unavailable |
| C3 | Claude CLI as interface | Cannot build standalone app |
| C4 | Python 3.10+ required | Older systems not supported |
| C5 | File size <150 lines | Requires modular design |

### 14.2 Assumptions

| ID | Assumption | Risk if Invalid |
|----|------------|-----------------|
| A1 | Users have Python 3.10+ | Need fallback or installer |
| A2 | Projects follow standard structure | Need flexible discovery |
| A3 | Hebrew-English only | Need i18n for other RTL |
| A4 | Single user per project | Need multi-user coordination |
| A5 | Regex sufficient for detection | May need AST parsing |

---

## 19. Risks and Mitigations

### 15.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Regex patterns miss edge cases | Medium | High | Comprehensive test fixtures |
| Batch boundary issues | Medium | Medium | Smart chunking at environment boundaries |
| SQLite locking under load | Low | Medium | WAL mode, connection pooling |
| Python tool import errors | Medium | High | Graceful fallback to skill-only |

### 15.2 Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | Medium | Strict PRD adherence |
| Integration complexity | Medium | High | Incremental phases |
| Test coverage gaps | Medium | High | TDD approach |
| Documentation lag | High | Low | Doc-as-code |

---

## 20. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Deliverables:**
- `qa_engine/` Python package structure
- `document_analyzer.py` - Document size analysis
- `coordination.py` - SQLite-based coordination
- `interfaces.py` - Tool interfaces
- `qa_setup.json` schema and loader

**Exit Criteria:**
- Document analyzer returns correct metrics
- Coordination locks/heartbeats work
- Config loads and validates

---

### Phase 2: Python Tool Migration (Week 3-4)

**Deliverables:**
- `BiDiDetector` - All 15 rules in Python
- `CodeDetector` - All phases in Python
- `TypesetDetector` - Log parsing in Python
- Unit tests for all tools

**Exit Criteria:**
- Python tools match LLM detection accuracy
- 60%+ token reduction measured
- 80%+ test coverage

---

### Phase 3: Orchestration Engine (Week 5-6)

**Deliverables:**
- `batch_processor.py` - Chunked parallel processing
- `controller.py` - Main orchestration
- `logging_system.py` - Structured logging
- Watchdog monitoring

**Exit Criteria:**
- Large documents process successfully
- Parallel execution works
- Logs capture all events

---

### Phase 4: insert_qa_skill (Week 7)

**Deliverables:**
- `insert_qa_skill/skill.md` - Full skill definition
- Templates for skill, tool, test
- Create mode implementation
- Split mode implementation

**Exit Criteria:**
- Create mode generates valid skill
- Split mode extracts Python correctly
- Generated tests pass

---

### Phase 5: Validation & Polish (Week 8)

**Deliverables:**
- Full test suite execution
- Real project validation
- Documentation
- Performance benchmarks

**Exit Criteria:**
- All KPIs met
- Real projects QA successfully
- Documentation complete

---

## 21. Acceptance Criteria

### 17.1 Overall System Acceptance

- [ ] All functional requirements (FR-*) implemented
- [ ] All non-functional requirements (NFR-*) met
- [ ] Token usage reduced by 60%+
- [ ] Detection consistency at 100% for Python tools
- [ ] Test coverage at 90%+
- [ ] Documentation complete

### 17.2 Component Acceptance

#### qa_engine Package
- [ ] Document analyzer correctly measures documents
- [ ] Batch processor handles 50,000+ lines
- [ ] Coordinator manages locks and heartbeats
- [ ] Logger captures all events
- [ ] Controller orchestrates full pipeline

#### Python Tools
- [ ] BiDiDetector implements all 15 rules
- [ ] CodeDetector implements all 6 phases
- [ ] TypesetDetector parses all log patterns
- [ ] All tools have 90%+ test coverage

#### insert_qa_skill
- [ ] Create mode generates valid skill structure
- [ ] Split mode extracts capabilities correctly
- [ ] Generated tests pass
- [ ] Integration updates work

---

## 22. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| BiDi | Bidirectional text (Hebrew RTL + English LTR) |
| CLS | LaTeX document class file (.cls) |
| L0/L1/L2 | Skill hierarchy levels (Super/Family/Skill) |
| Skill | Claude CLI skill (markdown-based playbook) |
| Tool | Python implementation of deterministic logic |
| Chunk | Portion of document for batch processing |
| Heartbeat | Periodic status update from agent |
| Watchdog | Monitor that detects stale agents |

### Appendix B: References

- [Architecture Research Report](./QA-CLAUDE-MECHANISM-ARCHITECTURE-REPORT.md)
- [QA-CLAUDE.md](~/.claude/skills/qa-orchestration/QA-CLAUDE.md)
- [Claude CLI Documentation](https://docs.anthropic.com/claude-code)

### Appendix C: Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-15 | Claude Code | Initial PRD |

---

*End of PRD*
