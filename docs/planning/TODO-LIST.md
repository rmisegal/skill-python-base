# Comprehensive TODO List - QA Skill Python Base System

**Document Version:** 1.0.0
**Date:** 2025-12-15
**Source:** IMPLEMENTATION-PLAN.md v1.0.0
**Reference:** PRD-QA-SKILL-PYTHON-BASE.md v1.1.0

---

## Quick Statistics

| Category | Count |
|----------|-------|
| Total Tasks | 147 |
| Phase 0 (Setup) | 12 |
| Phase 1 (Foundation) | 22 |
| Phase 2 (Python Tools) | 42 |
| Phase 3 (Orchestration) | 28 |
| Phase 4 (insert_qa_skill) | 18 |
| Phase 5 (Migration/Validation) | 20 |
| Phase 6 (Deployment) | 15 |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Pending |
| `[~]` | In Progress |
| `[x]` | Completed |
| `[!]` | Blocked |
| `[P]` | Can run in PARALLEL |
| `[S]` | Must run SEQUENTIAL |
| `[B]` | BLOCKING - must complete before next phase |

**Priority:**
- **P0** = Critical (blocking)
- **P1** = High (important)
- **P2** = Medium (nice to have)

---

## Phase 0: Project Setup

**Objective:** Initialize project structure and development environment

### 0.1 Directory Structure [P0] [B]

