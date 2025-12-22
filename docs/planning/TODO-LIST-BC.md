# Comprehensive TODO List - BC Skill Python Base System

**Document Version:** 1.0.0
**Date:** 2025-12-22
**Source:** IMPLEMENTATION-PLAN-BC-MECHANISM.md v1.0.0
**Reference:** PRD-BC-SKILL-PYTHON-BASE.md v1.0.0

---

## Quick Statistics

| Category | Count |
|----------|-------|
| Total Tasks | 127 |
| Phase 0 (Setup) | 10 |
| Phase 1 (Foundation) | 24 |
| Phase 2 (Python Validators) | 38 |
| Phase 3 (BC Skill Updates) | 28 |
| Phase 4 (insert_bc_skill) | 16 |
| Phase 5 (Validation & Deployment) | 11 |

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
**Duration:** 0.5 day

### 0.1 Directory Structure [P0] [B]

| ID | Task | Priority | Status | Parallel | Acceptance Criteria |
|----|------|----------|--------|----------|---------------------|
| P0-001 | Create `bc_engine/` directory | P0 | [ ] | - | Directory exists in skill-python-base |
| P0-002 | Create `bc_engine/validators/` directory | P0 | [ ] | [P] | Directory exists |
| P0-003 | Create `bc_engine/tests/` directory | P0 | [ ] | [P] | Directory exists |
| P0-004 | Create `fixtures/` directory | P0 | [ ] | [P] | Directory exists |
| P0-005 | Create `fixtures/valid/` subdirectory | P0 | [ ] | [P] | Directory exists |
| P0-006 | Create `fixtures/invalid/` subdirectory | P0 | [ ] | [P] | Directory exists |

### 0.2 Configuration Files [P0] [B]

| ID | Task | Priority | Status | Parallel | Acceptance Criteria |
|----|------|----------|--------|----------|---------------------|
| P0-007 | Create `bc_engine/pytest.ini` | P0 | [ ] | [P] | pytest runs with config |
| P0-008 | Create `bc_engine/requirements.txt` | P0 | [ ] | [P] | Lists pytest, pytest-cov |
| P0-009 | Create `bc_engine/conftest.py` | P0 | [ ] | [P] | Shared fixtures defined |
| P0-010 | Create `bc_engine/__init__.py` with version | P0 | [ ] | [S] | `bc_engine.__version__` works |

---

## Phase 1: Foundation

**Objective:** Establish core infrastructure and base classes
**Duration:** 3 days
**Blocking:** Must complete before Phase 2

### 1.1 Package Initialization [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-001 | Create `bc_engine/__init__.py` exports | P0 | [ ] | - | P0-010 | All public classes exported |
| P1-002 | Create `bc_engine/exceptions.py` | P0 | [ ] | [P] | P1-001 | BCValidationError, BCTemplateError defined |
| P1-003 | Create `bc_engine/constants.py` | P0 | [ ] | [P] | P1-001 | QA rule IDs, regex patterns |

### 1.2 Base Validator Module [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-004 | Create `bc_engine/validators/__init__.py` | P0 | [ ] | [P] | P0-002 | Package importable |
| P1-005 | Create `bc_engine/validators/base_validator.py` | P0 | [ ] | [S] | P1-004 | File exists |
| P1-006 | Implement `Severity` enum | P0 | [ ] | [S] | P1-005 | ERROR, WARNING, INFO values |
| P1-007 | Implement `ValidationIssue` dataclass | P0 | [ ] | [S] | P1-006 | file, line, rule, message, severity, fix fields |
| P1-008 | Implement `BaseValidator` ABC | P0 | [ ] | [S] | P1-007 | validate(), get_rules() abstract methods |
| P1-009 | Write tests for base_validator | P0 | [ ] | [S] | P1-008 | 100% coverage |

### 1.3 Template Engine [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-010 | Create `bc_engine/template_engine.py` | P0 | [ ] | [P] | P1-001 | File exists |
| P1-011 | Implement `TemplateEngine.__init__()` | P0 | [ ] | [S] | P1-010 | Loads builtin templates |
| P1-012 | Implement `render()` method | P0 | [ ] | [S] | P1-011 | Renders template with context |
| P1-013 | Implement `register_template()` method | P0 | [ ] | [S] | P1-012 | Custom templates added |
| P1-014 | Create builtin templates dict (pythonbox, tikz, table) | P0 | [ ] | [S] | P1-013 | 3+ templates defined |
| P1-015 | Write tests for template_engine | P0 | [ ] | [S] | P1-014 | 90%+ coverage |

