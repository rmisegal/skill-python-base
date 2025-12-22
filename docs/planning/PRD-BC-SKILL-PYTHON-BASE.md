# Product Requirements Document (PRD)
# BC (Book Creator) Skill Python Base System

**Document Version:** 1.0.0
**Date:** 2025-12-22
**Author:** Claude Code Architecture Team
**Status:** Draft
**Reference:** BC-CLAUDE-MECHANISM-ARCHITECTURE-REPORT.md

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

The current Claude CLI BC (Book Creator) skills system for Hebrew-English academic LaTeX documents suffers from:

- **No embedded QA rules**: Content creation skills lack knowledge of QA requirements, causing a "generate → fail QA → fix" cycle
- **High token consumption**: LLM performs templating that could be Python-automated
- **Missing critical skills**: The `bc-drawing` (Agent C) was referenced but never implemented
- **Inconsistent structure**: Skills located in wrong directories (e.g., `bc-Hrari-content-style` under `bc-math`)
- **No pre-validation**: Content is only validated after compilation, not at creation time
- **No orchestration engine**: Manual coordination of BC agents with no automated workflow
- **No test framework**: No way to verify BC skills generate QA-compliant content

### 1.2 Proposed Solution

Build a **hybrid skill/Python tool system** that:

- Embeds QA compliance rules directly into BC content creation skills
- Delegates deterministic operations (templating, validation) to Python
- Provides pre-validation tools to check content before compilation
- Implements BC orchestration engine with Python backend
- Creates `insert_bc_skill` meta-skill for automated skill creation
- Includes comprehensive test framework for BC outputs

### 1.3 Expected Outcomes

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Token usage per chapter | ~8,000 | ~5,000 | 37% reduction |
| QA pass rate (first run) | ~60% | ~95% | 58% improvement |
| Content consistency | ~85% | 100% | Deterministic templates |
| Pre-validation errors caught | 0% | 80%+ | New capability |
| Skill creation time | ~2 hours | ~15 min | 8x faster |
| Missing skills | 1 (bc-drawing) | 0 | Complete coverage |

---

## 2. Product Vision

### 2.1 Vision Statement

> Create a **QA-compliant-from-creation content generation system** for academic LaTeX documents that combines the creativity of Claude CLI skills with the precision of Python templating and validation, enabling consistent, high-quality book production at scale.

### 2.2 Product Principles

1. **QA-First Generation**: Embed QA rules into BC skills so content is correct from creation
2. **Template Before Generate**: Use Python templates for deterministic patterns
3. **Validate Before Compile**: Pre-validate content before LaTeX compilation
4. **Token Efficiency**: Minimize LLM calls for repetitive operations
5. **Composability**: Skills and tools should be independently testable and combinable
6. **Parallel Execution**: Maximize parallel processing at chapter and enhancement levels

### 2.3 Out of Scope

- GUI interface (CLI only)
- Support for non-LaTeX documents
- Real-time collaborative editing
- Languages other than Hebrew-English
- Cloud deployment (local execution only)

---

## 3. Goals and Objectives

### 3.1 Primary Goals

| ID | Goal | Success Criteria |
|----|------|------------------|
| G1 | Embed QA rules in BC skills | All BC skills contain QA compliance rules |
| G2 | Reduce token consumption | 30-40% reduction in tokens per chapter |
| G3 | Increase QA pass rate | 95%+ first-run QA pass rate |
| G4 | Enable pre-validation | Python validators for all content types |
| G5 | Automate skill creation | `insert_bc_skill` creates complete skill in <5 commands |

### 3.2 Secondary Goals

| ID | Goal | Success Criteria |
|----|------|------------------|
| G6 | Standardize skill structure | All BC skills in correct directories |
| G7 | Create BC orchestration | Python-backed orchestration engine |
| G8 | Enable automated testing | 90%+ test coverage for validators |
| G9 | Support parallel execution | Chapter-level and enhancement-level parallelization |

### 3.3 Non-Goals

- Replacing creative content generation with Python (LLM still required)
- Supporting non-academic writing styles
- Building a web service
- Automating LaTeX compilation (separate concern)

---

## 4. Target Users

### 4.1 Primary Users

#### User Persona 1: Academic Book Author
- **Role**: Creates Hebrew-English academic content
- **Need**: Generate QA-compliant LaTeX content efficiently
- **Skill Level**: Expert in domain, intermediate LaTeX
- **Usage Frequency**: Daily during book production

#### User Persona 2: BC Skill Developer
- **Role**: Creates and maintains BC skills
- **Need**: Easy skill creation with embedded QA rules
- **Skill Level**: Advanced Python, intermediate CLI
- **Usage Frequency**: Monthly

#### User Persona 3: Book Production Coordinator
- **Role**: Manages multi-chapter book production
- **Need**: Orchestration, progress tracking, batch processing
- **Skill Level**: Intermediate CLI, basic Python
- **Usage Frequency**: Weekly

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
   - Integration strategy with existing BC skills
   - Testing strategy for QA compliance
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
# Implementation Plan - BC Skill Python Base

## 1. Architecture Overview
   - System components
   - Data flow diagrams
   - Integration with QA mechanism

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
   - QA compliance validation

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
- [ ] Include QA compliance validation checkpoints

### 5.4 Parallel Execution Design Principle

**MANDATORY:** The design MUST maximize parallel execution wherever possible.

#### Parallel Execution Guidelines:

| Scenario | Parallel Approach |
|----------|-------------------|
| Chapter Production | Process ALL chapters in parallel |
| Phase 2.3 Enhancement | Run bc-code, bc-math, bc-drawing, bc-academic-source in parallel |
| Pre-Validation | Validate all .tex files in parallel |
| Python Tool Development | Develop independent validators in parallel |
| Test Execution | Run test suites in parallel |

#### Identify Parallel Opportunities:

```
PARALLEL EXECUTION MAP:

Phase 1 (Foundation):
├── [PARALLEL] base_validator.py
├── [PARALLEL] template_engine.py
├── [PARALLEL] progress_tracker.py
└── [SEQUENTIAL - depends on above] controller.py

Phase 2 (Validators):
├── [PARALLEL] validate_content.py
├── [PARALLEL] validate_code.py
├── [PARALLEL] validate_tikz.py
├── [PARALLEL] validate_tables.py
└── [PARALLEL] validate_citations.py

Phase 3 (Skill Updates):
├── [PARALLEL] Update bc-Hrari-content-style
├── [PARALLEL] Update bc-code
├── [PARALLEL] Update bc-academic-source
├── [PARALLEL] Update bc-math
└── [SEQUENTIAL - after all updates] integration_test.py
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
C:\25D\GeneralLearning\skill-python-base\
├── .claude/
│   └── skills/           # LOCAL skill development
│       ├── bc-orchestration/
│       ├── bc-source-research/
│       ├── bc-Hrari-content-style/
│       ├── bc-drawing/
│       ├── bc-code/
│       ├── bc-math/
│       ├── bc-academic-source/
│       ├── bc-architect/
│       ├── bc-hebrew/
│       └── insert_bc_skill/
├── bc_engine/            # Python backend
├── tests/                # Integration tests
└── docs/                 # Documentation
```