| ID | Task | Priority | Status | Parallel | Acceptance Criteria |
|----|------|----------|--------|----------|---------------------|
| P0-001 | Create project root: `C:\25D\Richman\skill-python-base\` | P0 | [ ] | - | Directory exists |
| P0-002 | Create `.claude/` directory | P0 | [ ] | [P] | Directory exists |
| P0-003 | Create `.claude/skills/` directory | P0 | [ ] | [P] | Directory exists |
| P0-004 | Create `qa_engine/` directory | P0 | [ ] | [P] | Directory exists |
| P0-005 | Create `tests/` directory structure | P0 | [ ] | [P] | unit/, skill_tests/, integration/, fixtures/ exist |
| P0-006 | Create `docs/` directory | P0 | [ ] | [P] | Directory exists |

### 0.2 Configuration Files [P0] [B]

| ID | Task | Priority | Status | Parallel | Acceptance Criteria |
|----|------|----------|--------|----------|---------------------|
| P0-007 | Create `pytest.ini` | P0 | [ ] | [P] | pytest runs with config |
| P0-008 | Create `.gitignore` | P0 | [ ] | [P] | Ignores __pycache__, .db, etc. |
| P0-009 | Create `requirements.txt` | P0 | [ ] | [P] | Lists pytest, etc. |
| P0-010 | Create `README.md` for project | P1 | [ ] | [P] | Basic project description |
| P0-011 | Create `pyproject.toml` (optional) | P2 | [ ] | [P] | Package config if needed |
| P0-012 | Initialize git repository | P1 | [ ] | [S] | .git exists, initial commit |

---

## Phase 1: Foundation

**Objective:** Establish core infrastructure and interfaces
**Blocking:** Must complete before Phase 2

### 1.1 Package Initialization [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-001 | Create `qa_engine/__init__.py` | P0 | [ ] | - | P0-004 | Package importable |
| P1-002 | Add version info to `__init__.py` | P0 | [ ] | [S] | P1-001 | `qa_engine.__version__` works |
| P1-003 | Create `qa_engine/exceptions.py` | P0 | [ ] | [P] | P1-001 | Custom exceptions defined |

### 1.2 Interfaces Module [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-004 | Create `qa_engine/interfaces.py` | P0 | [ ] | [P] | P1-001 | File exists |
| P1-005 | Implement `Severity` enum | P0 | [ ] | [P] | P1-004 | INFO, WARNING, CRITICAL |
| P1-006 | Implement `Issue` dataclass | P0 | [ ] | [P] | P1-004 | All fields defined per PRD |
| P1-007 | Implement `DetectorInterface` ABC | P0 | [ ] | [P] | P1-004 | detect(), get_rules() methods |
| P1-008 | Implement `FixerInterface` ABC | P0 | [ ] | [P] | P1-004 | fix(), get_patterns() methods |
| P1-009 | Write tests for interfaces | P0 | [ ] | [S] | P1-005 to P1-008 | 100% coverage |

### 1.3 Document Analyzer [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-010 | Create `qa_engine/document_analyzer.py` | P0 | [ ] | [P] | P1-001 | File exists |
| P1-011 | Implement `count_lines()` | P0 | [ ] | [P] | P1-010 | Returns correct line count |
| P1-012 | Implement `count_files()` | P0 | [ ] | [P] | P1-010 | Returns correct file count |
| P1-013 | Implement `estimate_tokens()` | P0 | [ ] | [P] | P1-010 | Returns token estimate |
| P1-014 | Implement `recommend_strategy()` | P0 | [ ] | [S] | P1-011 to P1-013 | Returns strategy enum |
| P1-015 | Implement `analyze_project()` | P0 | [ ] | [S] | P1-014 | Returns full metrics dict |
| P1-016 | Write tests for document_analyzer | P0 | [ ] | [S] | P1-015 | 90%+ coverage |

### 1.4 Coordination Module [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-017 | Create `qa_engine/coordination.py` | P0 | [ ] | [P] | P1-001 | File exists |
| P1-018 | Implement SQLite schema (qa_status, qa_locks, qa_heartbeat) | P0 | [ ] | [S] | P1-017 | Tables created on init |
| P1-019 | Implement `acquire_resource()` | P0 | [ ] | [S] | P1-018 | Lock acquired/rejected |
| P1-020 | Implement `release_resource()` | P0 | [ ] | [S] | P1-019 | Lock released |
| P1-021 | Implement `update_heartbeat()` | P0 | [ ] | [S] | P1-018 | Heartbeat recorded |
| P1-022 | Implement `check_stale_agents()` | P0 | [ ] | [S] | P1-021 | Returns stale agent list |
| P1-023 | Implement `update_skill_status()` | P0 | [ ] | [S] | P1-018 | Status updated in DB |
| P1-024 | Implement `get_all_status()` | P0 | [ ] | [S] | P1-023 | Returns status dict |
| P1-025 | Write tests for coordination | P0 | [ ] | [S] | P1-019 to P1-024 | 90%+ coverage |

### 1.5 Logging System [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-026 | Create `qa_engine/logging_system.py` | P0 | [ ] | [P] | P1-001 | File exists |
| P1-027 | Implement structured log format | P0 | [ ] | [S] | P1-026 | JSON-formatted logs |
| P1-028 | Implement file handler | P0 | [ ] | [S] | P1-027 | Logs to qa-logs/ |
| P1-029 | Implement console handler | P0 | [ ] | [S] | P1-027 | Logs to console |
| P1-030 | Implement event types (SKILL_START, SKILL_COMPLETE, etc.) | P0 | [ ] | [S] | P1-027 | All event types defined |
| P1-031 | Write tests for logging | P0 | [ ] | [S] | P1-028 to P1-030 | 90%+ coverage |

### 1.6 Configuration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-032 | Create `qa_setup.json` schema | P0 | [ ] | [S] | P1-006 | Valid JSON schema |
| P1-033 | Create default `qa_setup.json` | P0 | [ ] | [S] | P1-032 | File exists with defaults |
| P1-034 | Create `qa_engine/config_loader.py` | P0 | [ ] | [S] | P1-032 | File exists |
| P1-035 | Implement `load_config()` | P0 | [ ] | [S] | P1-034 | Loads and validates config |
| P1-036 | Implement `apply_defaults()` | P0 | [ ] | [S] | P1-035 | Missing values filled |
| P1-037 | Write tests for config_loader | P0 | [ ] | [S] | P1-035, P1-036 | 90%+ coverage |

### 1.7 Phase 1 Integration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-038 | Create Phase 1 integration test | P0 | [ ] | [S] | All P1 tasks | All modules work together |
| P1-039 | Verify module imports work | P0 | [ ] | [S] | P1-038 | No import errors |
| P1-040 | Document Phase 1 completion | P1 | [ ] | [S] | P1-039 | CHANGELOG updated |

---

## Phase 2: Python Tool Migration

**Objective:** Migrate all detection logic to deterministic Python tools
**Blocking:** Must complete before Phase 3

### 2.1 BiDi Detector [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-001 | Create `qa-BiDi-detect/` skill directory | P0 | [ ] | [P] | Phase 1 | Directory exists |
| P2-002 | Create `qa-BiDi-detect/tool.py` structure | P0 | [ ] | [S] | P2-001 | BiDiDetector class |
| P2-003 | Implement Rule 1: Cover Page Metadata | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-004 | Implement Rule 2: Table Cell Hebrew | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-005 | Implement Rule 3: Section Numbering | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-006 | Implement Rule 4: Reversed Text | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-007 | Implement Rule 5: Header/Footer Hebrew | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-008 | Implement Rule 6: Numbers Without LTR | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-009 | Implement Rule 7: English Without LTR | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-010 | Implement Rule 8: tcolorbox BiDi-Safe | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-011 | Implement Rule 9: Section Titles | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-012 | Implement Rule 10: Uppercase Acronyms | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-013 | Implement Rule 11: Decimal Numbers | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-014 | Implement Rule 12: Chapter Labels | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-015 | Implement Rule 13: fbox/parbox Mixed | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-016 | Implement Rule 14: Standalone Counter | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-017 | Implement Rule 15: Hebrew in English | P0 | [ ] | [P] | P2-002 | Detection works |
| P2-018 | Create `qa-BiDi-detect/fixtures/` directory | P0 | [ ] | [P] | P2-001 | Directory exists |
| P2-019 | Create valid_document.tex fixture | P0 | [ ] | [P] | P2-018 | No issues expected |
| P2-020 | Create invalid_document.tex fixture | P0 | [ ] | [P] | P2-018 | Known issues |
| P2-021 | Create `qa-BiDi-detect/test_tool.py` | P0 | [ ] | [S] | P2-003 to P2-017 | All rules tested |
| P2-022 | Verify BiDi detector 90%+ coverage | P0 | [ ] | [S] | P2-021 | Coverage report |

### 2.2 Code Detector [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-023 | Create `qa-code-detect/` skill directory | P0 | [ ] | [P] | Phase 1 | Directory exists |
| P2-024 | Create `qa-code-detect/tool.py` structure | P0 | [ ] | [S] | P2-023 | CodeDetector class |
| P2-025 | Implement Phase 2: Background Overflow | P0 | [ ] | [P] | P2-024 | Detection works |
| P2-026 | Implement Phase 3: Character Encoding | P0 | [ ] | [P] | P2-024 | Detection works |
| P2-027 | Implement Phase 4: Language Direction | P0 | [ ] | [P] | P2-024 | Detection works |
| P2-028 | Implement Phase 5: Hebrew Title | P0 | [ ] | [P] | P2-024 | Detection works |
| P2-029 | Implement Phase 6: F-String Braces | P0 | [ ] | [P] | P2-024 | Detection works |
| P2-030 | Create `qa-code-detect/fixtures/` | P0 | [ ] | [P] | P2-023 | Directory exists |
| P2-031 | Create Code fixture documents | P0 | [ ] | [P] | P2-030 | Valid/invalid docs |
| P2-032 | Create `qa-code-detect/test_tool.py` | P0 | [ ] | [S] | P2-025 to P2-029 | All phases tested |
| P2-033 | Verify Code detector 90%+ coverage | P0 | [ ] | [S] | P2-032 | Coverage report |

### 2.3 Typeset Detector [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-034 | Create `qa-typeset-detect/` skill directory | P1 | [ ] | [P] | Phase 1 | Directory exists |
| P2-035 | Create `qa-typeset-detect/tool.py` structure | P1 | [ ] | [S] | P2-034 | TypesetDetector class |
| P2-036 | Implement Overfull/Underfull hbox detection | P1 | [ ] | [P] | P2-035 | Detection works |
| P2-037 | Implement Overfull/Underfull vbox detection | P1 | [ ] | [P] | P2-035 | Detection works |
| P2-038 | Implement Undefined reference detection | P1 | [ ] | [P] | P2-035 | Detection works |
| P2-039 | Implement Float too large detection | P1 | [ ] | [P] | P2-035 | Detection works |
| P2-040 | Implement TikZ overflow risk detection | P1 | [ ] | [P] | P2-035 | Detection works |
| P2-041 | Create `qa-typeset-detect/fixtures/` | P1 | [ ] | [P] | P2-034 | sample.log files |
| P2-042 | Create `qa-typeset-detect/test_tool.py` | P1 | [ ] | [S] | P2-036 to P2-040 | All patterns tested |

### 2.4 Table Detector [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-043 | Create `qa-table-detect/` skill directory | P1 | [ ] | [P] | Phase 1 | Directory exists |
| P2-044 | Create `qa-table-detect/tool.py` structure | P1 | [ ] | [S] | P2-043 | TableDetector class |
| P2-045 | Implement table layout detection rules | P1 | [ ] | [S] | P2-044 | Detection works |
| P2-046 | Create `qa-table-detect/fixtures/` | P1 | [ ] | [P] | P2-043 | Fixture docs |
| P2-047 | Create `qa-table-detect/test_tool.py` | P1 | [ ] | [S] | P2-045 | Rules tested |

### 2.5 BiDi Fixers [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-048 | Create `qa-BiDi-fix-text/` skill directory | P1 | [ ] | [P] | P2-022 | Directory exists |
| P2-049 | Create `qa-BiDi-fix-text/tool.py` | P1 | [ ] | [S] | P2-048 | BiDiTextFixer class |
| P2-050 | Implement text direction fix patterns | P1 | [ ] | [S] | P2-049 | Fixes applied |
| P2-051 | Create `qa-BiDi-fix-text/test_tool.py` | P1 | [ ] | [S] | P2-050 | Fixes verified |
| P2-052 | Create `qa-BiDi-fix-numbers/` skill directory | P1 | [ ] | [P] | P2-022 | Directory exists |
| P2-053 | Create `qa-BiDi-fix-numbers/tool.py` | P1 | [ ] | [S] | P2-052 | BiDiNumberFixer class |
| P2-054 | Implement number wrap patterns (\\en{}) | P1 | [ ] | [S] | P2-053 | Fixes applied |
| P2-055 | Create `qa-BiDi-fix-numbers/test_tool.py` | P1 | [ ] | [S] | P2-054 | Fixes verified |

### 2.6 Code Fixers [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-056 | Create `qa-code-fix-background/` skill directory | P1 | [ ] | [P] | P2-033 | Directory exists |
| P2-057 | Create `qa-code-fix-background/tool.py` | P1 | [ ] | [S] | P2-056 | CodeBackgroundFixer class |
| P2-058 | Implement background overflow fix | P1 | [ ] | [S] | P2-057 | Fixes applied |
| P2-059 | Create `qa-code-fix-background/test_tool.py` | P1 | [ ] | [S] | P2-058 | Fixes verified |
| P2-060 | Create `qa-code-fix-encoding/` skill directory | P1 | [ ] | [P] | P2-033 | Directory exists |
| P2-061 | Create `qa-code-fix-encoding/tool.py` | P1 | [ ] | [S] | P2-060 | CodeEncodingFixer class |
| P2-062 | Implement encoding fix patterns | P1 | [ ] | [S] | P2-061 | Fixes applied |
| P2-063 | Create `qa-code-fix-encoding/test_tool.py` | P1 | [ ] | [S] | P2-062 | Fixes verified |

### 2.7 Phase 2 Integration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-064 | Create Phase 2 integration test | P0 | [ ] | [S] | All P2 detector tasks | All detectors work |
| P2-065 | Verify detector/fixer separation | P0 | [ ] | [S] | P2-064 | No combined detect+fix |
| P2-066 | Document Phase 2 completion | P1 | [ ] | [S] | P2-065 | CHANGELOG updated |

---

## Phase 3: Orchestration Engine

**Objective:** Build batch processing and main controller
**Blocking:** Must complete before Phase 4

### 3.1 Batch Processor [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-001 | Create `qa_engine/batch_processor.py` | P0 | [ ] | [P] | Phase 1 | File exists |
| P3-002 | Implement `find_environment_boundaries()` | P0 | [ ] | [S] | P3-001 | Finds \\begin/\\end |
| P3-003 | Implement `smart_chunk()` | P0 | [ ] | [S] | P3-002 | Chunks at boundaries |
| P3-004 | Implement `process_chunk()` | P0 | [ ] | [S] | P3-003 | Single chunk processed |
| P3-005 | Implement `parallel_process_chunks()` | P0 | [ ] | [S] | P3-004 | Uses ThreadPoolExecutor |
| P3-006 | Implement `merge_results()` | P0 | [ ] | [S] | P3-005 | Results combined |
| P3-007 | Create `tests/unit/test_batch_processor.py` | P0 | [ ] | [S] | P3-006 | 90%+ coverage |
| P3-008 | Test with 50,000+ line document | P0 | [ ] | [S] | P3-007 | Processes successfully |

### 3.2 Skill Discovery [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-009 | Create `qa_engine/skill_discovery.py` | P1 | [ ] | [P] | Phase 1 | File exists |
| P3-010 | Implement `scan_skills_directory()` | P1 | [ ] | [S] | P3-009 | Finds qa-* dirs |
| P3-011 | Implement `parse_skill_frontmatter()` | P1 | [ ] | [S] | P3-010 | Parses YAML |
| P3-012 | Implement `build_hierarchy()` | P1 | [ ] | [S] | P3-011 | L0/L1/L2 tree |
| P3-013 | Implement `find_python_tool()` | P1 | [ ] | [S] | P3-010 | Finds tool.py |
| P3-014 | Create `tests/unit/test_skill_discovery.py` | P1 | [ ] | [S] | P3-013 | 90%+ coverage |

### 3.3 Watchdog Monitor [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-015 | Create `qa_engine/watchdog.py` | P1 | [ ] | [P] | P1-025 | File exists |
| P3-016 | Implement `WatchdogMonitor` class | P1 | [ ] | [S] | P3-015 | Runs in thread |
| P3-017 | Implement `monitor_loop()` | P1 | [ ] | [S] | P3-016 | Checks heartbeats |
| P3-018 | Implement `handle_stale_agent()` | P1 | [ ] | [S] | P3-017 | Logs warning |
| P3-019 | Create `tests/unit/test_watchdog.py` | P1 | [ ] | [S] | P3-018 | Tests pass |

### 3.4 Report Generator [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-020 | Create `qa_engine/report_generator.py` | P1 | [ ] | [P] | Phase 1 | File exists |
| P3-021 | Implement `generate_markdown_report()` | P1 | [ ] | [S] | P3-020 | Creates .md file |
| P3-022 | Implement `generate_json_report()` | P1 | [ ] | [S] | P3-020 | Creates .json file |
| P3-023 | Implement `generate_summary()` | P1 | [ ] | [S] | P3-021, P3-022 | Summary section |
| P3-024 | Create `tests/unit/test_report_generator.py` | P1 | [ ] | [S] | P3-023 | Reports generated |

### 3.5 Main Controller [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-025 | Create `qa_engine/controller.py` | P0 | [ ] | [S] | P3-008, P3-014 | File exists |
| P3-026 | Implement `QAController.__init__()` | P0 | [ ] | [S] | P3-025 | Loads config |
| P3-027 | Implement `run_blocking_checks()` | P0 | [ ] | [S] | P3-026 | CLS version check |
| P3-028 | Implement `run_family()` | P0 | [ ] | [S] | P3-027 | Single family runs |
| P3-029 | Implement `run_skill()` | P0 | [ ] | [S] | P3-028 | Invokes Python tool |
| P3-030 | Implement `run_full_qa()` | P0 | [ ] | [S] | P3-029 | Full pipeline |
| P3-031 | Implement `get_progress()` | P0 | [ ] | [S] | P3-030 | Returns progress % |
| P3-032 | Create `tests/unit/test_controller.py` | P0 | [ ] | [S] | P3-031 | 90%+ coverage |

### 3.6 Phase 3 Integration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-033 | Create `tests/integration/test_full_pipeline.py` | P0 | [ ] | [S] | P3-032 | Full run works |
| P3-034 | Create `tests/integration/test_batch_processing.py` | P0 | [ ] | [S] | P3-033 | Large docs work |
| P3-035 | Create `tests/integration/test_parallel_families.py` | P0 | [ ] | [S] | P3-034 | Parallel works |
| P3-036 | Document Phase 3 completion | P1 | [ ] | [S] | P3-035 | CHANGELOG updated |

---

## Phase 4: insert_qa_skill Meta-Skill

**Objective:** Automate skill creation and Python extraction
**Blocking:** Must complete before Phase 5

### 4.1 Templates [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P4-001 | Create `insert_qa_skill/` skill directory | P1 | [ ] | - | Phase 3 | Directory exists |
| P4-002 | Create `insert_qa_skill/templates/` directory | P1 | [ ] | [S] | P4-001 | Directory exists |
| P4-003 | Create `skill_template.md` | P1 | [ ] | [P] | P4-002 | Valid template |
| P4-004 | Create `detector_template.py` | P1 | [ ] | [P] | P4-002 | Valid template |
| P4-005 | Create `fixer_template.py` | P1 | [ ] | [P] | P4-002 | Valid template |
| P4-006 | Create `test_template.py` | P1 | [ ] | [P] | P4-002 | Valid template |
| P4-007 | Create `fixture_template.tex` | P1 | [ ] | [P] | P4-002 | Valid template |

### 4.2 Generation Tool [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P4-008 | Create `insert_qa_skill/tool.py` | P1 | [ ] | [S] | P4-003 to P4-007 | File exists |
| P4-009 | Implement `parse_arguments()` | P1 | [ ] | [S] | P4-008 | CLI args parsed |
| P4-010 | Implement `create_skill()` (CREATE mode) | P1 | [ ] | [S] | P4-009 | Generates skill |
| P4-011 | Implement `split_skill()` (SPLIT mode) | P1 | [ ] | [S] | P4-010 | Extracts Python |
| P4-012 | Implement `update_parent_orchestrator()` | P1 | [ ] | [S] | P4-010 | Parent updated |
| P4-013 | Implement `update_qa_claude_md()` | P1 | [ ] | [S] | P4-012 | QA-CLAUDE.md updated |
| P4-014 | Implement `validate_generated_skill()` | P1 | [ ] | [S] | P4-013 | Skill validated |

### 4.3 Meta-Skill Definition [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P4-015 | Create `insert_qa_skill/skill.md` | P1 | [ ] | [S] | P4-014 | Valid skill def |
| P4-016 | Create `insert_qa_skill/test_tool.py` | P1 | [ ] | [S] | P4-015 | Tests pass |
| P4-017 | Integration test: create new skill | P1 | [ ] | [S] | P4-016 | New skill created |
| P4-018 | Integration test: split existing skill | P1 | [ ] | [S] | P4-017 | Python extracted |
| P4-019 | Document Phase 4 completion | P1 | [ ] | [S] | P4-018 | CHANGELOG updated |

---

## Phase 5: Skill Migration and Validation

**Objective:** Rewrite existing skills to standard format and validate
**Blocking:** Must complete before Phase 6

### 5.1 L1 Orchestrator Rewrites [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P5-001 | Rewrite `qa-super/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |
| P5-002 | Rewrite `qa-BiDi/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |
| P5-003 | Rewrite `qa-code/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |
| P5-004 | Rewrite `qa-typeset/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |
| P5-005 | Rewrite `qa-table/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |
| P5-006 | Rewrite `qa-infra/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |
| P5-007 | Rewrite `qa-bib/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |
| P5-008 | Rewrite `qa-img/skill.md` to standard | P1 | [ ] | [P] | Phase 4 | Follows standard |