### 1.4 Progress Tracker [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-016 | Create `bc_engine/progress_tracker.py` | P1 | [ ] | [P] | P1-001 | File exists |
| P1-017 | Implement `BCTaskStatus` enum | P1 | [ ] | [S] | P1-016 | PENDING, IN_PROGRESS, COMPLETED, FAILED |
| P1-018 | Implement `update_task()` method | P1 | [ ] | [S] | P1-017 | Updates BC-TASKS.md |
| P1-019 | Implement `read_status()` method | P1 | [ ] | [S] | P1-018 | Reads BC-TASKS.md |
| P1-020 | Write tests for progress_tracker | P1 | [ ] | [S] | P1-019 | 90%+ coverage |

### 1.5 Controller (Basic) [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-021 | Create `bc_engine/controller.py` | P0 | [ ] | [S] | P1-009, P1-015 | File exists |
| P1-022 | Implement `BCController.__init__()` | P0 | [ ] | [S] | P1-021 | Loads validators |
| P1-023 | Implement `validate_file()` method | P0 | [ ] | [S] | P1-022 | Single file validation |
| P1-024 | Implement `validate_project()` method | P0 | [ ] | [S] | P1-023 | Full project validation |

### 1.6 Phase 1 Integration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P1-025 | Create Phase 1 integration test | P0 | [ ] | [S] | All P1 tasks | All modules work together |
| P1-026 | Verify module imports work | P0 | [ ] | [S] | P1-025 | No import errors |
| P1-027 | Document Phase 1 completion | P1 | [ ] | [S] | P1-026 | CHANGELOG entry |

---

## Phase 2: Python Validators

**Objective:** Create all Python pre-validation tools
**Duration:** 4 days
**Blocking:** Must complete before Phase 3

### 2.1 Content Validator [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-001 | Create `bc_engine/validators/content_validator.py` | P0 | [ ] | [P] | P1-009 | File exists |
| P2-002 | Implement `ContentValidator` class | P0 | [ ] | [S] | P2-001 | Extends BaseValidator |
| P2-003 | Implement Rule: number-not-wrapped | P0 | [ ] | [S] | P2-002 | Detects numbers in Hebrew without \en{} |
| P2-004 | Implement Rule: english-not-wrapped | P0 | [ ] | [S] | P2-003 | Detects English in Hebrew without \en{} |
| P2-005 | Implement Rule: acronym-not-wrapped | P0 | [ ] | [S] | P2-004 | Detects acronyms (AI, ML) without \en{} |
| P2-006 | Implement Rule: figure-not-referenced | P1 | [ ] | [S] | P2-005 | Figures must have \ref{} in text |
| P2-007 | Create `fixtures/valid/chapter_valid.tex` | P0 | [ ] | [P] | P2-001 | No issues expected |
| P2-008 | Create `fixtures/invalid/chapter_invalid.tex` | P0 | [ ] | [P] | P2-001 | Known issues |
| P2-009 | Create `bc_engine/tests/test_content_validator.py` | P0 | [ ] | [S] | P2-006 | All rules tested |
| P2-010 | Verify content validator 90%+ coverage | P0 | [ ] | [S] | P2-009 | Coverage report |

### 2.2 Code Validator [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-011 | Create `bc_engine/validators/code_validator.py` | P0 | [ ] | [P] | P1-009 | File exists |
| P2-012 | Implement `CodeValidator` class | P0 | [ ] | [S] | P2-011 | Extends BaseValidator |
| P2-013 | Implement Rule: hebrew-in-comment | P0 | [ ] | [S] | P2-012 | Detects Hebrew in code comments |
| P2-014 | Implement Rule: code-no-english-wrapper | P0 | [ ] | [S] | P2-013 | pythonbox without english env |
| P2-015 | Implement Rule: code-too-long | P1 | [ ] | [S] | P2-014 | Code >40 lines warning |
| P2-016 | Implement Rule: emoji-in-code | P1 | [ ] | [S] | P2-015 | Emoji characters detected |
| P2-017 | Create `fixtures/valid/code_valid.tex` | P0 | [ ] | [P] | P2-011 | No issues expected |
| P2-018 | Create `fixtures/invalid/code_invalid.tex` | P0 | [ ] | [P] | P2-011 | Known issues |
| P2-019 | Create `bc_engine/tests/test_code_validator.py` | P0 | [ ] | [S] | P2-016 | All rules tested |
| P2-020 | Verify code validator 90%+ coverage | P0 | [ ] | [S] | P2-019 | Coverage report |