### 6.2 Development vs Production Paths

| Environment | Path | Purpose |
|-------------|------|---------|
| **LOCAL (Development)** | `C:\25D\GeneralLearning\skill-python-base\.claude\skills\` | All development, testing, iteration |
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
│  1. Create/modify skill.md files with QA rules                          │
│  2. Develop Python validators (validate_*.py)                           │
│  3. Create Python templates (templates/)                                │
│  4. Write unit tests (test_*.py)                                        │
│  5. Create test fixtures                                                │
│  6. Run local tests                                                     │
│                                                                          │
│                         ▼                                                │
│                                                                          │
│  STAGE 2: LOCAL TESTING                                                  │
│  ──────────────────────                                                 │
│  Location: skill-python-base/                                           │
│                                                                          │
│  1. Run ALL validator tests: python -m pytest                           │
│  2. Run pre-validation on sample chapters                               │
│  3. Generate sample content and verify QA compliance                    │
│  4. Verify token reduction metrics                                      │
│  5. All tests MUST pass                                                 │
│                                                                          │
│                         ▼                                                │
│                                                                          │
│  STAGE 3: QA COMPLIANCE VALIDATION                                       │
│  ─────────────────────────────────                                      │
│                                                                          │
│  1. Generate content using updated BC skills                            │
│  2. Run qa-super on generated content                                   │
│  3. Verify 95%+ QA pass rate                                            │
│  4. Document any remaining issues                                       │
│                                                                          │
│                         ▼                                                │
│                                                                          │
│  STAGE 4: USER APPROVAL                                                  │
│  ──────────────────────                                                 │
│                                                                          │
│  1. Generate test report                                                │
│  2. Document changes made                                               │
│  3. Present to user for review                                          │
│  4. User explicitly approves deployment                                 │
│                                                                          │
│                         ▼                                                │
│                                                                          │
│  STAGE 5: GLOBAL DEPLOYMENT                                              │
│  ─────────────────────────                                              │
│  Target: C:\Users\gal-t\.claude\skills\                                 │
│                                                                          │
│  1. Backup existing global skills                                       │
│  2. Copy LOCAL skills to GLOBAL location                                │
│  3. Copy bc_engine/ to appropriate location                             │
│  4. Verify global skills work                                           │
│  5. Run validation tests                                                │
│  6. Update BC-CLAUDE.md                                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Deployment Prerequisites

**Before deploying to global Claude CLI skills:**

- [ ] ALL unit tests pass (100%)
- [ ] ALL integration tests pass
- [ ] QA compliance verified (95%+ pass rate)
- [ ] Token reduction verified (30%+ reduction)
- [ ] All skills in correct directory structure
- [ ] Documentation complete
- [ ] User has reviewed changes
- [ ] User has EXPLICITLY approved deployment
- [ ] Backup of existing global skills created

### 6.5 Global Skill Replacement Procedure

```bash
# Step 1: Backup existing global skills
cp -r "C:\Users\gal-t\.claude\skills\bc-*" "C:\Users\gal-t\.claude\skills-backup-YYYYMMDD\"

# Step 2: Copy new skills to global
cp -r "C:\25D\GeneralLearning\skill-python-base\.claude\skills\bc-*" "C:\Users\gal-t\.claude\skills\"

# Step 3: Copy Python engine
cp -r "C:\25D\GeneralLearning\skill-python-base\bc_engine" "C:\Users\gal-t\.claude\"

# Step 4: Verify installation
cd "C:\Users\gal-t\.claude"
python -m pytest bc_engine/tests/

# Step 5: Test with real chapter
/bc-Hrari-content-style "test chapter"
```

### 6.6 Rollback Procedure

If issues are discovered after deployment:

```bash
# Restore from backup
rm -rf "C:\Users\gal-t\.claude\skills\bc-*"
cp -r "C:\Users\gal-t\.claude\skills-backup-YYYYMMDD\bc-*" "C:\Users\gal-t\.claude\skills\"
```

---

## 7. Claude CLI Skill Standards

### 7.1 Professional Skill Writing Requirements

**MANDATORY:** All BC skills MUST be written following Claude CLI professional standards.

When creating NEW skills or REWRITING existing skills, follow these requirements:

### 7.2 Skill File Structure Standard

```markdown
---
name: bc-{agent-name}
description: {Clear, concise description} - {Persona} persona
version: X.Y.Z
author: BC Team
tags: [bc, {phase}, {capability}, {persona}]
tools: [Read, Write, Edit, Grep, Glob, Bash]  # If applicable
qa_rules_embedded: true  # NEW: Indicates QA rules are embedded
---

# {Agent Name} Skill

## Agent Identity
- **Name:** {Display Name}
- **Role:** {Role Description}
- **Phase:** {2.1 | 2.2 | 2.3 | 2.4}
- **Persona:** {Historical Figure}