### 5.2 L2 Skill Updates [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P5-009 | Update `qa-BiDi-detect/skill.md` with tool ref | P1 | [ ] | [P] | P2-022 | Tool referenced |
| P5-010 | Update `qa-code-detect/skill.md` with tool ref | P1 | [ ] | [P] | P2-033 | Tool referenced |
| P5-011 | Update all other L2 detection skills | P1 | [ ] | [P] | Phase 2 | All updated |
| P5-012 | Update all L2 fixer skills | P1 | [ ] | [P] | Phase 2 | All updated |

### 5.3 Documentation Updates [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P5-013 | Update `QA-CLAUDE.md` architecture doc | P1 | [ ] | [S] | P5-001 to P5-012 | Current architecture |
| P5-014 | Update `full-pdf-qa.md` command | P1 | [ ] | [S] | P5-013 | Updated command |
| P5-015 | Create user documentation | P1 | [ ] | [P] | P5-014 | README updated |

### 5.4 Validation [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P5-016 | Test with real Hebrew-English document | P0 | [ ] | [S] | P5-014 | QA runs successfully |
| P5-017 | Measure token usage (before vs after) | P0 | [ ] | [S] | P5-016 | 60%+ reduction |
| P5-018 | Run performance benchmark | P0 | [ ] | [P] | P5-016 | Benchmarks pass |
| P5-019 | Create deployment readiness report | P0 | [ ] | [S] | P5-017, P5-018 | Report generated |
| P5-020 | Document Phase 5 completion | P1 | [ ] | [S] | P5-019 | CHANGELOG updated |