### 2.3 TikZ Validator [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-021 | Create `bc_engine/validators/tikz_validator.py` | P0 | [ ] | [P] | P1-009 | File exists |
| P2-022 | Migrate existing `validate_tikz_bidi.py` logic | P0 | [ ] | [S] | P2-021 | All rules migrated |
| P2-023 | Implement Rule: tikz-no-english-wrapper | P0 | [ ] | [S] | P2-022 | TikZ without \begin{english} |
| P2-024 | Implement Rule: hebrew-in-tikz | P0 | [ ] | [S] | P2-023 | Hebrew chars in TikZ |
| P2-025 | Implement Rule: resizebox-outside-english | P1 | [ ] | [S] | P2-024 | resizebox ordering |
| P2-026 | Create `fixtures/valid/tikz_valid.tex` | P0 | [ ] | [P] | P2-021 | No issues expected |
| P2-027 | Create `fixtures/invalid/tikz_invalid.tex` | P0 | [ ] | [P] | P2-021 | Known issues |
| P2-028 | Create `bc_engine/tests/test_tikz_validator.py` | P0 | [ ] | [S] | P2-025 | All rules tested |
| P2-029 | Verify TikZ validator 90%+ coverage | P0 | [ ] | [S] | P2-028 | Coverage report |

### 2.4 Table Validator [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-030 | Create `bc_engine/validators/table_validator.py` | P1 | [ ] | [P] | P1-009 | File exists |
| P2-031 | Implement `TableValidator` class | P1 | [ ] | [S] | P2-030 | Extends BaseValidator |
| P2-032 | Implement Rule: column-order-wrong | P1 | [ ] | [S] | P2-031 | RTL column order check |
| P2-033 | Implement Rule: cell-not-wrapped | P1 | [ ] | [S] | P2-032 | Hebrew cells need proper wrap |
| P2-034 | Create `fixtures/valid/table_valid.tex` | P1 | [ ] | [P] | P2-030 | No issues expected |
| P2-035 | Create `fixtures/invalid/table_invalid.tex` | P1 | [ ] | [P] | P2-030 | Known issues |
| P2-036 | Create `bc_engine/tests/test_table_validator.py` | P1 | [ ] | [S] | P2-033 | All rules tested |

### 2.5 Citation Validator [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-037 | Create `bc_engine/validators/citation_validator.py` | P1 | [ ] | [P] | P1-009 | File exists |
| P2-038 | Implement `CitationValidator` class | P1 | [ ] | [S] | P2-037 | Extends BaseValidator |
| P2-039 | Implement Rule: citation-not-in-bib | P1 | [ ] | [S] | P2-038 | \cite{} not in .bib |
| P2-040 | Implement Rule: doi-missing | P2 | [ ] | [S] | P2-039 | Warning if DOI absent |
| P2-041 | Create `fixtures/valid/citation_valid.tex` | P1 | [ ] | [P] | P2-037 | No issues expected |
| P2-042 | Create `fixtures/invalid/citation_invalid.tex` | P1 | [ ] | [P] | P2-037 | Known issues |
| P2-043 | Create `bc_engine/tests/test_citation_validator.py` | P1 | [ ] | [S] | P2-040 | All rules tested |

### 2.6 Phase 2 Integration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P2-044 | Create `bc_engine/validators/__init__.py` exports | P0 | [ ] | [S] | All P2 validators | All validators exported |
| P2-045 | Create `bc_engine/tests/test_integration.py` | P0 | [ ] | [S] | P2-044 | All validators work together |
| P2-046 | Verify overall 90%+ test coverage | P0 | [ ] | [S] | P2-045 | Coverage report |
| P2-047 | Document Phase 2 completion | P1 | [ ] | [S] | P2-046 | CHANGELOG entry |

---

## Phase 3: BC Skill Updates

**Objective:** Embed QA rules into all BC skills
**Duration:** 3 days
**Blocking:** Must complete before Phase 4