## Mission Statement
{Clear statement of skill's purpose}

## QA Compliance Rules (MUST FOLLOW)
### From qa-BiDi Family:
- {Rule list with patterns to AVOID and patterns to USE}

### From qa-code Family:
- {Rule list}

### From qa-img Family:
- {Rule list}

## Pre-Validation Checklist
Before outputting content, verify:
- [ ] {Checklist items}

## {Main Content Sections}
{Templates, Workflows, etc.}

## Communication Protocol
- **Trigger Keywords:** {keywords}
- **Handoff Protocol:** {handoff description}
- **Completion Signal:** {signal name}

## Input/Output Format

### Input
{Structured input specification}

### Output
{LaTeX or structured output format}

## Version History
- **vX.Y.Z** (YYYY-MM-DD): {Change description}

---

**Parent:** {parent-skill or workflow phase}
**Coordination:** bc-orchestration/BC-CLAUDE.md
```

### 7.3 Naming Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| Skill folder | `bc-{agent-name}` | `bc-drawing` |
| Skill file | `skill.md` | `skill.md` |
| Validator | `validate_{type}.py` | `validate_content.py` |
| Test file | `test_validate.py` | `test_validate.py` |
| Templates folder | `templates/` | `templates/` |
| Fixtures folder | `fixtures/` | `fixtures/` |

### 7.4 Skill Quality Checklist

Before a skill is considered complete:

- [ ] Follows standard file structure
- [ ] Has complete YAML frontmatter
- [ ] Has Agent Identity section
- [ ] Has QA Compliance Rules section (NEW)
- [ ] Has Pre-Validation Checklist (NEW)
- [ ] Has Communication Protocol
- [ ] Has Input/Output format specification
- [ ] Has Version History
- [ ] Has proper naming convention
- [ ] `qa_rules_embedded: true` in frontmatter (NEW)
- [ ] All tags are relevant and lowercase

### 7.5 Version Numbering Standard

Use Semantic Versioning (SemVer):

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking change | MAJOR | 1.0.0 → 2.0.0 |
| New feature | MINOR | 1.0.0 → 1.1.0 |
| Bug fix | PATCH | 1.0.0 → 1.0.1 |
| QA rules embedded | MINOR | 1.0.0 → 1.1.0 |

### 7.6 MANDATORY: QA Rules Embedding

**CRITICAL ARCHITECTURAL REQUIREMENT:** All BC content creation skills MUST embed relevant QA rules.

#### Embedding Principles

```
┌─────────────────────────────────────────────────────────────────────────┐
│              QA-FIRST CONTENT GENERATION ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  BEFORE (Current):                                                       │
│  ─────────────────                                                       │
│  BC Skill generates → Content has issues → QA fails → Fix → Re-QA       │
│                                                                          │
│  AFTER (Required):                                                       │
│  ──────────────────                                                      │
│  BC Skill (with QA rules) generates → Pre-validate → Content correct    │
│                                          ↓                               │
│                                       QA passes                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### QA Rules to Embed by Skill

| BC Skill | QA Rules to Embed |
|----------|-------------------|
| bc-Hrari-content-style | BiDi Rules 6, 7, 10, 12, 15; Figure reference completeness |
| bc-code | Code background wrap; English-only comments; Line limit |
| bc-drawing | TikZ english wrapper; English-only content; Caption placement |
| bc-math | BiDi Rules 1, 2, 3; `\ilm{}` formatting |
| bc-academic-source | Table column reversal; Cell command usage |

#### Embedding Format

```markdown
## QA Compliance Rules (MUST FOLLOW)

### From qa-BiDi Family:
| Rule | AVOID This | USE This Instead |
|------|------------|------------------|
| Rule 6 | `123` in Hebrew context | `\en{123}` or `\num{123}` |
| Rule 7 | `Word` in Hebrew context | `\en{Word}` |
| Rule 10 | `MCP` in Hebrew context | `\en{MCP}` |

### From qa-code Family:
| Rule | AVOID This | USE This Instead |
|------|------------|------------------|
| background-overflow | `\begin{pythonbox}` in RTL | Wrap in `\begin{english}...\end{english}` |
| hebrew-comment | `# הערה בעברית` | `# English comment only` |

### Pre-Validation Checklist
Before outputting content, verify:
- [ ] ALL numbers in Hebrew paragraphs wrapped: `\en{...}` or `\num{...}`
- [ ] ALL English terms wrapped: `\en{...}`
- [ ] ALL code blocks wrapped: `\begin{english}...\end{english}`
- [ ] ALL figures referenced in body text
- [ ] ALL TikZ wrapped in english environment
```

---

## 8. Skill Resources and Tools

### 8.1 Skill Resources Support

**MANDATORY:** BC Skills MUST support adding resources for enhanced functionality.

#### Resource Types:

| Resource Type | Location | Purpose |
|---------------|----------|---------|
| Python Validators | `validate_*.py` | Pre-validation before compilation |
| Templates | `templates/` | LaTeX pattern templates |
| Test Files | `test_validate.py` | Unit tests for validators |
| Fixtures | `fixtures/` | Test data files |
| Configuration | `config.json` | Skill-specific configuration |

### 8.2 Resource Directory Structure

```
bc-{skill-name}/
├── skill.md              # REQUIRED: Skill definition with QA rules
├── validate_{type}.py    # RECOMMENDED: Python validator
├── test_validate.py      # RECOMMENDED: Unit tests
├── templates/            # RECOMMENDED: LaTeX templates
│   ├── section.template
│   ├── figure.template
│   └── code.template
├── fixtures/             # RECOMMENDED: Test fixtures
│   ├── valid_output.tex
│   └── invalid_output.tex
└── config.json           # OPTIONAL: Skill config
```

### 8.3 Python Validator Recommendations

**When to Add Python Validators:**

| Scenario | Recommendation |
|----------|----------------|
| BiDi pattern checking | **MUST** add Python validator |
| Template generation | **MUST** add Python templater |
| Reference validation | **MUST** add Python validator |
| Creative content generation | KEEP in skill |
| Style/judgment decisions | KEEP in skill |

### 8.4 Template Integration Pattern

```markdown
## Skill Definition (skill.md)

### Python Template Reference

This skill uses Python templates for deterministic operations:

| Template | Purpose | Input | Output |
|----------|---------|-------|--------|
| section.template | Section structure | title, content | LaTeX section |
| figure.template | Figure with caption | label, caption, path | LaTeX figure |
| pythonbox.template | Code block | title, code | pythonbox env |

### Template Invocation

```python
from templates import template_engine

# Generate section
section_latex = template_engine.render('section', {
    'title': 'מבוא',
    'content': content
})
```
```

### 8.5 Recommended Resources for Each BC Skill

#### bc-Hrari-content-style
```
RECOMMENDED RESOURCES:
├── validate_content.py   # BiDi compliance validator
├── test_validate.py      # Unit tests
├── templates/            # LaTeX templates
│   ├── section.template
│   ├── figure_ref.template
│   └── citation.template
└── fixtures/
    ├── valid_chapter.tex
    └── invalid_chapter.tex
```

#### bc-code
```
RECOMMENDED RESOURCES:
├── validate_code.py      # Code block validator
├── test_validate.py      # Unit tests
├── templates/
│   ├── pythonbox.template
│   └── pythonbox_star.template
└── fixtures/
    ├── valid_code.tex
    └── invalid_code.tex
```

#### bc-drawing
```
RECOMMENDED RESOURCES:
├── validate_tikz_bidi.py # TikZ BiDi validator
├── test_validate.py      # Unit tests
├── templates/
│   ├── block_diagram.template
│   ├── flowchart.template
│   └── architecture.template
└── fixtures/
    ├── valid_diagram.tex
    └── invalid_diagram.tex
```

#### bc-academic-source
```
RECOMMENDED RESOURCES:
├── validate_citations.py # Citation validator
├── validate_tables.py    # Table structure validator
├── test_validate.py      # Unit tests
├── templates/
│   ├── rtl_table.template
│   └── bibtex.template
└── fixtures/
    ├── valid_table.tex
    └── invalid_table.tex
```

---

## 9. Functional Requirements

### 9.1 BC Engine Core (FR-100 Series)

#### FR-101: BC Controller
**Priority:** P0 (Critical)
**Description:** System shall provide a central controller for BC skill coordination.

**Acceptance Criteria:**
- AC1: Load configuration from `bc_setup.json`
- AC2: Manage chapter production workflow
- AC3: Coordinate parallel skill execution
- AC4: Track progress across phases
- AC5: Signal completion for each phase

**API:**
```python
class BCController:
    def __init__(self, project_path: str, config_path: str = None)
    def run_chapter_production(self, chapter: str) -> Dict
    def run_parallel_enhancement(self, chapter: str) -> Dict
    def get_progress(self) -> Dict
```

---

#### FR-102: Progress Tracker
**Priority:** P1 (High)
**Description:** System shall track and report BC production progress.

**Acceptance Criteria:**
- AC1: Track skill execution status (PENDING, RUNNING, DONE, ERROR)
- AC2: Track completion signals (Source_Collection_Complete, Draft_Complete, etc.)
- AC3: Calculate overall progress percentage
- AC4: Report phase completion

**Storage:** `bc_orchestration/BC-TASKS.md`

---

#### FR-103: Template Engine
**Priority:** P0 (Critical)
**Description:** System shall provide templating for deterministic LaTeX patterns.

**Acceptance Criteria:**
- AC1: Load templates from skill directories
- AC2: Render templates with variable substitution
- AC3: Support nested templates
- AC4: Handle BiDi-safe wrapper templates

**Templates to Support:**
```python
REQUIRED_TEMPLATES = {
    'section': '\\hebrewsection{{{title}}}\n{content}',
    'figure_ref': 'איור~\\ref{{fig:{label}}}',
    'table_ref': 'טבלה~\\ref{{tab:{label}}}',
    'en_wrap': '\\en{{{content}}}',
    'num_wrap': '\\num{{{content}}}',
    'ilm_wrap': '\\ilm{{${content}$}}',
    'pythonbox': '\\begin{{english}}\n\\begin{{pythonbox}}[{title}]\n{code}\n\\end{{pythonbox}}\n\\end{{english}}',
    'tikz': '\\begin{{english}}\n\\begin{{tikzpicture}}\n{content}\n\\end{{tikzpicture}}\n\\end{{english}}',
}
```

---

#### FR-104: Skill Discovery
**Priority:** P1 (High)
**Description:** System shall automatically discover all available BC skills.

**Acceptance Criteria:**
- AC1: Scan `.claude/skills/bc-*` directories
- AC2: Parse skill.md frontmatter for metadata
- AC3: Identify skills with embedded QA rules (`qa_rules_embedded: true`)
- AC4: Identify Python validators for each skill

---

### 9.2 Pre-Validation (FR-200 Series)

#### FR-201: Content Validator
**Priority:** P0 (Critical)
**Description:** Python tool to validate bc-Hrari-content-style output for QA compliance.

**Rules to Validate:**
| Rule | Pattern | Fix Suggestion |
|------|---------|----------------|
| number-not-wrapped | `(\d+)` in Hebrew context | Wrap with `\en{}` |
| english-not-wrapped | `([A-Z][a-z]+)` in Hebrew | Wrap with `\en{}` |
| acronym-not-wrapped | `([A-Z]{2,})` in Hebrew | Wrap with `\en{}` |
| figure-not-referenced | `\label{fig:X}` without `\ref{fig:X}` | Add reference |

**Interface:**
```python
class ContentValidator(BCValidator):
    def validate(content: str, file_path: str) -> List[ValidationIssue]
```

---

#### FR-202: Code Validator
**Priority:** P0 (Critical)
**Description:** Python tool to validate bc-code output for QA compliance.

**Rules to Validate:**
| Rule | Pattern | Fix Suggestion |
|------|---------|----------------|
| hebrew-in-comment | `#.*[\u0590-\u05FF]` | Use English comments |
| code-no-english-wrapper | pythonbox without english env | Wrap in english |
| code-too-long | >40 lines | Simplify or use pythonbox* |

---

#### FR-203: TikZ Validator
**Priority:** P0 (Critical)
**Description:** Python tool to validate bc-drawing output for BiDi compliance.

**Rules to Validate:**
| Rule | Pattern | Fix Suggestion |
|------|---------|----------------|
| tikz-no-english-wrapper | tikzpicture without english | Wrap in english |
| hebrew-in-tikz | Hebrew chars in tikzpicture | Use English only |

**Status:** IMPLEMENTED (`validate_tikz_bidi.py`)

---

#### FR-204: Table Validator
**Priority:** P1 (High)
**Description:** Python tool to validate bc-academic-source table output.

**Rules to Validate:**
| Rule | Pattern | Fix Suggestion |
|------|---------|----------------|
| column-order-wrong | Columns not reversed | Reverse column order |
| cell-not-wrapped | Mixed content without hebcell/encell | Use proper wrapper |

---

#### FR-205: Citation Validator
**Priority:** P1 (High)
**Description:** Python tool to validate citation completeness.

**Rules to Validate:**
| Rule | Pattern | Fix Suggestion |
|------|---------|----------------|
| citation-not-in-bib | `\cite{X}` without bib entry | Add to bibliography |
| doi-missing | BibTeX entry without DOI | Add DOI |

---

### 9.3 Skill Updates (FR-300 Series)

#### FR-301: Embed QA Rules in bc-Hrari-content-style
**Priority:** P0 (Critical)
**Description:** Add QA compliance rules and pre-validation checklist.

**Acceptance Criteria:**
- AC1: Add "QA Compliance Rules" section with BiDi rules
- AC2: Add "Pre-Validation Checklist" section
- AC3: Add `qa_rules_embedded: true` to frontmatter
- AC4: Update version to 2.0.0

---

#### FR-302: Embed QA Rules in bc-code
**Priority:** P0 (Critical)
**Description:** Add code-specific QA compliance rules.

**Acceptance Criteria:**
- AC1: Add code block wrapping rules
- AC2: Add English-only comment mandate
- AC3: Add line limit guidance
- AC4: Add pre-validation checklist

---

#### FR-303: Relocate bc-Hrari-content-style
**Priority:** P1 (High)
**Description:** Move skill from bc-math/ to root skills directory.

**Acceptance Criteria:**
- AC1: Move from `.claude/skills/bc-math/bc-Hrari-content-style/` to `.claude/skills/bc-Hrari-content-style/`
- AC2: Update all references
- AC3: Verify skill invocation works

---

#### FR-304: Update bc-drawing with Validation
**Priority:** P0 (Critical)
**Description:** Ensure bc-drawing has Python validator and templates.

**Status:** PARTIALLY IMPLEMENTED
- [x] skill.md created
- [x] validate_tikz_bidi.py created
- [ ] Templates for block diagram, flowchart, architecture
- [ ] Unit tests

---

### 9.4 BC Orchestration (FR-400 Series)

#### FR-401: bc_setup.json Configuration
**Priority:** P0 (Critical)
**Description:** Central configuration file for BC system.

**Schema:** See Section 15

---

#### FR-402: BC-CLAUDE.md Coordination Doc
**Priority:** P1 (High)
**Description:** Central coordination document for BC skills.

**Content:**
- Skill hierarchy diagram
- Workflow phases
- Signal definitions
- Parallel execution rules

---

#### FR-403: BC-TASKS.md Progress Tracker
**Priority:** P1 (High)
**Description:** Progress tracking file for BC execution.

**Format:**
```markdown
# BC Production Status

## Current Chapter: [chapter_name]

## Phase Status
| Phase | Status | Started | Completed | Signal |
|-------|--------|---------|-----------|--------|
| 2.1 Source Research | DONE | ... | ... | Source_Collection_Complete |
| 2.2 Content Drafting | RUNNING | ... | - | - |
| 2.3 Enhancement | PENDING | - | - | - |
```

---

### 9.5 Skill Management (FR-500 Series)

#### FR-501: insert_bc_skill - Create Mode
**Priority:** P0 (Critical)
**Description:** Create new BC skill from requirements.

**Inputs:**
- `--name`: Skill name
- `--phase`: Workflow phase (2.1, 2.2, 2.3, 2.4)
- `--persona`: Agent persona
- `--description`: Brief description
- `--qa_rules`: Comma-separated QA rules to embed
- `--python`: true | false (generate Python validator)

**Outputs:**
- `skill.md`: Skill definition with QA rules
- `validate_{type}.py`: Python validator (if `--python=true`)
- `test_validate.py`: Unit tests
- `templates/`: Template directory
- Updated BC-CLAUDE.md

---

#### FR-502: insert_bc_skill - Embed-QA Mode
**Priority:** P1 (High)
**Description:** Add QA rules to existing BC skill.

**Inputs:**
- `--skill`: Existing skill name
- `--qa_rules`: Comma-separated QA rules to add

**Outputs:**
- Updated `skill.md` with QA rules section
- Updated frontmatter with `qa_rules_embedded: true`
- Updated version number

---

#### FR-503: insert_bc_skill - Add-Validator Mode
**Priority:** P1 (High)
**Description:** Add Python validator to existing BC skill.

**Inputs:**
- `--skill`: Existing skill name
- `--validations`: Comma-separated validation types

**Outputs:**
- `validate_{type}.py`: Python validator
- `test_validate.py`: Unit tests
- Updated skill.md with validator reference

---

### 9.6 Testing (FR-600 Series)

#### FR-601: Base Validator Test Class
**Priority:** P0 (Critical)
**Description:** Provide base class for all validator tests.

**Methods:**
```python
class BCValidatorTestBase:
    def load_fixture(name: str) -> str
    def assertIssueFound(issues: list, rule: str)
    def assertNoIssue(issues: list, rule: str)
    def assertIssueCount(issues: list, expected: int)
    def assertQACompliant(content: str)
```

---

#### FR-602: Test Fixtures
**Priority:** P0 (Critical)
**Description:** Each BC validator shall have test fixtures.

**Required Fixtures:**
- `valid_output.tex`: Content with no issues (QA compliant)
- `invalid_output.tex`: Content with known issues
- Additional edge case fixtures as needed

---

#### FR-603: QA Compliance Test Suite
**Priority:** P0 (Critical)
**Description:** Test that BC skill output passes QA.

**Test Cases:**
- BC skill generates content → Content passes qa-super
- Pre-validation catches same issues as QA detection
- Fixed content passes both pre-validation and QA

---

---

## 10. Non-Functional Requirements

### 10.1 Performance (NFR-100)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-101 | Token usage reduction | 30-40% vs current |
| NFR-102 | Template rendering speed | <10ms per template |
| NFR-103 | Validation speed | 1000 lines/second |
| NFR-104 | Startup time | <2 seconds |

### 10.2 Reliability (NFR-200)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-201 | QA pass rate on first run | 95%+ |
| NFR-202 | Validation consistency | 100% (deterministic) |
| NFR-203 | Template correctness | 100% (BiDi safe) |
| NFR-204 | Error recovery | Continue on non-critical errors |

### 10.3 Usability (NFR-300)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-301 | Skill creation time | <15 minutes with insert_bc_skill |
| NFR-302 | Error messages | Clear, actionable with fix suggestions |
| NFR-303 | Documentation | README + API docs for all components |

### 10.4 Maintainability (NFR-400)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-401 | Test coverage | 90%+ for Python validators |
| NFR-402 | Code style | PEP 8 compliant |
| NFR-403 | Documentation | Docstrings for all public functions |
| NFR-404 | Module size | <150 lines per Python file |

### 10.5 Compatibility (NFR-500)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-501 | QA integration | Work with qa-super without modification |
| NFR-502 | Skill compatibility | Existing skills continue to work |
| NFR-503 | LaTeX compatibility | Work with hebrew-academic-template.cls |

---

## 11. Technical Architecture

### 11.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                 │
│                    (Claude CLI / bc-* skill commands)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          BC ORCHESTRATION LAYER                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   bc-super      │  │ bc_setup.json   │  │  BC Controller  │         │
│  │   (Skill)       │  │ (Configuration) │  │  (Python)       │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           └────────────────────┴────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONTENT CREATION LAYER (BC Skills)                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │bc-source-  │ │bc-Hrari-   │ │bc-drawing  │ │bc-code     │           │
│  │research    │ │content     │ │(Da Vinci)  │ │(Rami)      │           │
│  │(Garfield)  │ │(Harari)    │ │            │ │            │           │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘           │
│        │              │              │              │                   │
│  ┌─────┴──────┐ ┌─────┴──────┐ ┌─────┴──────┐ ┌─────┴──────┐           │
│  │bc-math     │ │bc-academic-│ │bc-architect│ │bc-hebrew   │           │
│  │(Hinton)    │ │source      │ │(Harari)    │ │(Academy)   │           │
│  │            │ │(Segal)     │ │            │ │            │           │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PYTHON TOOLS LAYER (Pre-Validation)                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ContentValid  │ │CodeValidator │ │TikZValidator │ │TableValidator│   │
│  │   (Python)   │ │   (Python)   │ │   (Python)   │ │   (Python)   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌──────────────┐                                     │
│  │CitationValid │ │TemplateEng  │                                      │
│  │   (Python)   │ │   (Python)   │                                      │
│  └──────────────┘ └──────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE LAYER                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  Progress   │ │   Signal    │ │  Template   │ │   Logger    │       │
│  │  Tracker    │ │   Handler   │ │   Engine    │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            FILE SYSTEM                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ .tex files  │ │ .bib files  │ │BC-TASKS.md  │ │  bc-logs/   │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Directory Structure

```
.claude/
├── skills/
│   ├── bc-orchestration/
│   │   ├── BC-CLAUDE.md
│   │   ├── BC-TASKS.md
│   │   └── bc_setup.json
│   │
│   ├── bc-source-research/
│   │   ├── skill.md
│   │   └── templates/
│   │       └── bibtex_entry.template
│   │
│   ├── bc-Hrari-content-style/      # MOVED from bc-math/
│   │   ├── skill.md
│   │   ├── validate_content.py
│   │   ├── test_validate.py
│   │   └── templates/
│   │       ├── section.template
│   │       └── figure_ref.template
│   │
│   ├── bc-drawing/
│   │   ├── skill.md
│   │   ├── validate_tikz_bidi.py
│   │   ├── test_validate.py
│   │   └── templates/
│   │       ├── block_diagram.template
│   │       └── flowchart.template
│   │
│   ├── bc-code/
│   │   ├── skill.md
│   │   ├── validate_code.py
│   │   ├── test_validate.py
│   │   └── templates/
│   │       └── pythonbox.template
│   │
│   ├── bc-math/
│   │   ├── skill.md
│   │   └── validate_math.py
│   │
│   ├── bc-academic-source/
│   │   ├── skill.md
│   │   ├── validate_citations.py
│   │   ├── validate_tables.py
│   │   └── templates/
│   │       └── rtl_table.template
│   │
│   ├── bc-architect/
│   │   └── skill.md
│   │
│   ├── bc-hebrew/
│   │   └── skill.md
│   │
│   ├── insert_bc_skill/
│   │   ├── skill.md
│   │   └── templates/
│   │       ├── skill_template.md
│   │       ├── validator_template.py
│   │       └── test_template.py
│   │
│   └── bc-test-runner/
│       ├── run_all_tests.py
│       ├── base_test.py
│       └── conftest.py
│
├── bc_engine/
│   ├── __init__.py
│   ├── controller.py
│   ├── progress_tracker.py
│   ├── template_engine.py
│   ├── signal_handler.py
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── base_validator.py
│   │   ├── validate_content.py
│   │   ├── validate_code.py
│   │   ├── validate_tikz.py
│   │   ├── validate_tables.py
│   │   └── validate_citations.py
│   └── templates/
│       └── builtin_templates.py
│
└── commands/
    └── doc-book-from-text.md
```

### 11.3 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.10+ |
| CLI Framework | Claude CLI | Latest |
| Testing | pytest | 7.x+ |
| Templating | Python f-strings | stdlib |
| Logging | Python logging | stdlib |
| LaTeX | LuaLaTeX | Latest |

---

## 12. User Stories

### 12.1 Book Author Stories

#### US-101: Generate QA-Compliant Chapter
**As a** book author
**I want to** generate a chapter that passes QA on first run
**So that** I don't waste time on fix cycles

**Acceptance Criteria:**
- Given I invoke bc-Hrari-content-style
- When it generates chapter content
- Then the content passes qa-super with 95%+ success rate

---

#### US-102: Pre-Validate Content
**As a** book author
**I want to** validate content before compilation
**So that** I catch issues early

**Acceptance Criteria:**
- Given I have generated content
- When I run pre-validation
- Then I see any QA compliance issues immediately
- And I receive fix suggestions

---

#### US-103: Generate BiDi-Safe Diagrams
**As a** book author
**I want to** generate TikZ diagrams that render correctly
**So that** diagrams are not reversed/mirrored

**Acceptance Criteria:**
- Given I request a diagram from bc-drawing
- When the diagram is generated
- Then it is wrapped in `\begin{english}...\end{english}`
- And all text is in English
- And captions are in Hebrew outside the english environment

---

### 12.2 Skill Developer Stories

#### US-201: Create New BC Skill
**As a** skill developer
**I want to** create a new BC skill with QA rules
**So that** it generates compliant content from the start

**Acceptance Criteria:**
- Given I invoke `insert_bc_skill --mode=create`
- When I provide skill details and QA rules
- Then skill.md is created with QA Compliance Rules section
- And Pre-Validation Checklist is included
- And Python validator is generated (if requested)

---

#### US-202: Add QA Rules to Existing Skill
**As a** skill developer
**I want to** add QA rules to an existing skill
**So that** it generates compliant content

**Acceptance Criteria:**
- Given I invoke `insert_bc_skill --mode=embed-qa`
- When I specify skill and rules
- Then skill.md is updated with QA rules section
- And frontmatter includes `qa_rules_embedded: true`

---

### 12.3 Production Coordinator Stories

#### US-301: Track Chapter Progress
**As a** production coordinator
**I want to** track progress across all chapters
**So that** I know the production status

**Acceptance Criteria:**
- Given production is running
- When I check BC-TASKS.md
- Then I see status of each chapter
- And completion signals for each phase

---

---

## 13. API Specifications

### 13.1 Python Validator Interface

```python
# bc_engine/validators/base_validator.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum

class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass
class ValidationIssue:
    """Issue found during pre-validation."""
    rule: str
    file: str
    line: int
    content: str
    severity: Severity
    fix_suggestion: str
    context: Optional[Dict[str, Any]] = None

class BCValidator(ABC):
    """Base interface for BC content validators."""

    @abstractmethod
    def validate(self, content: str, file_path: str) -> List[ValidationIssue]:
        """Validate content and return list of issues."""
        pass

    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        pass

    def is_qa_compliant(self, content: str, file_path: str) -> bool:
        """Check if content is QA compliant (no errors)."""
        issues = self.validate(content, file_path)
        return all(i.severity != Severity.ERROR for i in issues)
```

### 13.2 Template Engine Interface

```python
# bc_engine/template_engine.py

class TemplateEngine:
    """Interface for LaTeX template rendering."""

    def __init__(self, templates_dir: str = None):
        """Initialize with optional custom templates directory."""
        pass

    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        pass

    def register_template(self, name: str, template: str) -> None:
        """Register a new template."""
        pass

    def get_template(self, name: str) -> str:
        """Get template string by name."""
        pass
```

### 13.3 Controller Interface

```python
# bc_engine/controller.py

class BCController:
    """Main BC orchestration controller."""

    def __init__(self, project_path: str, config_path: str = None):
        """Initialize with project and optional config path."""
        pass

    def run_chapter_production(self, chapter: str) -> Dict:
        """Run full chapter production pipeline. Returns results dict."""
        pass

    def run_phase(self, chapter: str, phase: str) -> Dict:
        """Run specific phase for chapter. Returns phase results."""
        pass

    def pre_validate(self, file_path: str) -> List[ValidationIssue]:
        """Run pre-validation on file. Returns issues."""
        pass

    def get_progress(self) -> Dict:
        """Get current progress."""
        pass

    def get_qa_compliance(self, file_path: str) -> Dict:
        """Check QA compliance. Returns compliance report."""
        pass
```

---

## 14. Data Models

### 14.1 ValidationIssue Model

```python
@dataclass
class ValidationIssue:
    rule: str           # Rule identifier (e.g., "number-not-wrapped")
    file: str           # Source file path
    line: int           # Line number (1-indexed)
    content: str        # Offending content
    severity: Severity  # INFO, WARNING, ERROR
    fix_suggestion: str # Suggested fix
    context: dict = None  # Additional context
```

### 14.2 Skill Metadata Model

```python
@dataclass
class BCSkillMetadata:
    name: str           # Skill name
    description: str    # Brief description
    version: str        # Semantic version
    phase: str          # 2.1, 2.2, 2.3, 2.4
    persona: str        # Agent persona
    tags: List[str]     # Search tags
    qa_rules_embedded: bool  # Whether QA rules are embedded
    has_validator: bool  # Whether Python validator exists
```

### 14.3 Production Status Model

```python
@dataclass
class ChapterStatus:
    chapter_name: str
    current_phase: str   # 2.1, 2.2, 2.3, 2.4
    phase_status: Dict[str, str]  # phase -> status
    signals: Dict[str, datetime]  # signal -> timestamp
    issues_count: int
    qa_compliant: bool
```

### 14.4 Signal Definitions

| Signal | Source | Trigger | Next Phase |
|--------|--------|---------|------------|
| Source_Collection_Complete | bc-source-research | ≥30 sources collected | Phase 2.2 |
| Draft_Complete | bc-Hrari-content-style | Chapter drafted | Phase 2.3 |
| Enhancement_Complete | bc-code, bc-math, bc-drawing, bc-academic-source | All 4 done | Phase 2.4 |
| Hinton_Review_Complete | bc-math | Technical review done | Harari Review |
| Harari_Review_Complete | bc-architect | Style review done | Hebrew Polish |
| Polish_Complete | bc-hebrew | Linguistic review done | Compilation |

---

## 15. Configuration Schema

### 15.1 bc_setup.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BC Setup Configuration",
  "type": "object",
  "properties": {
    "enabled_skills": {
      "type": "array",
      "items": {"type": "string"},
      "default": ["source-research", "content", "drawing", "code", "math", "academic-source", "architect", "hebrew"]
    },
    "workflow_phases": {
      "type": "object",
      "properties": {
        "2.1": {"type": "array", "items": {"type": "string"}, "default": ["source-research"]},
        "2.2": {"type": "array", "items": {"type": "string"}, "default": ["content"]},
        "2.3": {"type": "array", "items": {"type": "string"}, "default": ["code", "math", "drawing", "academic-source"]},
        "2.4": {"type": "array", "items": {"type": "string"}, "default": ["math", "architect", "hebrew"]}
      }
    },
    "parallel_enhancement": {
      "type": "boolean",
      "description": "Run Phase 2.3 skills in parallel",
      "default": true
    },
    "pre_validation": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": true},
        "strict_mode": {"type": "boolean", "default": false},
        "validators": {
          "type": "array",
          "items": {"type": "string"},
          "default": ["content", "code", "tikz", "tables", "citations"]
        }
      }
    },
    "qa_compliance_check": {
      "type": "boolean",
      "description": "Run QA compliance check before signaling completion",
      "default": true
    },
    "template_mode": {
      "type": "string",
      "enum": ["llm_only", "template_first", "hybrid"],
      "default": "hybrid"
    },
    "logging": {
      "type": "object",
      "properties": {
        "level": {"type": "string", "default": "INFO"},
        "file_enabled": {"type": "boolean", "default": true}
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
| QA pass rate (first run) | 60% | 95% | Run qa-super on BC output |
| Token usage per chapter | 8,000 | 5,000 | Count from API |
| Pre-validation accuracy | N/A | 95% | Match QA detection |
| Test coverage | 0% | 90% | pytest-cov |
| Skill creation time | 2 hours | 15 min | Manual timing |
| Skills with QA rules | 12.5% (1/8) | 100% | Audit skills |

### 16.2 Acceptance Thresholds

| Phase | Metric | Threshold |
|-------|--------|-----------|
| Phase 1 | Core engine functional | All FR-100 pass |
| Phase 2 | Validators implemented | All FR-200 pass |
| Phase 3 | QA rules embedded | All FR-300 pass |
| Phase 4 | insert_bc_skill works | Creates valid skill |
| Phase 5 | Full validation | 95%+ QA pass rate |

---

## 17. Dependencies

### 17.1 External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| Claude CLI | Latest | Skill execution |
| pytest | 7.x+ | Testing |
| LuaLaTeX | Latest | Document compilation |

### 17.2 Internal Dependencies

| Component | Depends On |
|-----------|------------|
| BC Controller | Template Engine, Progress Tracker, Validators |
| Validators | Base Validator Interface |
| Template Engine | Builtin Templates |
| insert_bc_skill | Templates, BC-CLAUDE.md |

### 17.3 QA Mechanism Integration

| BC Component | QA Component | Integration |
|--------------|--------------|-------------|
| Pre-validators | qa-BiDi-detect | Same patterns |
| Code validator | qa-code-detect | Same patterns |
| TikZ validator | qa-BiDi-detect-tikz | Same patterns |
| Table validator | qa-table-detect | Same patterns |

---

## 18. Constraints and Assumptions

### 18.1 Constraints

| ID | Constraint | Impact |
|----|------------|--------|
| C1 | Must run locally (no cloud) | Cannot use cloud services |
| C2 | Windows primary platform | Some Unix tools unavailable |
| C3 | Claude CLI as interface | Cannot build standalone app |
| C4 | Python 3.10+ required | Older systems not supported |
| C5 | File size <150 lines | Requires modular design |
| C6 | Must integrate with existing QA | Cannot break QA mechanism |

### 18.2 Assumptions

| ID | Assumption | Risk if Invalid |
|----|------------|-----------------|
| A1 | Users have Python 3.10+ | Need fallback or installer |
| A2 | QA patterns are stable | Need to update BC validators |
| A3 | Hebrew-English only | Need i18n for other RTL |
| A4 | LLM still required for creative content | Can't fully automate |
| A5 | CLS file provides required commands | Need to update CLS |

---

## 19. Risks and Mitigations

### 19.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Pre-validation misses issues | Medium | High | Match QA patterns exactly |
| Template rendering issues | Low | Medium | Comprehensive testing |
| Python/skill integration fails | Medium | High | Graceful fallback |
| QA mechanism changes | Low | High | Version lock QA patterns |

### 19.2 Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | Medium | Strict PRD adherence |
| QA pass rate not achieved | Medium | High | Iterative improvement |
| Test coverage gaps | Medium | High | TDD approach |
| Documentation lag | High | Low | Doc-as-code |

---

## 20. Implementation Phases

### Phase 1: Foundation (Week 1)

**Deliverables:**
- `bc_engine/` Python package structure
- `base_validator.py` - Validator interface
- `template_engine.py` - Template rendering
- `progress_tracker.py` - Progress tracking
- `bc_setup.json` schema and loader

**Exit Criteria:**
- Base validator interface defined
- Template engine renders correctly
- Progress tracker works

---

### Phase 2: Python Validators (Week 2)

**Deliverables:**
- `validate_content.py` - BiDi rules for content
- `validate_code.py` - Code block rules
- `validate_tikz.py` - TikZ rules (EXISTS)
- `validate_tables.py` - Table rules
- `validate_citations.py` - Citation rules
- Unit tests for all validators

**Exit Criteria:**
- Validators match QA detection patterns
- 90%+ test coverage
- Pre-validation catches 80%+ of issues

---

### Phase 3: Skill Updates (Week 3)

**Deliverables:**
- bc-Hrari-content-style with QA rules
- bc-code with QA rules
- bc-drawing with QA rules (PARTIAL)
- bc-math with QA rules (PARTIAL)
- bc-academic-source with QA rules
- bc-Hrari-content-style relocated

**Exit Criteria:**
- All BC skills have QA Compliance Rules section
- All skills have Pre-Validation Checklist
- All skills have `qa_rules_embedded: true`

---

### Phase 4: insert_bc_skill (Week 4)

**Deliverables:**
- `insert_bc_skill/skill.md` - Full skill definition
- Templates for skill, validator, test
- Create mode implementation
- Embed-QA mode implementation
- Add-Validator mode implementation

**Exit Criteria:**
- Create mode generates valid skill
- Embed-QA mode updates skill correctly
- Generated validators work

---

### Phase 5: Validation & Polish (Week 5)

**Deliverables:**
- Full test suite execution
- QA compliance validation (95%+ target)
- BC-CLAUDE.md documentation
- Performance benchmarks

**Exit Criteria:**
- 95%+ QA pass rate achieved
- All KPIs met
- Documentation complete

---

## 21. Acceptance Criteria

### 21.1 Overall System Acceptance

- [ ] All functional requirements (FR-*) implemented
- [ ] All non-functional requirements (NFR-*) met
- [ ] QA pass rate 95%+ on first run
- [ ] Token usage reduced by 30%+
- [ ] Test coverage at 90%+
- [ ] Documentation complete

### 21.2 Component Acceptance

#### bc_engine Package
- [ ] Controller coordinates skill execution
- [ ] Template engine renders all patterns
- [ ] Progress tracker reports status
- [ ] All validators pass tests

#### BC Skills
- [ ] All skills have QA rules embedded
- [ ] All skills have pre-validation checklists
- [ ] bc-Hrari-content-style relocated
- [ ] bc-drawing complete with templates

#### insert_bc_skill
- [ ] Create mode generates valid skill structure
- [ ] Embed-QA mode updates skills correctly
- [ ] Add-Validator mode creates working validators
- [ ] Generated tests pass

---

## 22. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| BC | Book Creator - content generation skills |
| QA | Quality Assurance - content validation skills |
| BiDi | Bidirectional text (Hebrew RTL + English LTR) |
| CLS | LaTeX document class file (.cls) |
| Pre-validation | Checking content before LaTeX compilation |
| Phase | Workflow stage (2.1, 2.2, 2.3, 2.4) |
| Signal | Completion indicator between phases |
| Persona | Historical figure the agent emulates |

### Appendix B: QA Rules Reference

| QA Rule | Detection Pattern | BC Skill | Fix Pattern |
|---------|-------------------|----------|-------------|
| BiDi Rule 6 | Number in Hebrew | All content | `\en{N}` or `\num{N}` |
| BiDi Rule 7 | English in Hebrew | All content | `\en{word}` |
| BiDi Rule 10 | Acronym in Hebrew | All content | `\en{ABC}` |
| Code background | pythonbox in RTL | bc-code | Wrap in english |
| Hebrew comment | Hebrew in code | bc-code | English only |
| TikZ no wrapper | tikz without english | bc-drawing | Wrap in english |
| Hebrew in TikZ | Hebrew chars in tikz | bc-drawing | English only |
| Table column order | Wrong order | bc-academic-source | Reverse columns |

### Appendix C: Template Reference

| Template Name | Purpose | Variables |
|---------------|---------|-----------|
| section | Hebrew section | title, content |
| figure_ref | Figure reference | label |
| table_ref | Table reference | label |
| en_wrap | English wrapper | content |
| num_wrap | Number wrapper | content |
| ilm_wrap | Math wrapper | content |
| pythonbox | Code block | title, code |
| tikz | TikZ diagram | content |
| rtl_table | RTL table | columns, rows |

### Appendix D: References

- [BC Architecture Research Report](./BC-CLAUDE-MECHANISM-ARCHITECTURE-REPORT.md)
- [QA PRD](./PRD-QA-SKILL-PYTHON-BASE.md)
- [ACADEMIC_BOOK_WORKFLOW.md](.claude/skills/ACADEMIC_BOOK_WORKFLOW.md)
- [Claude CLI Documentation](https://docs.anthropic.com/claude-code)

### Appendix E: Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-22 | Claude Code | Initial PRD |

---

*End of PRD*