---

## Phase 6: Global Deployment

**Objective:** Deploy to global Claude CLI skills location
**All tasks STRICTLY SEQUENTIAL**

### 6.1 Pre-Deployment [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P6-001 | Create backup script | P0 | [ ] | [S] | Phase 5 | Script works |
| P6-002 | Execute backup of global skills | P0 | [ ] | [S] | P6-001 | Backup created |
| P6-003 | Run full local test suite | P0 | [ ] | [S] | P6-002 | 100% pass |
| P6-004 | Verify test coverage >= 90% | P0 | [ ] | [S] | P6-003 | Coverage met |
| P6-005 | Generate deployment report | P0 | [ ] | [S] | P6-004 | Report created |

### 6.2 User Approval [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P6-006 | Present deployment report to user | P0 | [ ] | [S] | P6-005 | Report shown |
| P6-007 | Get explicit user approval | P0 | [ ] | [S] | P6-006 | User approves |

### 6.3 Deployment Execution [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P6-008 | Copy qa-* skills to global location | P0 | [ ] | [S] | P6-007 | Skills copied |
| P6-009 | Copy qa_engine to global location | P0 | [ ] | [S] | P6-008 | Engine copied |
| P6-010 | Copy qa_setup.json to global location | P0 | [ ] | [S] | P6-009 | Config copied |

