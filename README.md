# QA Engine - Hebrew-English LaTeX Quality Assurance System

## Abstract

**QA Engine** is a modular, Python-based quality assurance system designed for Hebrew-English LaTeX documents. It provides automated detection and correction of bidirectional text issues, code formatting problems, typesetting warnings, bibliography errors, and image management in RTL (Right-to-Left) academic documents.

The system implements a **three-level skill hierarchy**:
- **Level 0 (Meta)**: Super orchestrators coordinating all families
- **Level 1 (Family)**: Family orchestrators managing related skills
- **Level 2 (Worker)**: Specialized detectors and fixers

Key features:
- **Deterministic Python Tools**: Automated detection and fixing without LLM dependency
- **Hybrid Workflow**: Python handles deterministic patterns, LLM handles complex decisions
- **Thread-Safe Coordination**: Resource locking and heartbeat monitoring for multi-agent scenarios
- **Batch Processing**: Smart chunking for large documents with parallel execution
- **Pipeline Management**: Configurable execution order with parallel stage support

---

## Table of Contents

1. [Installation](#installation)
2. [Project Architecture](#project-architecture)
3. [Class Architecture](#class-architecture)
4. [Orchestration Structure](#orchestration-structure)
5. [Pipeline Operation](#pipeline-operation)
6. [Configuration Files](#configuration-files)
7. [Multithreading and Lock Mechanism](#multithreading-and-lock-mechanism)
8. [Watchdog and Heartbeat Monitor](#watchdog-and-heartbeat-monitor)
9. [Logging System](#logging-system)
10. [Dependency Injection](#dependency-injection)
11. [Batch Processing](#batch-processing)
12. [Usage](#usage)
13. [Unit Testing](#unit-testing)
14. [Skill Reference](#skill-reference)
15. [How to Add New Skill](#how-to-add-new-skill)
16. [How to Add New Tool](#how-to-add-new-tool)
17. [How to Add New Resource](#how-to-add-new-resource)
18. [Migration: Local to Global Skills](#migration-local-to-global-skills)

---

## Installation

### Prerequisites

- Python 3.9+ (Python 3.13 recommended)
- Windows 11 or Linux
- UV package manager (recommended) or pip

### Option 1: Direct UV Usage (Recommended - No Manual venv)

UV can run Python scripts directly without manually creating a virtual environment:

```powershell
# Install UV (Windows PowerShell) - one-time setup
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Navigate to project directory
cd C:\path\to\skill-python-base

# Run any Python script directly (UV auto-manages venv)
uv run python -c "from qa_engine import api; print('Ready!')"

# Run tests directly
uv run pytest tests/ -v

# Run the QA CLI
uv run python -m qa_engine.cli.main run --project ./book

# Sync dependencies (creates .venv if needed)
uv sync
```

UV automatically creates and manages `.venv/` when you use `uv run` or `uv sync`.

### Option 2: Using UV with Manual venv

If you prefer explicit virtual environment control:

```powershell
# Install UV (Windows PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Navigate to project directory
cd C:\path\to\skill-python-base

# Create virtual environment with UV
uv venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

### Option 3: Using Python venv (Standard)

```powershell
# Navigate to project directory
cd C:\path\to\skill-python-base

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
# source .venv/bin/activate

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Verify Installation

```powershell
# Run tests to verify installation
python -m pytest tests/ -v

# Run a simple import test
python -c "from qa_engine import api; print('Installation successful!')"
```

---

## Project Architecture

**CLS Version:** v6.3.4 | [BC Mechanism](docs/BC-MECHANISM.md) | [UV Environment](docs/UV-ENVIRONMENT.md) | [When to Use](docs/WHEN-TO-USE.md) | [Book Creation Guide](docs/How-to-create-Academic-Book-with-this-project.md)

```
skill-python-base/
├── .claude/                    # Claude CLI configuration
│   ├── skills/                 # 69 skills (QA + BC mechanisms)
│   │   ├── qa-super/           # Level 0 QA orchestrator
│   │   ├── bc-super/           # Level 0 BC orchestrator
│   │   ├── qa-BiDi/            # Level 1 BiDi family
│   │   ├── bc-architect/       # Level 1 BC architect
│   │   └── ...                 # Other QA/BC skills
│   ├── commands/               # Slash commands
│   └── tasks/                  # Task management
│
├── docs/                       # Documentation
│   ├── architecture/           # Architecture reports (QA, BC)
│   ├── planning/               # PRDs, implementation plans
│   └── reports/                # Status and verification reports
│
├── src/qa_engine/              # Main Python package
│   ├── __init__.py
│   ├── api.py                  # Public API entry point
│   │
│   ├── domain/                 # Domain layer (core business logic)
│   │   ├── interfaces.py       # DetectorInterface, FixerInterface, CreatorInterface
│   │   ├── models/             # Data models
│   │   │   ├── base.py         # BaseEntity abstract class
│   │   │   ├── skill_model.py  # Skill, OrchestratorSkill, DetectorSkill, FixerSkill
│   │   │   ├── tool_model.py   # Tool, DetectorTool, FixerTool
│   │   │   ├── resource_model.py
│   │   │   ├── issue.py        # Issue dataclass
│   │   │   └── status.py       # QAStatus enum
│   │   └── services/           # Domain services
│   │       ├── document_analyzer.py  # Analyzes document size/complexity
│   │       └── skill_registry.py     # Skill registration
│   │
│   ├── infrastructure/         # Infrastructure layer (implementations)
│   │   ├── detection/          # Detector implementations
│   │   │   ├── bidi_detector.py
│   │   │   ├── code_detector.py
│   │   │   ├── typeset_detector.py
│   │   │   ├── image_detector.py
│   │   │   ├── table_detector.py
│   │   │   ├── bib_detector.py
│   │   │   └── *_rules.py      # Rule definitions
│   │   │
│   │   ├── fixing/             # Fixer implementations
│   │   │   ├── bidi_fixer.py
│   │   │   ├── code_fixer.py
│   │   │   ├── float_fixer.py
│   │   │   ├── image_fixer.py
│   │   │   └── encoding_fixer.py
│   │   │
│   │   ├── creation/           # Creator implementations
│   │   │   └── image_creator.py
│   │   │
│   │   ├── coordination/       # Multi-agent coordination
│   │   │   ├── coordinator.py  # Resource locking via SQLite
│   │   │   ├── heartbeat.py    # Watchdog monitor
│   │   │   └── db_manager.py   # SQLite database manager
│   │   │
│   │   ├── processing/         # Batch processing
│   │   │   ├── batch_processor.py
│   │   │   └── chunk.py
│   │   │
│   │   ├── backup/             # Project backup utilities
│   │   │   └── project_backup.py
│   │   │
│   │   ├── reporting/          # Report generation
│   │   │   ├── report_generator.py
│   │   │   └── formatters.py
│   │   │
│   │   └── *_orchestrator.py   # Family orchestrators
│   │       ├── bidi_orchestrator.py
│   │       ├── image_orchestrator.py
│   │       ├── typeset_orchestrator.py
│   │       └── super_orchestrator.py
│   │
│   ├── typeset/                # Typeset-specific modules
│   │   ├── detection/          # Log parsing, TikZ, itemsep
│   │   └── fixing/             # Hbox, vbox, mdframed fixers
│   │
│   ├── shared/                 # Shared utilities
│   │   ├── config.py           # ConfigManager singleton
│   │   ├── logging.py          # PrintManager, JsonLogger
│   │   ├── threading.py        # ResourceManager (locks)
│   │   ├── di.py               # DIContainer
│   │   └── version.py
│   │
│   ├── management/             # Entity management (CRUD)
│   │   ├── base_manager.py     # Generic CRUD operations
│   │   ├── skill_manager.py
│   │   ├── tool_manager.py
│   │   ├── resource_manager.py
│   │   └── pipeline_manager.py
│   │
│   ├── parsers/                # File parsers
│   │   ├── skill_parser.py     # Parse skill.md YAML
│   │   ├── tool_parser.py      # Parse tool.py
│   │   └── config_parser.py
│   │
│   ├── serializers/            # File serializers
│   │   ├── skill_serializer.py
│   │   ├── tool_serializer.py
│   │   └── config_serializer.py
│   │
│   ├── sdk/                    # SDK for skill development
│   │   ├── controller.py       # QAController
│   │   ├── executor.py         # QAExecutor
│   │   ├── skill_creator.py    # Create new skills
│   │   └── skill_templates.py
│   │
│   ├── cli/                    # Command-line interface
│   │   ├── main.py
│   │   ├── skill_commands.py
│   │   ├── tool_commands.py
│   │   └── pipeline_commands.py
│   │
│   └── meta/                   # Meta-skills (skill improvement)
│       ├── failure_classifier.py
│       └── improvement_tracker.py
│
├── config/                     # Configuration files
│   ├── qa_setup.json           # Main QA configuration
│   ├── logging_config.json     # Logging configuration
│   └── schemas/                # JSON schemas
│       ├── skill_schema.json
│       ├── tool_schema.json
│       ├── resource_schema.json
│       └── pipeline_schema.json
│
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── arch/                   # Architecture tests
│   └── comparison/             # Comparison tests (LLM vs Python)
│
├── pyproject.toml              # Project configuration
├── pytest.ini                  # Pytest configuration
└── requirements.txt            # Dependencies
```

---

## Class Architecture

### Core Interfaces (`domain/interfaces.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DetectorInterface (ABC)                       │
├─────────────────────────────────────────────────────────────────┤
│ + detect(content, file_path, offset) -> List[Issue]             │
│ + get_rules() -> Dict[str, str]                                 │
│                                                                 │
│ Constraints:                                                    │
│ - Read-only: MUST NOT modify content                            │
│ - Stateless: No side effects                                    │
│ - Deterministic: Same input = same output                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     FixerInterface (ABC)                         │
├─────────────────────────────────────────────────────────────────┤
│ + fix(content, issues) -> str                                   │
│ + get_patterns() -> Dict[str, Dict]                             │
│                                                                 │
│ Constraints:                                                    │
│ - Issue-driven: Only fix provided issues                        │
│ - No detection: NEVER search for new issues                     │
│ - Targeted: Only modify what's needed                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CreatorInterface (ABC)                        │
├─────────────────────────────────────────────────────────────────┤
│ + create(path, **options) -> bool                               │
│ + create_from_issues(issues) -> Dict[str, bool]                 │
│ + get_supported_formats() -> List[str]                          │
│                                                                 │
│ Constraints:                                                    │
│ - File creation only                                            │
│ - Idempotent: Creating twice should not error                   │
└─────────────────────────────────────────────────────────────────┘
```

### Entity Hierarchy (`domain/models/`)

```
BaseEntity (ABC)
├── id, name, description, version, enabled, metadata
├── validate() -> List[str]
├── to_dict() -> Dict
└── from_dict(data) -> BaseEntity

    ├── Skill
    │   ├── level: SkillLevel (L0_META, L1_FAMILY, L2_WORKER)
    │   ├── skill_type: SkillType (ORCHESTRATOR, DETECTION, FIX, VALIDATION)
    │   ├── family, parent, children, tags
    │   ├── rules: Dict[str, RuleConfig]
    │   │
    │   ├── OrchestratorSkill (L0/L1)
    │   │   └── managed_families, coordination_mode
    │   │
    │   ├── DetectorSkill (L2)
    │   │   └── detection_rules, has_python_tool
    │   │
    │   └── FixerSkill (L2)
    │       └── fix_patterns, has_python_tool
    │
    ├── Tool
    │   ├── tool_type, handler_path, parameters
    │   │
    │   ├── DetectorTool
    │   │   └── rules: List[str]
    │   │
    │   └── FixerTool
    │       └── patterns: List[str]
    │
    └── Resource
        ├── resource_type, file_path, format
        │
        ├── ConfigResource
        ├── RulesResource
        └── PatternsResource
```

### Manager Pattern (`management/`)

```
BaseManager[T] (Generic, ABC)
├── _storage_path: Path
├── _cache: Dict[str, T]
│
├── CRUD Operations:
│   ├── create(entity) -> T
│   ├── read(entity_id) -> Optional[T]
│   ├── update(entity_id, updates) -> T
│   └── delete(entity_id) -> bool
│
├── Bulk Operations:
│   ├── list_all() -> List[T]
│   └── find(**criteria) -> List[T]
│
├── State Management:
│   ├── enable(entity_id) -> bool
│   ├── disable(entity_id) -> bool
│   └── duplicate(entity_id, new_id) -> T
│
└── Persistence:
    ├── load_all() -> None
    ├── save_all() -> None
    └── refresh(entity_id) -> Optional[T]

    ├── SkillManager (skills storage)
    ├── ToolManager (tools storage)
    ├── ResourceManager (resources storage)
    └── PipelineManager (pipeline stages)
```

---

## Orchestration Structure

### Three-Level Hierarchy

```
Level 0 (Meta/Super)
└── qa-super (SuperOrchestrator)
    │
    ├── Level 1 (Family Orchestrators)
    │   ├── qa-BiDi (BiDiOrchestrator)
    │   │   ├── qa-BiDi-detect
    │   │   └── qa-BiDi-fix-text
    │   │
    │   ├── qa-img (ImageOrchestrator)
    │   │   ├── qa-img-detect
    │   │   ├── qa-img-fix-paths
    │   │   ├── qa-img-fix-missing
    │   │   └── qa-img-validate
    │   │
    │   ├── qa-typeset (TypesetOrchestrator)
    │   │   ├── qa-typeset-detect
    │   │   ├── qa-typeset-fix-hbox
    │   │   ├── qa-typeset-fix-vbox
    │   │   └── qa-typeset-fix-float
    │   │
    │   ├── qa-code
    │   │   ├── qa-code-detect
    │   │   ├── qa-code-fix-background
    │   │   └── qa-code-fix-encoding
    │   │
    │   ├── qa-table
    │   │   ├── qa-table-detect
    │   │   └── qa-table-fix-*
    │   │
    │   └── qa-bib
    │       ├── qa-bib-detect
    │       └── qa-bib-fix
    │
    └── Level 2 (Worker Skills)
        └── Individual detector/fixer skills
```

### Orchestrator Workflow

```python
# SuperOrchestrator (Level 0)
class SuperOrchestrator:
    def run(self, content, file_path, families, apply_fixes):
        # 1. Initialize
        result = SuperOrchestratorResult()

        # 2. Analyze document
        result.document_metrics = self.analyzer.analyze(self.project_path)

        # 3. Delegate to families (parallel or sequential)
        for family in enabled_families:
            family_result = self._run_family(family, content, file_path, apply_fixes)
            result.family_results[family] = family_result

        # 4. Aggregate results
        return result

# Family Orchestrator (Level 1) - Example: BiDiOrchestrator
class BiDiOrchestrator:
    def run(self, content, file_path, apply_fixes):
        # Phase 1: Detection
        detect_result = self.detector.detect(content, file_path)

        # Phase 2: Fixing (if enabled)
        if apply_fixes and detect_result.issues:
            fix_result = self.fixer.fix(content, detect_result.issues)

        return BiDiOrchestratorResult(detect_result, fix_result)
```

---

## Pipeline Operation

### Pipeline Manager

The `PipelineManager` controls execution order and parallelization of skills.

```python
from qa_engine.management import PipelineManager

# Initialize
pipeline = PipelineManager(config_path, skill_manager)

# Load existing pipeline
pipeline.load_pipeline()

# Insert skill at automatic position (based on skill_type)
pipeline.insert_skill("qa-BiDi-detect")

# Insert at specific position
pipeline.insert_skill("qa-custom-fix", position=5)

# Move skill to new position
pipeline.move_skill("qa-BiDi-detect", new_position=0)

# Set skills to run in parallel
pipeline.set_parallel(["qa-BiDi-detect", "qa-code-detect", "qa-img-detect"])

# Enable/disable stages
pipeline.disable_stage("qa-table-detect")
pipeline.enable_stage("qa-table-detect")

# Get execution order
for stage in pipeline.get_enabled_stages():
    print(f"{stage.order}: {stage.skill_id} (parallel with: {stage.parallel_with})")

# Save pipeline
pipeline.save_pipeline()
```

### Pipeline Stage Configuration

```python
@dataclass
class PipelineStage:
    skill_id: str           # Skill to execute
    order: int              # Execution order (0-based)
    enabled: bool = True    # Whether stage is active
    parallel_with: List[str] = []  # Skills to run in parallel
```

### Implicit Type Ordering

Skills are automatically ordered by type:

| Order | Type        | Example                |
|-------|-------------|------------------------|
| 0     | ORCHESTRATOR| qa-super, qa-BiDi      |
| 1     | DETECTION   | qa-BiDi-detect         |
| 2     | FIX         | qa-BiDi-fix-text       |
| 3     | VALIDATION  | qa-img-validate        |

---

## Configuration Files

### Main Configuration (`config/qa_setup.json`)

```json
{
  "version": "1.1.0",
  "enabled_families": ["BiDi", "code", "table", "bib", "img", "typeset"],
  "parallel_families": true,
  "auto_fix": true,

  "batch_processing": {
    "enabled": true,
    "batch_size": 50,
    "chunk_lines": 1000,
    "max_workers": 4
  },

  "coordination": {
    "heartbeat_interval": 30,
    "stale_timeout": 120,
    "lock_timeout": 60
  },

  "logging": {
    "level": "INFO",
    "json_format": true,
    "log_dir": "qa-logs"
  },

  "families": {
    "BiDi": {
      "enabled": true,
      "detectors": ["qa-BiDi-detect"],
      "fixers": ["qa-BiDi-fix-text"],
      "rules": {
        "bidi-numbers": {"enabled": true, "auto_fix": true},
        "bidi-english": {"enabled": true, "auto_fix": true}
      }
    }
  },

  "global_workflow": {
    "phases": {
      "pre_compilation": {
        "execution": "parallel",
        "tools": ["ImageDetector", "BiDiDetector"],
        "skills": ["qa-img-detect", "qa-BiDi-detect"]
      },
      "compilation": {
        "execution": "sequential",
        "command": "lualatex"
      },
      "post_compilation": {
        "execution": "parallel",
        "tools": ["TypesetDetector"],
        "requires": ["compilation"]
      }
    },
    "order": ["pre_compilation", "compilation", "post_compilation"]
  }
}
```

### Configuration Parameters Reference

| Section | Parameter | Description | Default |
|---------|-----------|-------------|---------|
| `batch_processing.enabled` | Enable batch processing | Whether to use chunking | `true` |
| `batch_processing.batch_size` | Files per batch | Number of files to process together | `50` |
| `batch_processing.chunk_lines` | Lines per chunk | Maximum lines per chunk | `1000` |
| `batch_processing.max_workers` | Thread pool size | Parallel threads for chunking | `4` |
| `coordination.heartbeat_interval` | Heartbeat frequency | Seconds between heartbeats | `30` |
| `coordination.stale_timeout` | Stale threshold | Seconds without heartbeat = stale | `120` |
| `coordination.lock_timeout` | Lock wait time | Maximum seconds to wait for lock | `60` |
| `logging.level` | Log level | DEBUG, INFO, WARNING, ERROR | `INFO` |
| `logging.json_format` | Structured logs | Use JSON format for logs | `true` |
| `logging.log_dir` | Log directory | Where to save log files | `qa-logs` |

### JSON Schemas (`config/schemas/`)

| Schema               | Purpose                          |
|----------------------|----------------------------------|
| `skill_schema.json`  | Validates skill.md YAML          |
| `tool_schema.json`   | Validates tool definitions       |
| `resource_schema.json`| Validates resource configs      |
| `pipeline_schema.json`| Validates pipeline stages       |

### Skill YAML Frontmatter (`skill.md`)

```yaml
---
name: qa-BiDi-detect
description: Detects BiDi issues in Hebrew-English documents
version: 1.0.0
level: 2                    # 0=meta, 1=family, 2=worker
skill_type: detection       # orchestrator, detection, fix, validation
family: BiDi
parent: qa-BiDi
has_python_tool: true
tags: [qa, bidi, detection, level-2]
detection_rules:
  - bidi-numbers
  - bidi-english
  - bidi-acronym
---
```

---

## Multithreading and Lock Mechanism

### ResourceManager (`shared/threading.py`)

Thread-safe singleton for resource locking using mutex pattern.

```python
from qa_engine.shared.threading import ResourceManager

# Get singleton instance
manager = ResourceManager()

# Acquire lock with timeout
if manager.acquire("chapter01.tex", agent_id="agent-1", timeout=60.0):
    try:
        # Critical section - exclusive access
        process_file("chapter01.tex")
    finally:
        manager.release("chapter01.tex", agent_id="agent-1")

# Using context manager (recommended)
with manager.locked("chapter01.tex", agent_id="agent-1", timeout=60.0):
    process_file("chapter01.tex")

# Check lock status
if manager.is_locked("chapter01.tex"):
    owner = manager.get_owner("chapter01.tex")
    print(f"Resource locked by: {owner}")

# Find stale locks (older than 120 seconds)
stale = manager.get_stale_locks(timeout_seconds=120)
for resource in stale:
    print(f"Stale lock: {resource}")
```

### Coordinator (`infrastructure/coordination/coordinator.py`)

Database-backed coordination for distributed agents using SQLite.

```python
from qa_engine.infrastructure.coordination import Coordinator

coordinator = Coordinator("qa_coordination.db")

# Acquire resource with expiration
if coordinator.acquire_resource("main.tex", agent_id="agent-1", timeout=60):
    try:
        # Process resource
        coordinator.update_status("qa-BiDi-detect", "running", "agent-1")
        # ... do work ...
        coordinator.update_status("qa-BiDi-detect", "completed", "agent-1", issues_found=5)
    finally:
        coordinator.release_resource("main.tex", "agent-1")

# Check resource ownership
owner = coordinator.get_resource_owner("main.tex")

# Get all skill statuses
statuses = coordinator.get_all_status()
```

### Lock Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ResourceManager                           │
│                    (In-Memory Locks)                         │
├─────────────────────────────────────────────────────────────┤
│  _locks: Dict[str, threading.Lock]                          │
│  _owners: Dict[str, str]                                    │
│  _timestamps: Dict[str, datetime]                           │
│                                                             │
│  Thread-safe operations via _manager_lock                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Coordinator                              │
│                   (SQLite Persistence)                       │
├─────────────────────────────────────────────────────────────┤
│  qa_locks table:                                            │
│    resource | agent_id | acquired_at | expires_at           │
│                                                             │
│  qa_status table:                                           │
│    skill_name | state | started_at | issues_found | agent_id│
└─────────────────────────────────────────────────────────────┘
```

---

## Watchdog and Heartbeat Monitor

### HeartbeatMonitor (`infrastructure/coordination/heartbeat.py`)

Monitors agent health and detects stale agents.

```python
from qa_engine.infrastructure.coordination import HeartbeatMonitor

# Initialize monitor
monitor = HeartbeatMonitor(
    db_path="qa_heartbeat.db",
    stale_timeout=120,      # Seconds without heartbeat = stale
    check_interval=30       # Check every 30 seconds
)

# Update heartbeat (call periodically)
monitor.update_heartbeat("agent-1", current_task="Processing chapter 3")

# Define callback for stale agents
def on_stale_agent(agent_info):
    print(f"Stale agent detected: {agent_info['agent_id']}")
    print(f"Last seen: {agent_info['last_seen']}")
    print(f"Task: {agent_info['current_task']}")
    # Cleanup or restart agent

# Start background watchdog thread
monitor.start_watchdog(on_stale=on_stale_agent)

# Get agent status
status = monitor.get_agent_status("agent-1")

# Stop watchdog
monitor.stop_watchdog()

# Remove agent from tracking
monitor.remove_agent("agent-1")
```

### Watchdog Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Agent 1      │     │    Agent 2      │     │    Agent N      │
│  (Worker)       │     │  (Worker)       │     │  (Worker)       │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │ update_heartbeat()    │ update_heartbeat()    │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     HeartbeatMonitor                             │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │ Watchdog Thread │───►│ check_stale_agents() every 30s     │ │
│  │ (Background)    │    │ └─► on_stale callback if detected   │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
│                                                                  │
│  SQLite: qa_heartbeat table                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ agent_id | last_seen            | current_task              ││
│  │ agent-1  | 2025-01-15T10:30:00  | Processing chapter 3      ││
│  │ agent-2  | 2025-01-15T10:28:00  | Running qa-BiDi-detect    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Logging System

### PrintManager (`shared/logging.py`)

Thread-safe console output with verbosity control.

```python
from qa_engine.shared.logging import PrintManager

# Get singleton instance
printer = PrintManager()

# Enable verbose mode
printer.set_verbose(True)

# Log messages
printer.info("Processing file: main.tex")
printer.debug("Chunk 1/5 processed")     # Only shown in verbose mode
printer.warning("Large file detected")
printer.error("Failed to process file")

# Output format: [HH:MM:SS] LEVEL: message
# [10:30:45] INFO: Processing file: main.tex
```

### JsonLogger (`shared/logging.py`)

Structured JSON logging to files for analysis.

```python
from qa_engine.shared.logging import JsonLogger, LogLevel

# Get singleton instance
logger = JsonLogger()

# Configure logger
logger.configure(log_dir="qa-logs", min_level="INFO")

# Log events
logger.log(LogLevel.INFO, "skill_started", agent_id="agent-1", skill="qa-BiDi-detect")
logger.log(LogLevel.WARNING, "large_file", agent_id="agent-1", file="chapter05.tex", lines=5000)
logger.log(LogLevel.ERROR, "detection_failed", agent_id="agent-1", error="Timeout")

# Convenience method
logger.log_event("issues_found", "agent-1", count=15, skill="qa-BiDi-detect")
```

### Log File Format

```json
{"timestamp": "2025-01-15T10:30:45.123456", "level": "INFO", "agent": "agent-1", "event": "skill_started", "payload": {"skill": "qa-BiDi-detect"}}
{"timestamp": "2025-01-15T10:30:46.234567", "level": "INFO", "agent": "agent-1", "event": "issues_found", "payload": {"count": 15}}
```

---

## Dependency Injection

### DIContainer (`shared/di.py`)

Thread-safe singleton DI container for service management.

```python
from qa_engine.shared.di import DIContainer

# Get singleton container
container = DIContainer()

# Register service with factory (singleton by default)
container.register(
    interface=ConfigManager,
    factory=lambda: ConfigManager(),
    singleton=True
)

# Register existing instance
config = ConfigManager()
config.load("qa_setup.json")
container.register_instance(ConfigManager, config)

# Register transient (new instance each time)
container.register(
    interface=BiDiDetector,
    factory=lambda: BiDiDetector(),
    singleton=False
)

# Resolve service
config = container.resolve(ConfigManager)
detector = container.resolve(BiDiDetector)

# Check if registered
if container.is_registered(ConfigManager):
    print("ConfigManager is registered")

# Reset for testing
DIContainer.reset()
```

---

## Batch Processing

### BatchProcessor (`infrastructure/processing/batch_processor.py`)

Smart chunking and parallel processing for large documents.

```python
from qa_engine.infrastructure.processing import BatchProcessor
from pathlib import Path

# Initialize with custom settings
processor = BatchProcessor(
    chunk_size=500,    # Lines per chunk
    max_workers=4      # Parallel threads
)

# Create chunks from file
content = Path("large_file.tex").read_text()
chunks = processor.create_chunks(Path("large_file.tex"), content)

print(f"Created {len(chunks)} chunks")
for chunk in chunks:
    print(f"  Chunk {chunk.chunk_index}: lines {chunk.start_line}-{chunk.end_line}")

# Define processor function
def detect_issues(content: str, file_path: str, offset: int) -> List[Issue]:
    detector = BiDiDetector()
    return detector.detect(content, file_path, offset)

# Process in parallel
results = processor.process_chunks(chunks, detect_issues, parallel=True)

# Merge results (deduplicate overlaps)
all_issues = processor.merge_results(results)
print(f"Found {len(all_issues)} unique issues")
```

### Chunking Strategy

```
┌──────────────────────────────────────────────────────────────┐
│                    Large File (2500 lines)                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Chunk 0: Lines 1-510 (500 + 10 overlap)                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Content lines 1-500                                  │    │
│  │ + 10 overlap lines for cross-line issues             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Chunk 1: Lines 501-1010                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Content lines 501-1000                               │    │
│  │ + 10 overlap lines                                   │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Chunk 2: Lines 1001-1510                                    │
│  ...                                                         │
│                                                              │
│  Chunk 4: Lines 2001-2500 (final chunk, no overlap)          │
│                                                              │
└──────────────────────────────────────────────────────────────┘

                    │
                    │ ThreadPoolExecutor (4 workers)
                    ▼

┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Thread 1│  │ Thread 2│  │ Thread 3│  │ Thread 4│
│ Chunk 0 │  │ Chunk 1 │  │ Chunk 2 │  │ Chunk 3 │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                       │
                       ▼
              merge_results()
        (deduplicate overlap issues)
```

---

## Usage

### Basic Usage

```python
from qa_engine.infrastructure import (
    SuperOrchestrator,
    BiDiOrchestrator,
    ImageOrchestrator,
    TypesetOrchestrator
)

# Super Orchestrator - Run all families
orchestrator = SuperOrchestrator(project_path=Path("my_project"))
result = orchestrator.run(
    content=tex_content,
    file_path="chapter01.tex",
    families=["BiDi", "img", "typeset"],
    apply_fixes=True
)

print(f"Total issues: {result.total_issues}")
print(f"Total fixed: {result.total_fixed}")
print(f"Verdict: {result.verdict}")

# Family Orchestrator - Run specific family
bidi = BiDiOrchestrator()
result = bidi.run(tex_content, "chapter01.tex", apply_fixes=True)

# Detection only
result = bidi.run(tex_content, "chapter01.tex", apply_fixes=False)
for issue in result.detect_result.text_issues:
    print(f"Line {issue.line}: {issue.content}")

# Get fixed content
if result.fix_result:
    fixed_content = result.fix_result.fixed_content
```

### Using Skill Tools Directly

```python
# Import from skill tool.py
import sys
sys.path.insert(0, "src")

# BiDi tool
from qa_engine.infrastructure.detection import BiDiDetector
from qa_engine.infrastructure.fixing import BidiFixer

detector = BiDiDetector()
issues = detector.detect(content, "file.tex")

fixer = BidiFixer()
fixed = fixer.fix(content, issues)

# Image tool
from qa_engine.infrastructure import ImageOrchestrator

img = ImageOrchestrator(project_root=Path("my_project"))
result = img.run(content, "file.tex", apply_fixes=True, create_missing=True)

# Typeset tool
from qa_engine.infrastructure import TypesetOrchestrator

typeset = TypesetOrchestrator()
result = typeset.run(log_content, tex_content, "file.tex", apply_fixes=True)
```

### CLI Usage

```bash
# Run full QA pipeline
python -m qa_engine.cli.main run --project ./my_latex_project

# Run specific family
python -m qa_engine.cli.main run --project . --family BiDi

# Detection only
python -m qa_engine.cli.main detect --project . --output report.json

# List skills
python -m qa_engine.cli.main skills list

# Show pipeline
python -m qa_engine.cli.main pipeline show
```

---

## Unit Testing

### Running Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_bidi_detector.py -v

# Run specific test class
python -m pytest tests/unit/test_bidi_detector.py::TestBiDiDetector -v

# Run specific test method
python -m pytest tests/unit/test_bidi_detector.py::TestBiDiDetector::test_detect_numbers -v

# Run tests with coverage
python -m pytest tests/ --cov=src/qa_engine --cov-report=html

# Run tests in parallel (requires pytest-xdist)
python -m pytest tests/ -n auto

# Run only unit tests
python -m pytest tests/unit/ -v

# Run integration tests
python -m pytest tests/integration/ -v

# Run architecture tests
python -m pytest tests/arch/ -v

# Run comparison tests (LLM vs Python)
python -m pytest tests/comparison/ -v
```

### Test Structure

```
tests/
├── unit/                       # Unit tests (isolated components)
│   ├── test_bidi_detector.py
│   ├── test_bidi_orchestrator.py
│   ├── test_image_orchestrator.py
│   ├── test_typeset_orchestrator.py
│   ├── test_super_orchestrator.py
│   ├── test_config.py
│   ├── test_threading.py
│   └── ...
│
├── integration/                # Integration tests (component interaction)
│   ├── test_controller.py
│   └── test_cls_examples.py
│
├── arch/                       # Architecture tests (structural validation)
│   ├── test_architecture.py    # Layer dependencies
│   └── test_skill_structure.py # Skill file structure
│
└── comparison/                 # Comparison tests (LLM skill vs Python tool)
    ├── test_bib_comparison.py
    ├── test_fancy_table_comparison.py
    └── test_typeset_detect_comparison.py
```

### Writing Tests

```python
"""Unit tests for BiDi Detector."""
import pytest
from qa_engine.infrastructure.detection import BiDiDetector


class TestBiDiDetector:
    """Tests for BiDiDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = BiDiDetector()

    def test_detect_unwrapped_numbers(self):
        """Test detecting unwrapped numbers in Hebrew context."""
        content = r"בשנת 2024 פותחו מודלים חדשים"
        issues = self.detector.detect(content, "test.tex")

        assert len(issues) >= 1
        assert any(i.rule == "bidi-numbers" for i in issues)

    def test_detect_unwrapped_english(self):
        """Test detecting unwrapped English in Hebrew context."""
        content = r"המודל נקרא CNN והוא מבוסס על"
        issues = self.detector.detect(content, "test.tex")

        assert len(issues) >= 1
        assert any(i.rule == "bidi-english" for i in issues)

    def test_no_issues_when_wrapped(self):
        """Test no issues when content is properly wrapped."""
        content = r"בשנת \num{2024} פותחו מודלים"
        issues = self.detector.detect(content, "test.tex")

        assert len(issues) == 0

    def test_get_rules(self):
        """Test get_rules returns rule descriptions."""
        rules = self.detector.get_rules()

        assert "bidi-numbers" in rules
        assert isinstance(rules["bidi-numbers"], str)
```

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings = ignore::DeprecationWarning
```

---

## Skill Reference

### Level 0 - Super Orchestrator

| Skill | Mission | Python Tool |
|-------|---------|-------------|
| `qa-super` | Coordinates all QA families, manages pipeline execution | `SuperOrchestrator` |

### Level 1 - Family Orchestrators

| Skill | Mission | Python Tool |
|-------|---------|-------------|
| `qa-BiDi` | Manages all bidirectional text QA for Hebrew-English documents | `BiDiOrchestrator` |
| `qa-img` | Coordinates image detection, fixing, creation, and validation | `ImageOrchestrator` |
| `qa-typeset` | Manages LaTeX compilation warnings (hbox, vbox, float) | `TypesetOrchestrator` |
| `qa-code` | Handles code block formatting and direction issues | - |
| `qa-table` | Manages table RTL rendering and styling | - |
| `qa-bib` | Handles bibliography and citation issues | `BibOrchestrator` |
| `qa-infra` | Manages project structure and file organization | - |

### Level 2 - Worker Skills (Detection)

| Skill | Mission | Python Tool | Auto-Fix |
|-------|---------|-------------|----------|
| `qa-BiDi-detect` | Detects unwrapped numbers, English, acronyms in Hebrew | `BiDiDetector` | N/A |
| `qa-img-detect` | Detects missing images, wrong paths, case mismatches | `ImageDetector` | N/A |
| `qa-typeset-detect` | Parses .log files for compilation warnings | `TypesetDetector` | N/A |
| `qa-code-detect` | Detects code block background and encoding issues | `CodeDetector` | N/A |
| `qa-table-detect` | Detects table RTL issues and styling problems | `TableDetector` | N/A |
| `qa-bib-detect` | Detects missing .bib files and undefined citations | `BibDetector` | N/A |
| `qa-heb-math-detect` | Detects Hebrew text in math mode | `HebMathDetector` | N/A |

### Level 2 - Worker Skills (Fixing)

| Skill | Mission | Python Tool | Auto-Fix |
|-------|---------|-------------|----------|
| `qa-BiDi-fix-text` | Wraps numbers with `\num{}`, English with `\en{}` | `BidiFixer` | Yes |
| `qa-img-fix-paths` | Corrects image paths, extensions, case | `ImageFixer` | Yes |
| `qa-img-fix-missing` | Creates placeholder images for missing files | `ImageCreator` | Yes |
| `qa-typeset-fix-hbox` | Fixes overfull hbox (tables, sloppy) | `HboxFixer` | Hybrid |
| `qa-typeset-fix-vbox` | Fixes underfull vbox (raggedbottom, vfill) | `VboxFixer` | Yes |
| `qa-typeset-fix-float` | Fixes float too large (breakable, scale) | `FloatFixer` | Hybrid |
| `qa-code-fix-encoding` | Fixes emoji and special character encoding | `EncodingFixer` | Yes |

### Level 2 - Worker Skills (Validation)

| Skill | Mission | Python Tool | Requires |
|-------|---------|-------------|----------|
| `qa-img-validate` | Validates images render correctly in PDF | `ImageValidator` | PDF |
| `qa-coverpage` | Validates cover page BiDi rendering | - | PDF + LLM |

### Standalone Skill Usage

```python
# Example: Using qa-BiDi-detect standalone
from qa_engine.infrastructure.detection import BiDiDetector

detector = BiDiDetector()
content = open("chapter01.tex").read()
issues = detector.detect(content, "chapter01.tex")

for issue in issues:
    print(f"[{issue.rule}] Line {issue.line}: {issue.content}")
    print(f"  Suggested fix: {issue.fix}")
```

---

## How to Add New Skill

### Step 1: Create Skill Directory

```powershell
mkdir .claude\skills\qa-my-skill
```

### Step 2: Create `skill.md`

```markdown
---
name: qa-my-skill
description: Detects custom issues in LaTeX documents (Level 2 skill)
version: 1.0.0
author: Your Name
tags: [qa, custom, detection, level-2]
family: BiDi
parent: qa-BiDi
has_python_tool: true
detection_rules:
  - my-custom-rule-1
  - my-custom-rule-2
---

# My Custom Skill (Level 2)

## Agent Identity
- **Name:** My Custom Detector
- **Role:** Detects custom issues
- **Level:** 2 (Worker)
- **Parent:** qa-BiDi (Level 1)

## Mission Statement

Detect custom issues in Hebrew-English LaTeX documents.

## Detection Rules

### my-custom-rule-1
- **Pattern:** `custom pattern here`
- **Severity:** WARNING
- **Fix:** Wrap with `\custom{}`

## Python Tool Integration

```python
from qa_engine.infrastructure.detection import MyCustomDetector

detector = MyCustomDetector()
issues = detector.detect(content, file_path)
```
```

### Step 3: Create Python Detector

Create `src/qa_engine/infrastructure/detection/my_custom_detector.py`:

```python
"""My custom detector implementation."""
from __future__ import annotations

import re
from typing import Dict, List

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue, Severity


class MyCustomDetector(DetectorInterface):
    """Detects custom issues in LaTeX documents."""

    def __init__(self) -> None:
        self._rules = self._build_rules()

    def _build_rules(self) -> Dict[str, Dict]:
        return {
            "my-custom-rule-1": {
                "description": "Custom issue type 1",
                "pattern": r"pattern_here",
                "severity": Severity.WARNING,
            },
        }

    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        issues: List[Issue] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            for rule_name, rule_def in self._rules.items():
                if re.search(rule_def["pattern"], line):
                    issues.append(Issue(
                        rule=rule_name,
                        file=file_path,
                        line=line_num + offset,
                        content=line.strip(),
                        severity=rule_def["severity"],
                        fix="Suggested fix here",
                    ))

        return issues

    def get_rules(self) -> Dict[str, str]:
        return {name: rule["description"] for name, rule in self._rules.items()}
```

### Step 4: Create `tool.py` Wrapper

Create `.claude/skills/qa-my-skill/tool.py`:

```python
"""Python tool for qa-my-skill."""
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.detection.my_custom_detector import MyCustomDetector


def detect(content: str, file_path: str = "", offset: int = 0) -> List[Dict]:
    """Detect custom issues in content."""
    detector = MyCustomDetector()
    issues = detector.detect(content, file_path, offset)
    return [issue.to_dict() for issue in issues]


def get_rules() -> Dict[str, str]:
    """Return detection rules."""
    detector = MyCustomDetector()
    return detector.get_rules()


if __name__ == "__main__":
    # Demo
    sample = r"Sample content with custom pattern"
    issues = detect(sample, "demo.tex")
    print(f"Found {len(issues)} issues")
```

### Step 5: Export in `__init__.py`

Edit `src/qa_engine/infrastructure/detection/__init__.py`:

```python
from .my_custom_detector import MyCustomDetector

__all__ = [
    # ... existing exports ...
    "MyCustomDetector",
]
```

### Step 6: Write Tests

Create `tests/unit/test_my_custom_detector.py`:

```python
"""Unit tests for My Custom Detector."""
import pytest
from qa_engine.infrastructure.detection import MyCustomDetector


class TestMyCustomDetector:
    def setup_method(self):
        self.detector = MyCustomDetector()

    def test_detect_custom_issue(self):
        content = "content with custom pattern"
        issues = self.detector.detect(content, "test.tex")
        assert len(issues) >= 1

    def test_get_rules(self):
        rules = self.detector.get_rules()
        assert "my-custom-rule-1" in rules
```

### Step 7: Register in Pipeline (Optional)

```python
from qa_engine.management import PipelineManager

pipeline.insert_skill("qa-my-skill")
pipeline.save_pipeline()
```

---

## How to Add New Tool

### Step 1: Implement Interface

For a **detector tool**:

```python
# src/qa_engine/infrastructure/detection/new_detector.py
from ...domain.interfaces import DetectorInterface

class NewDetector(DetectorInterface):
    def detect(self, content: str, file_path: str, offset: int = 0) -> List[Issue]:
        # Implementation
        pass

    def get_rules(self) -> Dict[str, str]:
        # Implementation
        pass
```

For a **fixer tool**:

```python
# src/qa_engine/infrastructure/fixing/new_fixer.py
from ...domain.interfaces import FixerInterface

class NewFixer(FixerInterface):
    def fix(self, content: str, issues: List[Issue]) -> str:
        # Implementation
        pass

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        # Implementation
        pass
```

For a **creator tool**:

```python
# src/qa_engine/infrastructure/creation/new_creator.py
from ...domain.interfaces import CreatorInterface

class NewCreator(CreatorInterface):
    def create(self, path: str, **options) -> bool:
        # Implementation
        pass

    def create_from_issues(self, issues: List[Issue]) -> Dict[str, bool]:
        # Implementation
        pass

    def get_supported_formats(self) -> List[str]:
        # Implementation
        pass
```

### Step 2: Create Rules File (Optional)

```python
# src/qa_engine/infrastructure/detection/new_rules.py
from ...domain.models.issue import Severity

NEW_RULES = {
    "new-rule-1": {
        "description": "Description of rule 1",
        "pattern": r"regex_pattern",
        "severity": Severity.WARNING,
    },
}
```

### Step 3: Export and Test

Same as skill steps 5-6.

---

## How to Add New Resource

Resources are configuration files, rule definitions, or pattern libraries.

### Step 1: Create Resource File

```json
// config/resources/my_patterns.json
{
  "version": "1.0.0",
  "patterns": {
    "pattern-1": {
      "find": "regex_find",
      "replace": "replacement",
      "description": "What this pattern does"
    }
  }
}
```

### Step 2: Create Resource Model

```python
# If custom loading is needed
from qa_engine.domain.models.resource_model import PatternsResource

resource = PatternsResource(
    id="my-patterns",
    name="My Patterns",
    description="Custom patterns for XYZ",
    file_path=Path("config/resources/my_patterns.json"),
    format="json"
)
```

### Step 3: Load in Tool

```python
class MyFixer(FixerInterface):
    def __init__(self, patterns_path: Path = None):
        if patterns_path:
            self._patterns = self._load_patterns(patterns_path)
        else:
            self._patterns = DEFAULT_PATTERNS
```

---

## Migration: Local to Global Skills

### Understanding Skill Locations

- **Local (Project)**: `.claude/skills/` in project directory
- **Global (User)**: `~/.claude/skills/` (user home)

### Step 1: Copy Skill Files

```powershell
# Windows: Copy to global location
$source = ".\.claude\skills\qa-my-skill"
$dest = "$env:USERPROFILE\.claude\skills\qa-my-skill"

Copy-Item -Path $source -Destination $dest -Recurse
```

### Step 2: Update Python Path in tool.py

Local `tool.py`:
```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
```

Global `tool.py`:
```python
# Option 1: Install package globally
# pip install -e /path/to/skill-python-base

# Option 2: Add explicit path
QA_ENGINE_PATH = Path("C:/path/to/skill-python-base/src")
sys.path.insert(0, str(QA_ENGINE_PATH))
```

### Step 3: Install Python Package Globally

```powershell
# Install package in editable mode
pip install -e C:\path\to\skill-python-base

# Or create wheel and install
cd C:\path\to\skill-python-base
pip install build
python -m build
pip install dist/qa_engine-1.0.0-py3-none-any.whl
```

### Step 4: Update skill.md Paths

If skill.md references local files, update to absolute paths or package imports.

### Step 5: Verify Global Installation

```powershell
# Test from any directory
cd ~
python -c "from qa_engine.infrastructure import BiDiDetector; print('OK')"

# Test skill tool
python ~/.claude/skills/qa-my-skill/tool.py
```

### Migration Checklist

- [ ] Copy skill directory to global location
- [ ] Update `tool.py` Python path
- [ ] Install qa_engine package globally
- [ ] Update any hardcoded paths in skill.md
- [ ] Test skill from different directory
- [ ] Remove local copy (optional)

---

## Algorithm Reference

### Detection Algorithm

```
INPUT: LaTeX content, file_path
OUTPUT: List[Issue]

1. LOAD rules from *_rules.py
2. SPLIT content into lines
3. FOR each line:
   a. FOR each rule:
      i.  MATCH regex pattern against line
      ii. IF match found:
          - CREATE Issue with rule, line, content, severity
          - SUGGEST fix based on rule
          - APPEND to issues list
4. RETURN issues sorted by line number
```

### Fix Algorithm

```
INPUT: content, List[Issue]
OUTPUT: fixed_content

1. SORT issues by line number (descending to preserve line numbers)
2. SPLIT content into lines
3. FOR each issue:
   a. GET fix pattern from rule
   b. APPLY regex substitution to line
   c. IF pattern requires LLM:
      - ADD to manual_review list
4. JOIN lines
5. RETURN fixed_content, manual_review list
```

### Orchestration Algorithm

```
INPUT: content, file_path, families, apply_fixes
OUTPUT: OrchestratorResult

1. INITIALIZE result with run_id, timestamps
2. LOAD configuration
3. DETERMINE enabled families
4. FOR each family (parallel or sequential):
   a. RUN detection phase
   b. IF apply_fixes AND issues found:
      i.  RUN fix phase
      ii. IF validation available:
          RUN validation phase
   c. AGGREGATE family result
5. COMPUTE verdict (PASS/WARNING/FAIL)
6. RETURN result
```

---

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/my-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m pytest tests/ -v`)
5. Keep Python files under 150 lines
6. Submit pull request

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: See `docs/` directory for additional guides

## Version

1.0.0