### 3.1 bc-Hrari-content-style Update [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-001 | Relocate bc-Hrari-content-style from bc-math/ | P0 | [ ] | - | Phase 2 | Exists at skills root |
| P3-002 | Update references in ACADEMIC_BOOK_WORKFLOW.md | P0 | [ ] | [S] | P3-001 | No broken references |
| P3-003 | Update references in doc-book-from-text.md | P0 | [ ] | [S] | P3-001 | No broken references |
| P3-004 | Add QA rules section to skill.md | P0 | [ ] | [S] | P3-001 | All BiDi rules embedded |
| P3-005 | Add pre-validation checklist | P0 | [ ] | [S] | P3-004 | Checklist in skill.md |
| P3-006 | Link to content_validator.py | P0 | [ ] | [S] | P3-005, P2-010 | Validator path in skill.md |

### 3.2 bc-code Skill Update [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-007 | Add QA rules section to bc-code/skill.md | P0 | [ ] | [P] | Phase 2 | Code QA rules embedded |
| P3-008 | Add pre-validation checklist to bc-code | P0 | [ ] | [S] | P3-007 | Checklist in skill.md |
| P3-009 | Link to code_validator.py | P0 | [ ] | [S] | P3-008, P2-020 | Validator path in skill.md |
| P3-010 | Create LaTeX templates for bc-code | P1 | [ ] | [P] | P3-007 | pythonbox template |

### 3.3 bc-drawing Skill Completion [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-011 | Complete bc-drawing/skill.md with all rules | P0 | [ ] | [P] | Phase 2 | All TikZ rules documented |
| P3-012 | Add template examples to bc-drawing | P0 | [ ] | [S] | P3-011 | 3+ diagram templates |
| P3-013 | Link to tikz_validator.py | P0 | [ ] | [S] | P3-012, P2-029 | Validator path in skill.md |
| P3-014 | Create bc-drawing/templates/ directory | P1 | [ ] | [P] | P3-011 | Directory with .tex templates |

### 3.4 bc-math Skill Update [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-015 | Add QA rules section to bc-math/skill.md | P1 | [ ] | [P] | Phase 2 | Math QA rules embedded |
| P3-016 | Add BiDi detection rules for \hebmath | P1 | [ ] | [S] | P3-015 | Hebrew in math mode rules |
| P3-017 | Add pre-validation checklist to bc-math | P1 | [ ] | [S] | P3-016 | Checklist in skill.md |

### 3.5 bc-academic-source Skill Update [P1]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-018 | Add QA rules section to bc-academic-source | P1 | [ ] | [P] | Phase 2 | Table & citation rules |
| P3-019 | Link to table_validator.py | P1 | [ ] | [S] | P3-018, P2-036 | Validator path in skill.md |
| P3-020 | Link to citation_validator.py | P1 | [ ] | [S] | P3-019, P2-043 | Validator path in skill.md |
| P3-021 | Create LaTeX templates for tables | P1 | [ ] | [P] | P3-018 | rtltabular template |

### 3.6 BC Orchestration Setup [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-022 | Create bc-orchestration/ directory | P0 | [ ] | [S] | P3-001 to P3-021 | Directory exists |
| P3-023 | Create BC-CLAUDE.md coordination doc | P0 | [ ] | [S] | P3-022 | Architecture documented |
| P3-024 | Create bc_setup.json schema | P0 | [ ] | [S] | P3-023 | Valid JSON schema |
| P3-025 | Create BC-TASKS.md template | P0 | [ ] | [S] | P3-024 | Task tracking format |

### 3.7 Phase 3 Integration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P3-026 | Update ACADEMIC_BOOK_WORKFLOW.md | P1 | [ ] | [S] | P3-025 | All skills referenced |
| P3-027 | Update doc-book-from-text.md | P1 | [ ] | [S] | P3-026 | Pipeline updated |
| P3-028 | Version bump all updated skills | P0 | [ ] | [S] | P3-027 | qa_rules_embedded: true |

---

## Phase 4: insert_bc_skill Meta-Skill

**Objective:** Create meta-skill for automated BC skill creation
**Duration:** 2 days
**Blocking:** Must complete before Phase 5

### 4.1 Directory and Templates [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P4-001 | Create insert_bc_skill/ directory | P0 | [ ] | - | Phase 3 | Directory exists |
| P4-002 | Create insert_bc_skill/templates/ directory | P0 | [ ] | [S] | P4-001 | Directory exists |
| P4-003 | Create skill_template.md | P0 | [ ] | [P] | P4-002 | Valid skill template |
| P4-004 | Create validator_template.py | P0 | [ ] | [P] | P4-002 | Valid Python template |
| P4-005 | Create test_template.py | P0 | [ ] | [P] | P4-002 | Valid test template |