### 6.4 Post-Deployment Validation [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P6-011 | Run validation tests on global | P0 | [ ] | [S] | P6-010 | Tests pass |
| P6-012 | Update global QA-CLAUDE.md | P0 | [ ] | [S] | P6-011 | Doc updated |
| P6-013 | Test with real project | P0 | [ ] | [S] | P6-012 | QA runs |
| P6-014 | Document rollback procedure | P0 | [ ] | [S] | P6-013 | Procedure doc |
| P6-015 | Final sign-off | P0 | [ ] | [S] | P6-014 | Project complete |

---

## Execution Summary by Parallel Groups

### Phase 1 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P1-002, P1-003, P1-004 to P1-006 (interfaces) | PARALLEL |
| B | P1-010 to P1-016 (document_analyzer) | PARALLEL with A |
| C | P1-017 to P1-025 (coordination) | PARALLEL with A, B |
| D | P1-026 to P1-031 (logging) | PARALLEL with A, B, C |
| E | P1-032 to P1-037 (config) | SEQUENTIAL after A |
| F | P1-038 to P1-040 (integration) | SEQUENTIAL after all |

### Phase 2 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P2-001 to P2-022 (BiDi detector) | PARALLEL |
| B | P2-023 to P2-033 (Code detector) | PARALLEL with A |
| C | P2-034 to P2-042 (Typeset detector) | PARALLEL with A, B |
| D | P2-043 to P2-047 (Table detector) | PARALLEL with A, B, C |
| E | P2-048 to P2-055 (BiDi fixers) | SEQUENTIAL after A |
| F | P2-056 to P2-063 (Code fixers) | SEQUENTIAL after B |
| G | P2-064 to P2-066 (integration) | SEQUENTIAL after all |

