# Implementation Plan - BC Skill Python Base System

**Document Version:** 1.0.0
**Date:** 2025-12-22
**Reference PRD:** PRD-BC-SKILL-PYTHON-BASE.md
**Reference Report:** BC-CLAUDE-MECHANISM-ARCHITECTURE-REPORT.md
**Status:** Ready for Execution

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Phase Breakdown](#3-phase-breakdown)
4. [Parallel Execution Map](#4-parallel-execution-map)
5. [Detailed Task List](#5-detailed-task-list)
6. [Testing Strategy](#6-testing-strategy)
7. [Deployment Strategy](#7-deployment-strategy)
8. [Validation Checkpoints](#8-validation-checkpoints)
9. [Risk Mitigation Plan](#9-risk-mitigation-plan)
10. [Resource Requirements](#10-resource-requirements)

---

## 1. Executive Summary

### 1.1 Objective

Transform the BC (Book Creator) mechanism from a "generate → fail QA → fix" cycle to a "generate correctly → pass QA" flow by:

1. Embedding QA compliance rules into all BC content creation skills
2. Creating Python pre-validation tools
3. Building template engine for deterministic patterns
4. Implementing BC orchestration engine
5. Creating `insert_bc_skill` meta-skill

### 1.2 Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| QA pass rate (first run) | ~60% | 95%+ |
| Token usage per chapter | ~8,000 | ~5,000 |
| Skills with QA rules | 12.5% (1/8) | 100% |
| Pre-validation coverage | 0% | 80%+ |

### 1.3 Timeline Overview

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | 3 days | Foundation (bc_engine core) |
| Phase 2 | 4 days | Python Validators |
| Phase 3 | 3 days | BC Skill Updates |
| Phase 4 | 2 days | insert_bc_skill |
| Phase 5 | 2 days | Validation & Polish |
| **Total** | **14 days** | |

---

## 2. Architecture Overview

### 2.1 System Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BC MECHANISM ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    ORCHESTRATION LAYER                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │  │ bc_setup.json│  │BC Controller │  │Progress Track│           │    │
│  │  │ (Config)     │  │ (Python)     │  │ (Python)     │           │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│  ┌─────────────────────────────────┴───────────────────────────────┐    │
│  │                    BC SKILLS LAYER (Updated)                     │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │    │
│  │  │bc-content  │ │bc-drawing  │ │bc-code     │ │bc-academic │    │    │
│  │  │+QA Rules   │ │+QA Rules   │ │+QA Rules   │ │+QA Rules   │    │    │
│  │  │+Validator  │ │+Validator  │ │+Validator  │ │+Validator  │    │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│  ┌─────────────────────────────────┴───────────────────────────────┐    │
│  │                    PYTHON TOOLS LAYER                            │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │    │
│  │  │Content     │ │TikZ        │ │Code        │ │Table       │    │    │
│  │  │Validator   │ │Validator   │ │Validator   │ │Validator   │    │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │    │
│  │  ┌────────────┐ ┌────────────┐                                   │    │
│  │  │Template    │ │Citation    │                                   │    │
│  │  │Engine      │ │Validator   │                                   │    │
│  │  └────────────┘ └────────────┘                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   BC Skill   │────►│ Pre-Validate │────►│   Compile    │────►│   QA Super   │
│ (with QA     │     │   (Python)   │     │   (LaTeX)    │     │   (Verify)   │
│  rules)      │     │              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                                         │
       │                    │ Issues?                                 │
       │                    ▼                                         │
       │             ┌──────────────┐                                 │
       └────────────►│  Fix Before  │◄────────────────────────────────┘
                     │  Compile     │     (Rarely needed with
                     └──────────────┘      embedded QA rules)
```

### 2.3 Directory Structure (Target)

```
skill-python-base/
├── .claude/
│   └── skills/
│       ├── bc-orchestration/
│       │   ├── BC-CLAUDE.md
│       │   ├── BC-TASKS.md
│       │   └── bc_setup.json
│       │
│       ├── bc-source-research/
│       │   └── skill.md
│       │
│       ├── bc-Hrari-content-style/     # RELOCATED
│       │   ├── skill.md                # Updated with QA rules
│       │   ├── validate_content.py
│       │   ├── test_validate.py
│       │   ├── templates/
│       │   └── fixtures/
│       │
│       ├── bc-drawing/
│       │   ├── skill.md                # Updated
│       │   ├── validate_tikz_bidi.py   # EXISTS
│       │   ├── test_validate.py
│       │   └── templates/
│       │
│       ├── bc-code/
│       │   ├── skill.md                # Updated with QA rules
│       │   ├── validate_code.py
│       │   ├── test_validate.py
│       │   └── templates/
│       │
│       ├── bc-math/
│       │   ├── skill.md                # Updated with QA rules
│       │   └── validate_math.py
│       │
│       ├── bc-academic-source/
│       │   ├── skill.md                # Updated with QA rules
│       │   ├── validate_tables.py
│       │   ├── validate_citations.py
│       │   └── templates/
│       │
│       ├── bc-architect/
│       │   └── skill.md
│       │
│       ├── bc-hebrew/
│       │   └── skill.md
│       │
│       └── insert_bc_skill/
│           ├── skill.md
│           └── templates/
│
├── bc_engine/
│   ├── __init__.py
│   ├── controller.py
│   ├── progress_tracker.py
│   ├── template_engine.py
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── base_validator.py
│   │   ├── content_validator.py
│   │   ├── code_validator.py
│   │   ├── tikz_validator.py
│   │   ├── table_validator.py
│   │   └── citation_validator.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_content_validator.py
│       ├── test_code_validator.py
│       ├── test_tikz_validator.py
│       ├── test_table_validator.py
│       └── test_citation_validator.py
│
├── fixtures/
│   ├── valid/
│   │   ├── chapter_valid.tex
│   │   ├── code_valid.tex
│   │   ├── tikz_valid.tex
│   │   └── table_valid.tex
│   └── invalid/
│       ├── chapter_invalid.tex
│       ├── code_invalid.tex
│       ├── tikz_invalid.tex
│       └── table_invalid.tex
│
└── docs/
    ├── BC-CLAUDE.md
    └── VALIDATOR-API.md
```

---

## 3. Phase Breakdown

### Phase 1: Foundation (Days 1-3)

**Objective:** Build the core bc_engine infrastructure.

#### Day 1: Base Infrastructure

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P1-001 | Create bc_engine/ directory structure | P0 | 30min | None |
| P1-002 | Create `__init__.py` files | P0 | 15min | P1-001 |
| P1-003 | Implement `base_validator.py` | P0 | 2hr | P1-002 |
| P1-004 | Create ValidationIssue dataclass | P0 | 30min | P1-003 |
| P1-005 | Create Severity enum | P0 | 15min | P1-003 |

#### Day 2: Template Engine & Progress Tracker

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P1-006 | Implement `template_engine.py` | P0 | 2hr | P1-002 |
| P1-007 | Create builtin templates dict | P0 | 1hr | P1-006 |
| P1-008 | Implement `progress_tracker.py` | P1 | 2hr | P1-002 |
| P1-009 | Create BC-TASKS.md format | P1 | 1hr | P1-008 |

#### Day 3: Configuration & Controller

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P1-010 | Create `bc_setup.json` schema | P0 | 1hr | None |
| P1-011 | Create bc-orchestration/ directory | P0 | 15min | P1-010 |
| P1-012 | Implement `controller.py` (basic) | P0 | 2hr | P1-003, P1-006, P1-008 |
| P1-013 | Write Phase 1 tests | P0 | 2hr | All P1-* |

**Phase 1 Deliverables:**
- [ ] bc_engine/ package with base_validator.py
- [ ] template_engine.py with builtin templates
- [ ] progress_tracker.py with BC-TASKS.md support
- [ ] controller.py (basic version)
- [ ] bc_setup.json schema and default config
- [ ] All Phase 1 tests passing

---

### Phase 2: Python Validators (Days 4-7)

**Objective:** Create all Python pre-validation tools.

#### Day 4: Content Validator

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P2-001 | Implement `content_validator.py` | P0 | 3hr | P1-003 |
| P2-002 | Add Rule: number-not-wrapped | P0 | 30min | P2-001 |
| P2-003 | Add Rule: english-not-wrapped | P0 | 30min | P2-001 |
| P2-004 | Add Rule: acronym-not-wrapped | P0 | 30min | P2-001 |
| P2-005 | Add Rule: figure-not-referenced | P1 | 1hr | P2-001 |
| P2-006 | Create content test fixtures | P0 | 1hr | P2-001 |
| P2-007 | Write content validator tests | P0 | 1hr | P2-001, P2-006 |

#### Day 5: Code Validator

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P2-008 | Implement `code_validator.py` | P0 | 2hr | P1-003 |
| P2-009 | Add Rule: hebrew-in-comment | P0 | 30min | P2-008 |
| P2-010 | Add Rule: code-no-english-wrapper | P0 | 30min | P2-008 |
| P2-011 | Add Rule: code-too-long | P1 | 30min | P2-008 |
| P2-012 | Create code test fixtures | P0 | 1hr | P2-008 |
| P2-013 | Write code validator tests | P0 | 1hr | P2-008, P2-012 |

#### Day 6: TikZ & Table Validators

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P2-014 | Migrate existing validate_tikz_bidi.py | P0 | 1hr | P1-003 |
| P2-015 | Create TikZ test fixtures | P0 | 30min | P2-014 |
| P2-016 | Write TikZ validator tests | P0 | 1hr | P2-014, P2-015 |
| P2-017 | Implement `table_validator.py` | P1 | 2hr | P1-003 |
| P2-018 | Add Rule: column-order-wrong | P1 | 1hr | P2-017 |
| P2-019 | Add Rule: cell-not-wrapped | P1 | 30min | P2-017 |
| P2-020 | Create table test fixtures | P1 | 1hr | P2-017 |
| P2-021 | Write table validator tests | P1 | 1hr | P2-017, P2-020 |

#### Day 7: Citation Validator & Integration

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P2-022 | Implement `citation_validator.py` | P1 | 2hr | P1-003 |
| P2-023 | Add Rule: citation-not-in-bib | P1 | 1hr | P2-022 |
| P2-024 | Add Rule: doi-missing | P2 | 30min | P2-022 |
| P2-025 | Create citation test fixtures | P1 | 1hr | P2-022 |
| P2-026 | Write citation validator tests | P1 | 1hr | P2-022, P2-025 |
| P2-027 | Create validators/__init__.py exports | P0 | 30min | All P2-* |
| P2-028 | Write integration tests | P0 | 2hr | All P2-* |

**Phase 2 Deliverables:**
- [ ] content_validator.py with 4+ rules
- [ ] code_validator.py with 3+ rules
- [ ] tikz_validator.py migrated and tested
- [ ] table_validator.py with 2+ rules
- [ ] citation_validator.py with 2+ rules
- [ ] All test fixtures created
- [ ] 90%+ test coverage for validators

---

### Phase 3: BC Skill Updates (Days 8-10)

**Objective:** Embed QA rules into all BC skills.

#### Day 8: Core Content Skills

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P3-001 | Relocate bc-Hrari-content-style | P0 | 30min | None |
| P3-002 | Update references to new location | P0 | 30min | P3-001 |
| P3-003 | Add QA rules to bc-Hrari-content-style | P0 | 2hr | P3-001 |
| P3-004 | Add pre-validation checklist | P0 | 30min | P3-003 |
| P3-005 | Link validator to skill | P0 | 30min | P3-003, P2-001 |
| P3-006 | Add QA rules to bc-code | P0 | 1hr | None |
| P3-007 | Add pre-validation checklist to bc-code | P0 | 30min | P3-006 |
| P3-008 | Link code validator to bc-code | P0 | 30min | P3-006, P2-008 |

#### Day 9: Visual & Technical Skills

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P3-009 | Complete bc-drawing skill.md | P0 | 1hr | None |
| P3-010 | Add templates to bc-drawing | P0 | 2hr | P3-009 |
| P3-011 | Link TikZ validator to bc-drawing | P0 | 30min | P3-009, P2-014 |
| P3-012 | Add QA rules to bc-math | P1 | 1hr | None |
| P3-013 | Add BiDi detection rules to bc-math | P1 | 1hr | P3-012 |
| P3-014 | Add QA rules to bc-academic-source | P1 | 1hr | None |
| P3-015 | Link table validator to bc-academic-source | P1 | 30min | P3-014, P2-017 |
| P3-016 | Link citation validator to bc-academic-source | P1 | 30min | P3-014, P2-022 |

#### Day 10: Documentation & Templates

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P3-017 | Create BC-CLAUDE.md coordination doc | P0 | 2hr | All P3-* |
| P3-018 | Update ACADEMIC_BOOK_WORKFLOW.md | P1 | 1hr | All P3-* |
| P3-019 | Create LaTeX templates for bc-code | P1 | 1hr | P3-006 |
| P3-020 | Create LaTeX templates for bc-academic-source | P1 | 1hr | P3-014 |
| P3-021 | Update doc-book-from-text.md | P1 | 1hr | All P3-* |
| P3-022 | Version bump all updated skills | P0 | 30min | All P3-* |

**Phase 3 Deliverables:**
- [ ] bc-Hrari-content-style relocated and updated
- [ ] All 8 BC skills have QA rules embedded
- [ ] All skills have `qa_rules_embedded: true`
- [ ] BC-CLAUDE.md created
- [ ] All workflow documentation updated
- [ ] Templates created for code, drawing, tables

---

### Phase 4: insert_bc_skill (Days 11-12)

**Objective:** Create meta-skill for automated BC skill creation.

#### Day 11: Core Implementation

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P4-001 | Create insert_bc_skill/ directory | P0 | 15min | None |
| P4-002 | Create skill.md for insert_bc_skill | P0 | 2hr | P4-001 |
| P4-003 | Create skill_template.md | P0 | 1hr | P4-002 |
| P4-004 | Create validator_template.py | P0 | 1hr | P4-002 |
| P4-005 | Create test_template.py | P0 | 1hr | P4-002 |
| P4-006 | Implement create mode logic | P0 | 2hr | P4-003, P4-004, P4-005 |

#### Day 12: Additional Modes & Testing

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P4-007 | Implement embed-qa mode | P1 | 2hr | P4-002 |
| P4-008 | Implement add-validator mode | P1 | 2hr | P4-002 |
| P4-009 | Test create mode with sample skill | P0 | 1hr | P4-006 |
| P4-010 | Test embed-qa mode | P1 | 1hr | P4-007 |
| P4-011 | Test add-validator mode | P1 | 1hr | P4-008 |
| P4-012 | Document insert_bc_skill usage | P0 | 1hr | All P4-* |

**Phase 4 Deliverables:**
- [ ] insert_bc_skill/skill.md complete
- [ ] All 3 templates created
- [ ] Create mode working
- [ ] Embed-QA mode working
- [ ] Add-Validator mode working
- [ ] Usage documentation complete

---

### Phase 5: Validation & Polish (Days 13-14)

**Objective:** Validate the complete system and prepare for deployment.

#### Day 13: QA Compliance Validation

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P5-001 | Generate sample chapter using bc-Hrari | P0 | 1hr | Phase 3 |
| P5-002 | Run pre-validation on sample | P0 | 30min | P5-001, Phase 2 |
| P5-003 | Run qa-super on sample | P0 | 30min | P5-001 |
| P5-004 | Compare pre-validation vs QA results | P0 | 1hr | P5-002, P5-003 |
| P5-005 | Calculate QA pass rate | P0 | 30min | P5-003 |
| P5-006 | Generate code blocks using bc-code | P0 | 1hr | Phase 3 |
| P5-007 | Generate diagrams using bc-drawing | P0 | 1hr | Phase 3 |
| P5-008 | Run full QA on all generated content | P0 | 1hr | P5-006, P5-007 |

#### Day 14: Final Polish & Documentation

| Task ID | Task | Priority | Effort | Dependencies |
|---------|------|----------|--------|--------------|
| P5-009 | Fix any issues found in P5-004 | P0 | 2hr | P5-004 |
| P5-010 | Re-run validation to confirm 95% pass | P0 | 1hr | P5-009 |
| P5-011 | Calculate token reduction metrics | P1 | 1hr | P5-008 |
| P5-012 | Run full test suite | P0 | 30min | All phases |
| P5-013 | Generate test coverage report | P0 | 30min | P5-012 |
| P5-014 | Create CHANGELOG.md | P0 | 1hr | All phases |
| P5-015 | Create README.md for bc_engine | P0 | 1hr | All phases |
| P5-016 | Final review and sign-off | P0 | 1hr | All P5-* |

**Phase 5 Deliverables:**
- [ ] QA pass rate ≥95% verified
- [ ] Pre-validation matches QA detection ≥95%
- [ ] Token reduction ≥30% verified
- [ ] All tests passing (100%)
- [ ] Test coverage ≥90%
- [ ] CHANGELOG.md created
- [ ] README.md created
- [ ] System ready for deployment

---

## 4. Parallel Execution Map

### 4.1 Phase 1 Parallelization

```
Day 1:
├── [PARALLEL] P1-001: Create directory structure
├── [PARALLEL] P1-002: Create __init__.py files (after P1-001)
└── [SEQUENTIAL] P1-003, P1-004, P1-005: Base validator (chain)

Day 2:
├── [PARALLEL] P1-006, P1-007: Template engine
└── [PARALLEL] P1-008, P1-009: Progress tracker

Day 3:
├── [PARALLEL] P1-010, P1-011: Configuration
└── [SEQUENTIAL] P1-012: Controller (depends on Day 1-2)
└── [SEQUENTIAL] P1-013: Tests (depends on all)
```

### 4.2 Phase 2 Parallelization

```
Day 4-7 Parallel Tracks:

TRACK A (Content):          TRACK B (Code):           TRACK C (Visual):
├── P2-001: content_val     ├── P2-008: code_val      ├── P2-014: tikz_val
├── P2-002: rule 1          ├── P2-009: rule 1        ├── P2-015: fixtures
├── P2-003: rule 2          ├── P2-010: rule 2        └── P2-016: tests
├── P2-004: rule 3          ├── P2-011: rule 3
├── P2-005: rule 4          ├── P2-012: fixtures      TRACK D (Tables):
├── P2-006: fixtures        └── P2-013: tests         ├── P2-017: table_val
└── P2-007: tests                                     ├── P2-018: rule 1
                                                      ├── P2-019: rule 2
                            TRACK E (Citations):      ├── P2-020: fixtures
                            ├── P2-022: cite_val      └── P2-021: tests
                            ├── P2-023: rule 1
                            ├── P2-024: rule 2
                            ├── P2-025: fixtures
                            └── P2-026: tests

[SEQUENTIAL - End of Day 7]
└── P2-027: exports
└── P2-028: integration tests
```

### 4.3 Phase 3 Parallelization

```
Day 8-10 Parallel Tracks:

TRACK A (Content Skills):   TRACK B (Code Skills):    TRACK C (Visual Skills):
├── P3-001: relocate        ├── P3-006: add rules     ├── P3-009: complete
├── P3-002: update refs     ├── P3-007: checklist     ├── P3-010: templates
├── P3-003: add rules       └── P3-008: link val      └── P3-011: link val
├── P3-004: checklist
└── P3-005: link val        TRACK D (Technical):      TRACK E (Academic):
                            ├── P3-012: math rules    ├── P3-014: source rules
                            └── P3-013: BiDi rules    ├── P3-015: link table
                                                      └── P3-016: link cite

[SEQUENTIAL - Day 10]
├── P3-017: BC-CLAUDE.md
├── P3-018: workflow docs
├── P3-019-P3-020: templates
├── P3-021: command docs
└── P3-022: version bump
```

### 4.4 Phase 4 Parallelization

```
Day 11:
├── [PARALLEL] P4-003: skill_template.md
├── [PARALLEL] P4-004: validator_template.py
├── [PARALLEL] P4-005: test_template.py
└── [SEQUENTIAL] P4-006: create mode (depends on templates)

Day 12:
├── [PARALLEL] P4-007: embed-qa mode
├── [PARALLEL] P4-008: add-validator mode
└── [SEQUENTIAL] P4-009, P4-010, P4-011: testing
└── [SEQUENTIAL] P4-012: documentation
```

### 4.5 Phase 5 Parallelization

```
Day 13:
├── [PARALLEL] P5-001: generate chapter
├── [PARALLEL] P5-006: generate code
├── [PARALLEL] P5-007: generate diagrams
└── [SEQUENTIAL] P5-002, P5-003, P5-004, P5-005: validation (after generation)
└── [SEQUENTIAL] P5-008: full QA (after all generation)

Day 14:
├── [SEQUENTIAL] P5-009: fix issues (if any)
├── [SEQUENTIAL] P5-010: re-validate
├── [PARALLEL] P5-011: metrics
├── [PARALLEL] P5-012, P5-013: test suite
├── [PARALLEL] P5-014, P5-015: documentation
└── [SEQUENTIAL] P5-016: final review
```

---

## 5. Detailed Task List

### 5.1 Complete Task Table

| ID | Phase | Task | Priority | Effort | Deps | Parallel? |
|----|-------|------|----------|--------|------|-----------|
| **Phase 1: Foundation** |
| P1-001 | 1 | Create bc_engine/ directory structure | P0 | 30m | - | Yes |
| P1-002 | 1 | Create `__init__.py` files | P0 | 15m | P1-001 | Yes |
| P1-003 | 1 | Implement `base_validator.py` | P0 | 2h | P1-002 | No |
| P1-004 | 1 | Create ValidationIssue dataclass | P0 | 30m | P1-003 | No |
| P1-005 | 1 | Create Severity enum | P0 | 15m | P1-003 | No |
| P1-006 | 1 | Implement `template_engine.py` | P0 | 2h | P1-002 | Yes |
| P1-007 | 1 | Create builtin templates dict | P0 | 1h | P1-006 | Yes |
| P1-008 | 1 | Implement `progress_tracker.py` | P1 | 2h | P1-002 | Yes |
| P1-009 | 1 | Create BC-TASKS.md format | P1 | 1h | P1-008 | Yes |
| P1-010 | 1 | Create `bc_setup.json` schema | P0 | 1h | - | Yes |
| P1-011 | 1 | Create bc-orchestration/ directory | P0 | 15m | P1-010 | Yes |
| P1-012 | 1 | Implement `controller.py` (basic) | P0 | 2h | P1-003,P1-006,P1-008 | No |
| P1-013 | 1 | Write Phase 1 tests | P0 | 2h | All P1 | No |
| **Phase 2: Validators** |
| P2-001 | 2 | Implement `content_validator.py` | P0 | 3h | P1-003 | Yes |
| P2-002 | 2 | Add Rule: number-not-wrapped | P0 | 30m | P2-001 | No |
| P2-003 | 2 | Add Rule: english-not-wrapped | P0 | 30m | P2-001 | No |
| P2-004 | 2 | Add Rule: acronym-not-wrapped | P0 | 30m | P2-001 | No |
| P2-005 | 2 | Add Rule: figure-not-referenced | P1 | 1h | P2-001 | No |
| P2-006 | 2 | Create content test fixtures | P0 | 1h | P2-001 | Yes |
| P2-007 | 2 | Write content validator tests | P0 | 1h | P2-001,P2-006 | No |
| P2-008 | 2 | Implement `code_validator.py` | P0 | 2h | P1-003 | Yes |
| P2-009 | 2 | Add Rule: hebrew-in-comment | P0 | 30m | P2-008 | No |
| P2-010 | 2 | Add Rule: code-no-english-wrapper | P0 | 30m | P2-008 | No |
| P2-011 | 2 | Add Rule: code-too-long | P1 | 30m | P2-008 | No |
| P2-012 | 2 | Create code test fixtures | P0 | 1h | P2-008 | Yes |
| P2-013 | 2 | Write code validator tests | P0 | 1h | P2-008,P2-012 | No |
| P2-014 | 2 | Migrate existing validate_tikz_bidi.py | P0 | 1h | P1-003 | Yes |
| P2-015 | 2 | Create TikZ test fixtures | P0 | 30m | P2-014 | Yes |
| P2-016 | 2 | Write TikZ validator tests | P0 | 1h | P2-014,P2-015 | No |
| P2-017 | 2 | Implement `table_validator.py` | P1 | 2h | P1-003 | Yes |
| P2-018 | 2 | Add Rule: column-order-wrong | P1 | 1h | P2-017 | No |
| P2-019 | 2 | Add Rule: cell-not-wrapped | P1 | 30m | P2-017 | No |
| P2-020 | 2 | Create table test fixtures | P1 | 1h | P2-017 | Yes |
| P2-021 | 2 | Write table validator tests | P1 | 1h | P2-017,P2-020 | No |
| P2-022 | 2 | Implement `citation_validator.py` | P1 | 2h | P1-003 | Yes |
| P2-023 | 2 | Add Rule: citation-not-in-bib | P1 | 1h | P2-022 | No |
| P2-024 | 2 | Add Rule: doi-missing | P2 | 30m | P2-022 | No |
| P2-025 | 2 | Create citation test fixtures | P1 | 1h | P2-022 | Yes |
| P2-026 | 2 | Write citation validator tests | P1 | 1h | P2-022,P2-025 | No |
| P2-027 | 2 | Create validators/__init__.py exports | P0 | 30m | All P2 | No |
| P2-028 | 2 | Write integration tests | P0 | 2h | All P2 | No |
| **Phase 3: Skill Updates** |
| P3-001 | 3 | Relocate bc-Hrari-content-style | P0 | 30m | - | Yes |
| P3-002 | 3 | Update references to new location | P0 | 30m | P3-001 | No |
| P3-003 | 3 | Add QA rules to bc-Hrari-content-style | P0 | 2h | P3-001 | No |
| P3-004 | 3 | Add pre-validation checklist | P0 | 30m | P3-003 | No |
| P3-005 | 3 | Link validator to skill | P0 | 30m | P3-003,P2-001 | No |
| P3-006 | 3 | Add QA rules to bc-code | P0 | 1h | - | Yes |
| P3-007 | 3 | Add pre-validation checklist to bc-code | P0 | 30m | P3-006 | No |
| P3-008 | 3 | Link code validator to bc-code | P0 | 30m | P3-006,P2-008 | No |
| P3-009 | 3 | Complete bc-drawing skill.md | P0 | 1h | - | Yes |
| P3-010 | 3 | Add templates to bc-drawing | P0 | 2h | P3-009 | No |
| P3-011 | 3 | Link TikZ validator to bc-drawing | P0 | 30m | P3-009,P2-014 | No |
| P3-012 | 3 | Add QA rules to bc-math | P1 | 1h | - | Yes |
| P3-013 | 3 | Add BiDi detection rules to bc-math | P1 | 1h | P3-012 | No |
| P3-014 | 3 | Add QA rules to bc-academic-source | P1 | 1h | - | Yes |
| P3-015 | 3 | Link table validator to bc-academic-source | P1 | 30m | P3-014,P2-017 | No |
| P3-016 | 3 | Link citation validator to bc-academic-source | P1 | 30m | P3-014,P2-022 | No |
| P3-017 | 3 | Create BC-CLAUDE.md coordination doc | P0 | 2h | All P3 | No |
| P3-018 | 3 | Update ACADEMIC_BOOK_WORKFLOW.md | P1 | 1h | All P3 | No |
| P3-019 | 3 | Create LaTeX templates for bc-code | P1 | 1h | P3-006 | Yes |
| P3-020 | 3 | Create LaTeX templates for bc-academic-source | P1 | 1h | P3-014 | Yes |
| P3-021 | 3 | Update doc-book-from-text.md | P1 | 1h | All P3 | No |
| P3-022 | 3 | Version bump all updated skills | P0 | 30m | All P3 | No |
| **Phase 4: insert_bc_skill** |
| P4-001 | 4 | Create insert_bc_skill/ directory | P0 | 15m | - | Yes |
| P4-002 | 4 | Create skill.md for insert_bc_skill | P0 | 2h | P4-001 | No |
| P4-003 | 4 | Create skill_template.md | P0 | 1h | P4-002 | Yes |
| P4-004 | 4 | Create validator_template.py | P0 | 1h | P4-002 | Yes |
| P4-005 | 4 | Create test_template.py | P0 | 1h | P4-002 | Yes |
| P4-006 | 4 | Implement create mode logic | P0 | 2h | P4-003,P4-004,P4-005 | No |
| P4-007 | 4 | Implement embed-qa mode | P1 | 2h | P4-002 | Yes |
| P4-008 | 4 | Implement add-validator mode | P1 | 2h | P4-002 | Yes |
| P4-009 | 4 | Test create mode with sample skill | P0 | 1h | P4-006 | No |
| P4-010 | 4 | Test embed-qa mode | P1 | 1h | P4-007 | No |
| P4-011 | 4 | Test add-validator mode | P1 | 1h | P4-008 | No |
| P4-012 | 4 | Document insert_bc_skill usage | P0 | 1h | All P4 | No |
| **Phase 5: Validation** |
| P5-001 | 5 | Generate sample chapter using bc-Hrari | P0 | 1h | Phase 3 | Yes |
| P5-002 | 5 | Run pre-validation on sample | P0 | 30m | P5-001,Phase 2 | No |
| P5-003 | 5 | Run qa-super on sample | P0 | 30m | P5-001 | No |
| P5-004 | 5 | Compare pre-validation vs QA results | P0 | 1h | P5-002,P5-003 | No |
| P5-005 | 5 | Calculate QA pass rate | P0 | 30m | P5-003 | No |
| P5-006 | 5 | Generate code blocks using bc-code | P0 | 1h | Phase 3 | Yes |
| P5-007 | 5 | Generate diagrams using bc-drawing | P0 | 1h | Phase 3 | Yes |
| P5-008 | 5 | Run full QA on all generated content | P0 | 1h | P5-006,P5-007 | No |
| P5-009 | 5 | Fix any issues found in P5-004 | P0 | 2h | P5-004 | No |
| P5-010 | 5 | Re-run validation to confirm 95% pass | P0 | 1h | P5-009 | No |
| P5-011 | 5 | Calculate token reduction metrics | P1 | 1h | P5-008 | Yes |
| P5-012 | 5 | Run full test suite | P0 | 30m | All phases | No |
| P5-013 | 5 | Generate test coverage report | P0 | 30m | P5-012 | No |
| P5-014 | 5 | Create CHANGELOG.md | P0 | 1h | All phases | Yes |
| P5-015 | 5 | Create README.md for bc_engine | P0 | 1h | All phases | Yes |
| P5-016 | 5 | Final review and sign-off | P0 | 1h | All P5 | No |

### 5.2 Task Summary by Priority

| Priority | Count | Total Effort |
|----------|-------|--------------|
| P0 (Critical) | 52 | ~60 hours |
| P1 (High) | 22 | ~22 hours |
| P2 (Medium) | 1 | ~0.5 hours |
| **Total** | **75** | **~82.5 hours** |

### 5.3 Task Summary by Phase

| Phase | Tasks | Effort | Days |
|-------|-------|--------|------|
| Phase 1: Foundation | 13 | ~14 hours | 3 |
| Phase 2: Validators | 28 | ~28 hours | 4 |
| Phase 3: Skill Updates | 22 | ~20 hours | 3 |
| Phase 4: insert_bc_skill | 12 | ~14 hours | 2 |
| Phase 5: Validation | 16 | ~14 hours | 2 |
| **Total** | **91** | **~90 hours** | **14** |

---

## 6. Testing Strategy

### 6.1 Test Categories

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TESTING PYRAMID                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                         ┌─────────────┐                                  │
│                         │  QA Compl.  │  ← Full QA run on BC output     │
│                         │   Tests     │                                  │
│                         └──────┬──────┘                                  │
│                    ┌───────────┴───────────┐                            │
│                    │   Integration Tests    │  ← Controller + Validators │
│                    └───────────┬───────────┘                            │
│           ┌────────────────────┴────────────────────┐                   │
│           │            Unit Tests                    │  ← Each validator │
│           └────────────────────┬────────────────────┘                   │
│  ┌─────────────────────────────┴─────────────────────────────┐          │
│  │                       Fixtures                             │          │
│  │   valid_*.tex (no issues)    invalid_*.tex (known issues) │          │
│  └───────────────────────────────────────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Unit Test Requirements

#### Base Validator Tests
```python
# bc_engine/tests/test_base_validator.py

def test_validation_issue_creation():
    """Test ValidationIssue dataclass."""
    pass

def test_severity_enum():
    """Test Severity enum values."""
    pass

def test_base_validator_interface():
    """Test abstract interface enforced."""
    pass
```

#### Content Validator Tests
```python
# bc_engine/tests/test_content_validator.py

class TestContentValidator:
    def test_detects_unwrapped_number(self):
        """Numbers in Hebrew must be wrapped."""
        content = "גרסה 0.5 של המערכת"
        issues = validator.validate(content, "test.tex")
        assert any(i.rule == 'number-not-wrapped' for i in issues)

    def test_allows_wrapped_number(self):
        """Wrapped numbers should pass."""
        content = r"גרסה \en{0.5} של המערכת"
        issues = validator.validate(content, "test.tex")
        assert not any(i.rule == 'number-not-wrapped' for i in issues)

    def test_detects_unwrapped_english(self):
        """English words in Hebrew must be wrapped."""
        pass

    def test_detects_unwrapped_acronym(self):
        """Acronyms in Hebrew must be wrapped."""
        pass

    def test_detects_unreferenced_figure(self):
        """All figures must be referenced in text."""
        pass
```

#### Code Validator Tests
```python
# bc_engine/tests/test_code_validator.py

class TestCodeValidator:
    def test_detects_hebrew_comment(self):
        """Hebrew in code comments is forbidden."""
        pass

    def test_allows_english_comment(self):
        """English comments should pass."""
        pass

    def test_detects_unwrapped_pythonbox(self):
        """pythonbox without english wrapper detected."""
        pass

    def test_detects_long_code(self):
        """Code blocks over 40 lines trigger warning."""
        pass
```

#### TikZ Validator Tests
```python
# bc_engine/tests/test_tikz_validator.py

class TestTikZValidator:
    def test_detects_tikz_without_english(self):
        """TikZ without english wrapper detected."""
        pass

    def test_detects_hebrew_in_tikz(self):
        """Hebrew chars in TikZ detected."""
        pass

    def test_allows_correct_tikz(self):
        """Properly wrapped TikZ passes."""
        pass
```

### 6.3 Integration Test Requirements

```python
# bc_engine/tests/test_integration.py

class TestIntegration:
    def test_all_validators_run(self):
        """All validators execute on sample document."""
        pass

    def test_controller_orchestration(self):
        """Controller coordinates validators correctly."""
        pass

    def test_pre_validation_matches_qa(self):
        """Pre-validation catches same issues as QA."""
        pass
```

### 6.4 QA Compliance Tests

```python
# bc_engine/tests/test_qa_compliance.py

class TestQACompliance:
    def test_generated_content_passes_qa(self):
        """Content from BC skills passes qa-super."""
        # Generate content using BC skills
        # Run qa-super
        # Assert 95%+ pass rate
        pass

    def test_pre_validation_accuracy(self):
        """Pre-validation catches 95%+ of QA issues."""
        pass
```

### 6.5 Test Fixtures

#### Valid Fixtures (Should Pass)
```latex
% fixtures/valid/chapter_valid.tex
\hebrewchapter{מבוא לבינה מלאכותית}

מערכות \en{AI} מודרניות כוללות \en{Machine Learning} ו\en{Deep Learning}.
בשנת \hebyear{2024}, הושקו מודלים עם \en{100} מיליארד פרמטרים.

% Valid figure with reference
כפי שניתן לראות באיור~\ref{fig:example}, המערכת מורכבת מ\en{3} שכבות.

\begin{figure}[htbp]
\centering
\begin{english}
\begin{tikzpicture}
\node {Input Layer};
\end{tikzpicture}
\end{english}
\caption{ארכיטקטורת המערכת}
\label{fig:example}
\end{figure}
```

#### Invalid Fixtures (Should Fail)
```latex
% fixtures/invalid/chapter_invalid.tex
\hebrewchapter{מבוא לבינה מלאכותית}

% ISSUE: Unwrapped numbers
מערכות AI מודרניות כוללות Machine Learning.
בשנת 2024, הושקו מודלים עם 100 מיליארד פרמטרים.

% ISSUE: Unreferenced figure
\begin{figure}[htbp]
\centering
% ISSUE: TikZ without english wrapper
\begin{tikzpicture}
% ISSUE: Hebrew in TikZ
\node {שכבת קלט};
\end{tikzpicture}
\caption{ארכיטקטורת המערכת}
\label{fig:example}
\end{figure}
```

### 6.6 Test Coverage Requirements

| Component | Target Coverage |
|-----------|-----------------|
| base_validator.py | 100% |
| content_validator.py | 95% |
| code_validator.py | 95% |
| tikz_validator.py | 95% |
| table_validator.py | 90% |
| citation_validator.py | 90% |
| template_engine.py | 90% |
| controller.py | 85% |
| **Overall** | **90%+** |

---

## 7. Deployment Strategy

### 7.1 Deployment Stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       DEPLOYMENT PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STAGE 1: Local Verification                                             │
│  ────────────────────────────                                           │
│  Location: skill-python-base/                                           │
│                                                                          │
│  ✓ All unit tests pass                                                  │
│  ✓ All integration tests pass                                           │
│  ✓ QA compliance ≥95%                                                   │
│  ✓ Test coverage ≥90%                                                   │
│                                                                          │
│                              ▼                                           │
│                                                                          │
│  STAGE 2: Backup Existing                                                │
│  ────────────────────────                                               │
│  Target: C:\Users\gal-t\.claude\skills-backup-YYYYMMDD\                 │
│                                                                          │
│  ✓ Backup all bc-* skills                                               │
│  ✓ Backup bc_engine/ (if exists)                                        │
│  ✓ Verify backup integrity                                              │
│                                                                          │
│                              ▼                                           │
│                                                                          │
│  STAGE 3: Deploy Skills                                                  │
│  ──────────────────────                                                 │
│  Target: C:\Users\gal-t\.claude\skills\                                 │
│                                                                          │
│  ✓ Copy all bc-* skills                                                 │
│  ✓ Copy bc-orchestration/                                               │
│  ✓ Copy insert_bc_skill/                                                │
│                                                                          │
│                              ▼                                           │
│                                                                          │
│  STAGE 4: Deploy Engine                                                  │
│  ──────────────────────                                                 │
│  Target: C:\Users\gal-t\.claude\bc_engine\                              │
│                                                                          │
│  ✓ Copy bc_engine/ package                                              │
│  ✓ Verify Python imports work                                           │
│                                                                          │
│                              ▼                                           │
│                                                                          │
│  STAGE 5: Post-Deploy Verification                                       │
│  ─────────────────────────────────                                      │
│                                                                          │
│  ✓ Run smoke tests                                                      │
│  ✓ Verify skill invocation works                                        │
│  ✓ Test with real chapter                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Deployment Commands

```bash
# Stage 1: Verify locally
cd C:\25D\GeneralLearning\skill-python-base
python -m pytest bc_engine/tests/ -v --cov=bc_engine --cov-report=term-missing

# Stage 2: Backup
$date = Get-Date -Format "yyyyMMdd"
Copy-Item -Recurse "C:\Users\gal-t\.claude\skills\bc-*" "C:\Users\gal-t\.claude\skills-backup-$date\"

# Stage 3: Deploy skills
Copy-Item -Recurse ".\.claude\skills\bc-*" "C:\Users\gal-t\.claude\skills\" -Force
Copy-Item -Recurse ".\.claude\skills\bc-orchestration" "C:\Users\gal-t\.claude\skills\" -Force
Copy-Item -Recurse ".\.claude\skills\insert_bc_skill" "C:\Users\gal-t\.claude\skills\" -Force

# Stage 4: Deploy engine
Copy-Item -Recurse ".\bc_engine" "C:\Users\gal-t\.claude\" -Force

# Stage 5: Verify
cd C:\Users\gal-t\.claude
python -c "from bc_engine import BCController; print('Import OK')"
```

### 7.3 Rollback Procedure

```bash
# Rollback to backup
$date = "YYYYMMDD"  # Use actual backup date
Remove-Item -Recurse "C:\Users\gal-t\.claude\skills\bc-*"
Copy-Item -Recurse "C:\Users\gal-t\.claude\skills-backup-$date\bc-*" "C:\Users\gal-t\.claude\skills\"
```

---

## 8. Validation Checkpoints

### 8.1 Phase 1 Checkpoint

| Criteria | Verification Method | Pass Condition |
|----------|---------------------|----------------|
| Directory structure | ls -R bc_engine/ | All dirs exist |
| Base validator | pytest test_base_validator.py | All tests pass |
| Template engine | pytest test_template_engine.py | All tests pass |
| Progress tracker | pytest test_progress_tracker.py | All tests pass |
| Controller basic | pytest test_controller.py | All tests pass |
| Config loading | python -c "import bc_setup" | No errors |

### 8.2 Phase 2 Checkpoint

| Criteria | Verification Method | Pass Condition |
|----------|---------------------|----------------|
| Content validator | pytest test_content_validator.py | All tests pass |
| Code validator | pytest test_code_validator.py | All tests pass |
| TikZ validator | pytest test_tikz_validator.py | All tests pass |
| Table validator | pytest test_table_validator.py | All tests pass |
| Citation validator | pytest test_citation_validator.py | All tests pass |
| Integration | pytest test_integration.py | All tests pass |
| Coverage | pytest --cov | ≥90% |

### 8.3 Phase 3 Checkpoint

| Criteria | Verification Method | Pass Condition |
|----------|---------------------|----------------|
| bc-content relocated | ls bc-Hrari-content-style/ | Exists at root |
| QA rules in all skills | grep "qa_rules_embedded" */skill.md | 8 matches |
| Pre-validation checklists | grep "Pre-Validation" */skill.md | 8 matches |
| BC-CLAUDE.md | cat BC-CLAUDE.md | Complete |
| Workflow updated | diff ACADEMIC_BOOK_WORKFLOW.md | Changes present |

### 8.4 Phase 4 Checkpoint

| Criteria | Verification Method | Pass Condition |
|----------|---------------------|----------------|
| insert_bc_skill exists | ls insert_bc_skill/skill.md | Exists |
| Templates exist | ls insert_bc_skill/templates/ | 3 files |
| Create mode works | /insert_bc_skill --mode=create test | Skill created |
| Embed-QA mode works | /insert_bc_skill --mode=embed-qa | Rules added |
| Add-validator mode works | /insert_bc_skill --mode=add-validator | Validator created |

### 8.5 Phase 5 Checkpoint (Final)

| Criteria | Verification Method | Pass Condition |
|----------|---------------------|----------------|
| QA pass rate | Run qa-super on BC output | ≥95% |
| Pre-val accuracy | Compare pre-val vs QA | ≥95% match |
| Token reduction | Count tokens | ≥30% reduction |
| All tests pass | pytest | 100% pass |
| Coverage | pytest --cov | ≥90% |
| Docs complete | Check CHANGELOG, README | Present |

---

## 9. Risk Mitigation Plan

### 9.1 Technical Risks

| Risk | Probability | Impact | Mitigation | Contingency |
|------|-------------|--------|------------|-------------|
| Pre-validation misses issues | Medium | High | Match QA regex exactly | Iterate on patterns |
| QA mechanism changes | Low | High | Version lock patterns | Update when QA changes |
| Template rendering issues | Low | Medium | Extensive testing | Fallback to LLM |
| Python import errors | Medium | Medium | Test imports early | Document dependencies |
| Performance degradation | Low | Medium | Benchmark early | Optimize hot paths |

### 9.2 Project Risks

| Risk | Probability | Impact | Mitigation | Contingency |
|------|-------------|--------|------------|-------------|
| Scope creep | High | Medium | Strict PRD adherence | Defer to v2 |
| 95% pass rate not achieved | Medium | High | Iterative improvement | Lower to 90% |
| Test coverage gaps | Medium | Medium | TDD approach | Add tests post-hoc |
| Integration breaks existing | Low | High | Extensive testing | Rollback |

### 9.3 Mitigation Actions by Phase

| Phase | Key Risks | Actions |
|-------|-----------|---------|
| Phase 1 | Foundation incomplete | Daily verification |
| Phase 2 | Regex patterns wrong | Compare with QA detect |
| Phase 3 | Skills break | Test each skill after update |
| Phase 4 | Templates malformed | Test all 3 modes |
| Phase 5 | QA rate below target | Allow buffer for fixes |

---

## 10. Resource Requirements

### 10.1 Development Environment

| Resource | Requirement |
|----------|-------------|
| Python | 3.10+ |
| Claude CLI | Latest |
| pytest | 7.x+ |
| pytest-cov | Latest |
| Git | Any |
| Editor | VS Code recommended |

### 10.2 Test Environment

| Resource | Requirement |
|----------|-------------|
| Sample LaTeX project | GenAI-Security-Cheat-Sheet |
| LuaLaTeX | MiKTeX installation |
| QA mechanism | Current qa-super working |

### 10.3 File Count Estimates

| Component | Files | Lines (est.) |
|-----------|-------|--------------|
| bc_engine/ core | 6 | ~600 |
| bc_engine/validators/ | 6 | ~900 |
| bc_engine/tests/ | 8 | ~800 |
| BC skills (updated) | 8 | ~1600 |
| insert_bc_skill | 4 | ~400 |
| Fixtures | 8 | ~400 |
| Documentation | 4 | ~600 |
| **Total** | **~44** | **~5300** |

---

## Appendix A: Quick Reference

### A.1 Key Commands

```bash
# Run all tests
python -m pytest bc_engine/tests/ -v

# Run with coverage
python -m pytest bc_engine/tests/ --cov=bc_engine --cov-report=html

# Validate single file
python -c "from bc_engine.validators import ContentValidator; v = ContentValidator(); print(v.validate(open('file.tex').read(), 'file.tex'))"

# Run pre-validation on project
python -m bc_engine.controller --validate path/to/project
```

### A.2 Key Files

| File | Purpose |
|------|---------|
| `bc_engine/validators/base_validator.py` | Base interface |
| `bc_engine/controller.py` | Main orchestrator |
| `bc_engine/template_engine.py` | Template rendering |
| `.claude/skills/bc-orchestration/bc_setup.json` | Configuration |
| `.claude/skills/bc-orchestration/BC-CLAUDE.md` | Coordination doc |

### A.3 Key Patterns

```python
# Validate content
from bc_engine.validators import ContentValidator
validator = ContentValidator()
issues = validator.validate(content, file_path)
if not issues:
    print("QA Compliant!")

# Render template
from bc_engine import TemplateEngine
engine = TemplateEngine()
latex = engine.render('pythonbox', {'title': 'Example', 'code': code})
```

---

## Appendix B: Approval Sign-Off

### Planning Approval

- [ ] Architecture reviewed
- [ ] Task list complete
- [ ] Dependencies mapped
- [ ] Parallel opportunities identified
- [ ] Testing strategy approved
- [ ] User approval obtained

**Approved by:** _________________
**Date:** _________________

### Phase Completion Sign-Offs

| Phase | Completed | Verified | Signed |
|-------|-----------|----------|--------|
| Phase 1 | [ ] | [ ] | _____ |
| Phase 2 | [ ] | [ ] | _____ |
| Phase 3 | [ ] | [ ] | _____ |
| Phase 4 | [ ] | [ ] | _____ |
| Phase 5 | [ ] | [ ] | _____ |

### Deployment Approval

- [ ] All phases complete
- [ ] All checkpoints passed
- [ ] QA compliance verified (≥95%)
- [ ] User approval for deployment

**Approved for deployment by:** _________________
**Date:** _________________

---

*End of Implementation Plan*