### 4.2 Meta-Skill Implementation [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P4-006 | Create insert_bc_skill/skill.md | P0 | [ ] | [S] | P4-003 to P4-005 | Skill definition |
| P4-007 | Implement CREATE mode logic | P0 | [ ] | [S] | P4-006 | Generates new skill |
| P4-008 | Implement EMBED-QA mode logic | P1 | [ ] | [S] | P4-007 | Adds QA rules to existing |
| P4-009 | Implement ADD-VALIDATOR mode logic | P1 | [ ] | [S] | P4-008 | Adds Python validator |

### 4.3 Testing and Documentation [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P4-010 | Test CREATE mode with sample skill | P0 | [ ] | [S] | P4-009 | New skill created |
| P4-011 | Test EMBED-QA mode | P1 | [ ] | [S] | P4-010 | QA rules added |
| P4-012 | Test ADD-VALIDATOR mode | P1 | [ ] | [S] | P4-011 | Validator created |
| P4-013 | Create insert_bc_skill/README.md | P0 | [ ] | [S] | P4-012 | Usage documented |

### 4.4 Phase 4 Integration [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P4-014 | Integration test: full skill creation | P0 | [ ] | [S] | P4-013 | End-to-end works |
| P4-015 | Document Phase 4 completion | P1 | [ ] | [S] | P4-014 | CHANGELOG entry |
| P4-016 | Update BC-CLAUDE.md with insert_bc_skill | P1 | [ ] | [S] | P4-015 | Architecture updated |

---

## Phase 5: Validation and Deployment

**Objective:** Validate complete system and prepare for deployment
**Duration:** 2 days
**All tasks BLOCKING for deployment**

### 5.1 QA Compliance Validation [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P5-001 | Generate sample chapter using bc-Hrari | P0 | [ ] | [P] | Phase 4 | Chapter generated |
| P5-002 | Generate code blocks using bc-code | P0 | [ ] | [P] | Phase 4 | Code blocks generated |
| P5-003 | Generate diagrams using bc-drawing | P0 | [ ] | [P] | Phase 4 | Diagrams generated |
| P5-004 | Run pre-validation on all generated content | P0 | [ ] | [S] | P5-001 to P5-003 | Pre-val report |
| P5-005 | Run qa-super on all generated content | P0 | [ ] | [S] | P5-004 | QA report |
| P5-006 | Compare pre-validation vs QA results | P0 | [ ] | [S] | P5-005 | ≥95% match |
| P5-007 | Calculate QA pass rate | P0 | [ ] | [S] | P5-006 | ≥95% pass |

### 5.2 Final Documentation [P0] [B]

| ID | Task | Priority | Status | Parallel | Dependencies | Acceptance Criteria |
|----|------|----------|--------|----------|--------------|---------------------|
| P5-008 | Create bc_engine/CHANGELOG.md | P0 | [ ] | [P] | P5-007 | All changes documented |
| P5-009 | Create bc_engine/README.md | P0 | [ ] | [P] | P5-007 | Usage documented |
| P5-010 | Run full test suite | P0 | [ ] | [S] | P5-008, P5-009 | 100% pass |
| P5-011 | Final review and sign-off | P0 | [ ] | [S] | P5-010 | Project complete |

---

## Execution Summary by Parallel Groups

### Phase 0 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P0-002 to P0-006 (directories) | PARALLEL after P0-001 |
| B | P0-007 to P0-009 (config) | PARALLEL with A |
| C | P0-010 (init) | SEQUENTIAL after all |

### Phase 1 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P1-002, P1-003 (exceptions, constants) | PARALLEL after P1-001 |
| B | P1-004 to P1-009 (base_validator) | SEQUENTIAL |
| C | P1-010 to P1-015 (template_engine) | PARALLEL with B |
| D | P1-016 to P1-020 (progress_tracker) | PARALLEL with B, C |
| E | P1-021 to P1-024 (controller) | SEQUENTIAL after B, C |
| F | P1-025 to P1-027 (integration) | SEQUENTIAL after all |