### Phase 3 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P3-001 to P3-008 (batch) | PARALLEL |
| B | P3-009 to P3-014 (discovery) | PARALLEL with A |
| C | P3-015 to P3-019 (watchdog) | PARALLEL with A, B |
| D | P3-020 to P3-024 (report) | PARALLEL with A, B, C |
| E | P3-025 to P3-032 (controller) | SEQUENTIAL after A, B |
| F | P3-033 to P3-036 (integration) | SEQUENTIAL after all |

### Phase 4-6: Mostly Sequential

Phase 4, 5, 6 have limited parallelization opportunities as noted in individual task tables.

---

## Progress Tracking

### Overall Progress

| Phase | Total Tasks | Completed | Progress |
|-------|-------------|-----------|----------|
| Phase 0 | 12 | 0 | 0% |
| Phase 1 | 40 | 0 | 0% |
| Phase 2 | 66 | 0 | 0% |
| Phase 3 | 36 | 0 | 0% |
| Phase 4 | 19 | 0 | 0% |
| Phase 5 | 20 | 0 | 0% |
| Phase 6 | 15 | 0 | 0% |
| **TOTAL** | **208** | **0** | **0%** |

---

## Notes

1. **Parallel execution** requires care with shared resources (database, files)
2. **Phase gates** must be respected - do not start next phase until current phase complete
3. **Test coverage** requirement is 90%+ for all Python code
4. **User approval** is required before Phase 6 deployment
5. **Rollback** procedure must be tested before deployment

---

*End of TODO List*