```
Day 1:
├── [PARALLEL] P1-001 → P1-002, P1-003
├── [PARALLEL] P1-004 → P1-005 to P1-009 (chain)
├── [PARALLEL] P1-010 → P1-011 to P1-015 (chain)
└── [PARALLEL] P1-016 → P1-017 to P1-020 (chain)

Day 2-3:
├── [SEQUENTIAL] P1-021 to P1-024 (controller, depends on B, C)
└── [SEQUENTIAL] P1-025 to P1-027 (integration, depends on all)
```

### Phase 2 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P2-001 to P2-010 (content_validator) | PARALLEL |
| B | P2-011 to P2-020 (code_validator) | PARALLEL with A |
| C | P2-021 to P2-029 (tikz_validator) | PARALLEL with A, B |
| D | P2-030 to P2-036 (table_validator) | PARALLEL with A, B, C |
| E | P2-037 to P2-043 (citation_validator) | PARALLEL with A, B, C, D |
| F | P2-044 to P2-047 (integration) | SEQUENTIAL after all |

```
Day 4-6 (HIGHLY PARALLEL):
┌────────────────┬────────────────┬────────────────┐
│  TRACK A       │  TRACK B       │  TRACK C       │
│  Content Val   │  Code Val      │  TikZ Val      │
├────────────────┼────────────────┼────────────────┤
│  P2-001        │  P2-011        │  P2-021        │
│  P2-002-006    │  P2-012-016    │  P2-022-025    │
│  P2-007-008    │  P2-017-018    │  P2-026-027    │
│  P2-009-010    │  P2-019-020    │  P2-028-029    │
└────────────────┴────────────────┴────────────────┘
┌────────────────┬────────────────┐
│  TRACK D       │  TRACK E       │
│  Table Val     │  Citation Val  │
├────────────────┼────────────────┤
│  P2-030        │  P2-037        │
│  P2-031-033    │  P2-038-040    │
│  P2-034-035    │  P2-041-042    │
│  P2-036        │  P2-043        │
└────────────────┴────────────────┘

Day 7:
└── [SEQUENTIAL] P2-044 to P2-047 (integration)
```

### Phase 3 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P3-001 to P3-006 (bc-Hrari) | SEQUENTIAL (relocation first) |
| B | P3-007 to P3-010 (bc-code) | PARALLEL with A |
| C | P3-011 to P3-014 (bc-drawing) | PARALLEL with A, B |
| D | P3-015 to P3-017 (bc-math) | PARALLEL with A, B, C |
| E | P3-018 to P3-021 (bc-academic) | PARALLEL with A, B, C, D |
| F | P3-022 to P3-025 (orchestration) | SEQUENTIAL after A-E |
| G | P3-026 to P3-028 (integration) | SEQUENTIAL after F |

```
Day 8-9:
┌────────────────┬────────────────┬────────────────┐
│  TRACK A       │  TRACK B       │  TRACK C       │
│  bc-Hrari      │  bc-code       │  bc-drawing    │
├────────────────┼────────────────┼────────────────┤
│  P3-001        │  P3-007        │  P3-011        │
│  P3-002-003    │  P3-008-009    │  P3-012-013    │
│  P3-004-006    │  P3-010        │  P3-014        │
└────────────────┴────────────────┴────────────────┘
┌────────────────┬────────────────┐
│  TRACK D       │  TRACK E       │
│  bc-math       │  bc-academic   │
├────────────────┼────────────────┤
│  P3-015        │  P3-018        │
│  P3-016-017    │  P3-019-021    │
└────────────────┴────────────────┘

Day 10:
├── [SEQUENTIAL] P3-022 to P3-025 (orchestration setup)
└── [SEQUENTIAL] P3-026 to P3-028 (integration)
```

### Phase 4 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P4-003 to P4-005 (templates) | PARALLEL after P4-002 |
| B | P4-006 to P4-009 (implementation) | SEQUENTIAL |
| C | P4-010 to P4-013 (testing) | SEQUENTIAL after B |
| D | P4-014 to P4-016 (integration) | SEQUENTIAL after C |

```
Day 11:
├── [SEQUENTIAL] P4-001 → P4-002
├── [PARALLEL] P4-003, P4-004, P4-005 (templates)
└── [SEQUENTIAL] P4-006 to P4-009 (implementation)

Day 12:
├── [SEQUENTIAL] P4-010 to P4-013 (testing)
└── [SEQUENTIAL] P4-014 to P4-016 (integration)
```

### Phase 5 Parallel Groups

| Group | Tasks | Execution |
|-------|-------|-----------|
| A | P5-001 to P5-003 (generation) | PARALLEL |
| B | P5-004 to P5-007 (validation) | SEQUENTIAL after A |
| C | P5-008, P5-009 (docs) | PARALLEL after B |
| D | P5-010, P5-011 (final) | SEQUENTIAL after C |

```
Day 13:
├── [PARALLEL] P5-001, P5-002, P5-003 (generate content)
└── [SEQUENTIAL] P5-004 to P5-007 (validation chain)

Day 14:
├── [PARALLEL] P5-008, P5-009 (documentation)
└── [SEQUENTIAL] P5-010, P5-011 (final review)
```

---

## Progress Tracking

### Overall Progress

| Phase | Total Tasks | Completed | Progress |
|-------|-------------|-----------|----------|
| Phase 0 | 10 | 0 | 0% |
| Phase 1 | 27 | 0 | 0% |
| Phase 2 | 47 | 0 | 0% |
| Phase 3 | 28 | 0 | 0% |
| Phase 4 | 16 | 0 | 0% |
| Phase 5 | 11 | 0 | 0% |
| **TOTAL** | **139** | **0** | **0%** |

### Critical Path

The critical path (longest sequential chain) is:

```
P0-001 → P1-001 → P1-005 → P1-009 → P2-001 → P2-010 → P3-001 → P3-006 →
P3-022 → P3-028 → P4-001 → P4-014 → P5-001 → P5-007 → P5-011
```

**Total critical path tasks:** 15
**Estimated critical path duration:** 14 days

---

## Dependencies Graph

```
Phase 0 ─────────────────────────────────────────────────────────────►
    │
    └──► Phase 1 (Foundation) ─────────────────────────────────────►
              │
              ├──► P1-009 (base_validator tests) ─┐
              │                                    │
              ├──► P1-015 (template_engine tests)──┼──► P1-021 (controller)
              │                                    │
              └──► P1-020 (progress_tracker)──────┘
                                                   │
                                                   ▼
         Phase 2 (Validators) ◄────────────────────┘
              │
              ├──► P2-010 (content_validator) ─────┐
              │                                     │
              ├──► P2-020 (code_validator) ────────┼──► Phase 3
              │                                     │
              ├──► P2-029 (tikz_validator) ────────┤
              │                                     │
              ├──► P2-036 (table_validator) ───────┤
              │                                     │
              └──► P2-043 (citation_validator) ────┘
                                                    │
                                                    ▼
         Phase 3 (Skill Updates) ◄──────────────────┘
              │
              └──► P3-028 (version bump all) ──────► Phase 4
                                                     │
                                                     ▼
         Phase 4 (insert_bc_skill) ◄─────────────────┘
              │
              └──► P4-016 (BC-CLAUDE update) ──────► Phase 5
                                                     │
                                                     ▼
         Phase 5 (Validation) ◄──────────────────────┘
              │
              └──► P5-011 (Final sign-off) ──────► COMPLETE
```

---

## Acceptance Criteria Summary

### Phase Completion Requirements

| Phase | Acceptance Criteria |
|-------|---------------------|
| Phase 0 | All directories exist, pytest runs |
| Phase 1 | All modules import, base tests pass |
| Phase 2 | All validators 90%+ coverage |
| Phase 3 | All BC skills have qa_rules_embedded: true |
| Phase 4 | insert_bc_skill creates valid skills |
| Phase 5 | QA pass rate ≥95%, all tests pass |

### Quality Gates

| Gate | Requirement | Verification |
|------|-------------|--------------|
| Unit Test Coverage | ≥90% | pytest --cov |
| QA Compliance | ≥95% pass rate | qa-super run |
| Pre-validation Accuracy | ≥95% match with QA | Compare reports |
| Documentation | All skills documented | Manual review |

---

## Notes

1. **Parallel execution** maximized in Phase 2 (5 validators can run simultaneously)
2. **Phase gates** must be respected - do not start next phase until current complete
3. **Test coverage** requirement is 90%+ for all Python validators
4. **QA compliance** must reach 95%+ before Phase 5 sign-off
5. **Critical path** is 15 tasks over 14 days - any delay impacts timeline
6. **Highest parallelization** is in Phase 2 Day 4-6 with 5 parallel tracks

---

*End of TODO List*
